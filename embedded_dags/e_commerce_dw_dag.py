from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import pandas as pd

from mysql_operator import MySQLOperators
from postgresql_operator import PostgresOperators


def extract_and_load_to_staging(**kwargs):
    source_operator = MySQLOperators("mysql")
    staging_operator = PostgresOperators("postgres")
    tables = [
        "product_category_name_translation",
        "geolocation",
        "sellers",
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
        "order_reviews",
    ]
    for table in tables:
        df = source_operator.get_data_to_pd(f"SELECT * FROM {table}")
        staging_operator.save_data_to_postgres(df, f"stg_{table}", schema="staging", if_exists="replace")


def transform_dim_customers():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_customers")
    df["customer_unique_id"] = df["customer_unique_id"].astype(str)
    df["customer_zip_code_prefix"] = df["customer_zip_code_prefix"].astype(str).str.zfill(5)
    df["customer_city"] = df["customer_city"].str.title()
    df["customer_state"] = df["customer_state"].str.upper()
    df["customer_key"] = df.index + 1
    df["effective_date"] = datetime.now().date()
    df["end_date"] = datetime.now().date() + timedelta(days=365 * 10)
    df["is_current"] = True
    warehouse_operator.save_data_to_postgres(df, "dim_customers", schema="warehouse", if_exists="replace")


def transform_dim_products():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df_products = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_products")
    df_categories = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_product_category_name_translation")
    df = pd.merge(df_products, df_categories, on="product_category_name", how="left")
    df["product_category_name_english"] = df["product_category_name_english"].fillna("Unknown")
    for col in ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        df[col] = df[col].fillna(0)
    df["product_key"] = df.index + 1
    df["last_updated"] = pd.Timestamp.now().date()
    warehouse_operator.save_data_to_postgres(df, "dim_products", schema="warehouse", if_exists="replace")


def transform_dim_sellers():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_sellers")
    df["seller_zip_code_prefix"] = df["seller_zip_code_prefix"].astype(str).str.zfill(5)
    df["seller_city"] = df["seller_city"].str.title()
    df["seller_state"] = df["seller_state"].str.upper()
    df["seller_key"] = df.index + 1
    df["last_updated"] = pd.Timestamp.now().date()
    warehouse_operator.save_data_to_postgres(df, "dim_sellers", schema="warehouse", if_exists="replace")


def transform_dim_geolocation():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_geolocation")
    df["geolocation_zip_code_prefix"] = df["geolocation_zip_code_prefix"].astype(str).str.zfill(5)
    df["geolocation_city"] = df["geolocation_city"].str.title()
    df["geolocation_state"] = df["geolocation_state"].str.upper()
    df = df.drop_duplicates(subset=["geolocation_zip_code_prefix"])
    df["geolocation_key"] = df.index + 1
    warehouse_operator.save_data_to_postgres(df, "dim_geolocation", schema="warehouse", if_exists="replace")


def transform_dim_dates():
    warehouse_operator = PostgresOperators("postgres")
    date_range = pd.date_range(start=pd.Timestamp("2016-01-01"), end=pd.Timestamp("2025-12-31"))
    df = pd.DataFrame({
        "date_key": date_range,
        "day": date_range.day,
        "month": date_range.month,
        "year": date_range.year,
        "quarter": date_range.quarter,
        "day_of_week": date_range.dayofweek,
        "day_name": date_range.strftime("%A"),
        "month_name": date_range.strftime("%B"),
        "is_weekend": date_range.dayofweek.isin([5, 6]),
    })
    warehouse_operator.save_data_to_postgres(df, "dim_dates", schema="warehouse", if_exists="replace")


def transform_dim_payments():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_payments")
    df["payment_type"] = df["payment_type"].str.lower()
    df["payment_installments"] = df["payment_installments"].fillna(1).astype(int)
    df["payment_key"] = df.index + 1
    df = df.drop_duplicates(subset=["payment_type", "payment_installments"])
    warehouse_operator.save_data_to_postgres(df, "dim_payments", schema="warehouse", if_exists="replace")


def transform_fact_orders():
    staging_operator = PostgresOperators("postgres")
    warehouse_operator = PostgresOperators("postgres")
    df_orders = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_orders")
    df_items = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_order_items")
    df_payments = staging_operator.get_data_to_pd("SELECT * FROM staging.stg_payments")
    df_customers = staging_operator.get_data_to_pd("SELECT customer_id, customer_zip_code_prefix FROM staging.stg_customers")
    df = pd.merge(df_orders, df_items, on="order_id", how="left")
    df = pd.merge(df, df_payments, on="order_id", how="left")
    df = pd.merge(df, df_customers, on="customer_id", how="left")
    for col in ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]:
        df[col] = pd.to_datetime(df[col])
    df["order_status"] = df["order_status"].str.lower()
    df["total_amount"] = df["price"] + df["freight_value"]
    df["delivery_time"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400
    df["estimated_delivery_time"] = (df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400
    df["customer_key"] = df["customer_id"]
    df["product_key"] = df["product_id"]
    df["seller_key"] = df["seller_id"]
    df["geolocation_key"] = df["customer_zip_code_prefix"] if "customer_zip_code_prefix" in df.columns else "unknown"
    df["payment_key"] = df["payment_type"].astype("category").cat.codes + 1
    df["order_date_key"] = df["order_purchase_timestamp"].dt.date
    fact_columns = ["order_id", "customer_key", "product_key", "seller_key", "geolocation_key", "payment_key", "order_date_key", "order_status", "price", "freight_value", "total_amount", "payment_value", "delivery_time", "estimated_delivery_time"]
    warehouse_operator.save_data_to_postgres(df[fact_columns], "fact_orders", schema="warehouse", if_exists="replace")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 10, 26),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "e_commerce_dw_etl",
    default_args=default_args,
    description="ETL process for E-commerce Data Warehouse",
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:
    with TaskGroup("extract") as extract_group:
        extract_task = PythonOperator(task_id="extract_and_load_to_staging", python_callable=extract_and_load_to_staging)

    with TaskGroup("transform") as transform_group:
        task_dim_customers = PythonOperator(task_id="transform_dim_customers", python_callable=transform_dim_customers)
        task_dim_products = PythonOperator(task_id="transform_dim_products", python_callable=transform_dim_products)
        task_dim_sellers = PythonOperator(task_id="transform_dim_sellers", python_callable=transform_dim_sellers)
        task_dim_geolocation = PythonOperator(task_id="transform_dim_geolocation", python_callable=transform_dim_geolocation)
        task_dim_dates = PythonOperator(task_id="transform_dim_dates", python_callable=transform_dim_dates)
        task_dim_payments = PythonOperator(task_id="transform_dim_payments", python_callable=transform_dim_payments)

    with TaskGroup("load") as load_group:
        task_fact_orders = PythonOperator(task_id="transform_fact_orders", python_callable=transform_fact_orders)

    extract_group >> transform_group >> load_group
