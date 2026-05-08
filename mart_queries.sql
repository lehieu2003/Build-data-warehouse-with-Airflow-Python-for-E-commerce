-- Mart-only queries for BI and quick validation

-- 1) Doanh thu theo ngay
SELECT
    order_date,
    order_count,
    total_revenue,
    average_order_value
FROM mart.mart_sales_daily
ORDER BY order_date;

-- 2) Top san pham theo doanh thu
SELECT
    product_id,
    product_category_name_english,
    total_quantity,
    total_revenue
FROM mart.mart_product_performance
ORDER BY total_revenue DESC
LIMIT 20;

-- 3) Doanh thu theo thanh pho/bang
SELECT
    geolocation_city,
    geolocation_state,
    order_count,
    total_revenue
FROM mart.mart_city_revenue
ORDER BY total_revenue DESC
LIMIT 20;

-- 4) Tong doanh thu toan bo mart sales daily
SELECT
    SUM(total_revenue) AS total_revenue_all_days
FROM mart.mart_sales_daily;

-- 5) Tong so don toan bo mart sales daily
SELECT
    SUM(order_count) AS total_orders_all_days
FROM mart.mart_sales_daily;
