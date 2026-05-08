# Data Engineer Workflow (dua tren project nay)

Tai lieu nay mo ta workflow lam viec cua Data Engineer dua tren project `Build-data-warehouse-with-Airflow-Python-for-E-commerce`.

Muc tieu: giup ban nhin duoc day du vong doi cong viec, tu du lieu raw den dashboard.

## 1. Xac dinh bai toan va output

Dau vao:

- Du lieu e-commerce Olist (CSV).

Dau ra:

- Data warehouse trong PostgreSQL (`staging`, `warehouse`, `mart`).
- Dashboard phan tich tren Power BI.

Cau hoi business tieu bieu:

- Doanh thu theo thang.
- So luong don theo trang thai.
- San pham ban chay theo danh muc.
- Doanh thu theo khu vuc.

## 2. Setup moi truong (local data platform)

Data Engineer khoi tao stack bang Docker Compose:

- Airflow webserver + scheduler (orchestration).
- MySQL (source system mo phong).
- PostgreSQL warehouse (`de_psql`).
- pgAdmin (GUI quan sat DB).

Lenh chinh:

```powershell
docker compose build
docker compose up -d --remove-orphans
```

## 3. Ingestion layer: nap raw data vao source

CSV duoc nap vao MySQL:

1. Bat `local_infile`.
2. Tao bang source (`olist.sql`).
3. Load du lieu (`load_data.sql`).

Vai tro Data Engineer:

- Bao dam source co du bang va du lieu truoc khi chay pipeline.

## 4. Orchestration layer: dieu phoi bang Airflow

DAG chinh: `e_commerce_dw_etl`

Task flow:

```text
extract -> transform -> load -> publish_marts
```

- `extract`: doc MySQL va ghi sang `staging.stg_*`.
- `transform`: tao dimension (`dim_*`) trong schema `warehouse`.
- `load`: tao fact table `warehouse.fact_orders`.
- `publish_marts`: tao bang tong hop trong schema `mart` de BI dung truc tiep.

Vai tro Data Engineer:

- Cai dat schedule/catchup/retry hop ly.
- Theo doi DAG run va logs khi fail.

## 5. Data modeling layer: thiet ke warehouse

Mo hinh muc tieu:

- Star schema don gian.
- `fact_orders` o trung tam.
- Cac dimension: `dim_customers`, `dim_products`, `dim_sellers`, `dim_dates`, `dim_payments`, `dim_geolocation`.
- Data marts phuc vu BI: `mart_sales_daily`, `mart_product_performance`, `mart_city_revenue`.

Vai tro Data Engineer:

- Chuan hoa key join.
- Lam sach/chuan hoa field (city/state/zip/date/time).
- Tinh metric phu hop cho phan tich (`total_amount`, `delivery_time`...).

## 6. Data quality va validation

Sau moi lan DAG chay, Data Engineer can validate:

1. Co du bang trong `staging`.
2. Co du bang trong `warehouse`.
3. Co du bang trong `mart`.
4. Fact va mart co du lieu (`COUNT(*) > 0`).
5. Query business tra ket qua hop ly.

Lenh quick check:

```powershell
docker exec de_psql psql -U admin -d postgres -c "\dt staging.*"
docker exec de_psql psql -U admin -d postgres -c "\dt warehouse.*"
docker exec de_psql psql -U admin -d postgres -c "\dt mart.*"
docker exec de_psql psql -U admin -d postgres -c "SELECT COUNT(*) FROM warehouse.fact_orders;"
```

## 7. Data serving layer: ban giao cho BI

Kenh tieu thu:

- Power BI ket noi PostgreSQL (`localhost:5433`).
- Uu tien chon bang trong schema `mart`.
- Tao model relationship va refresh dashboard.

Vai tro Data Engineer:

- Cung cap schema on dinh cho BI.
- Dam bao pipeline refresh khong pha vo dashboard.

## 8. Monitoring va incident handling

Khi co loi, quy trinh debug:

1. `dags list` / `dags list-import-errors`.
2. Kiem tra `/opt/airflow/dags` trong scheduler.
3. Doc `airflow-scheduler` logs.
4. Kiem tra ket noi DB va schema.
5. Trigger lai sau khi fix.

Tai lieu chi tiet:

- `docs/DEBUG_DOCKER_CLI_TROUBLESHOOTING.md`

## 9. Van hanh hang ngay (daily routine)

Mot workflow thuc te cho Data Engineer:

1. Kiem tra service health (`docker ps`, Airflow UI health).
2. Kiem tra DAG run hom nay (`success/failed`).
3. Neu fail: doc log, sua loi, rerun task.
4. Kiem tra quality query nhanh tren warehouse.
5. Dong bo voi BI team neu co thay doi schema/logic.

## 10. Governance va version control

Trong project nay:

- Code pipeline + SQL + docs duoc quan ly bang Git.
- Tach tai lieu setup, troubleshooting, workflow de onboarding nhanh.

Khuyen nghi:

- Bo sung data quality checks tu dong.
- Bo sung convention dat ten bang/cot.
- Quan ly secrets an toan hon cho moi truong production.

## 11. Nang cap tiep theo (roadmap)

De workflow nay giong production hon, Data Engineer se nang cap:

1. Incremental load thay vi full replace.
2. Data tests (null/unique/referential checks).
3. Alerting khi DAG fail (email/slack).
4. CI/CD cho DAG + SQL + docs.
5. Tach moi truong dev/staging/prod.

---

Neu ban moi hoc Data Engineering, hay xem workflow nay nhu khung xuong:

- Ingest dung.
- Model dung.
- Validate dung.
- Orchestrate on dinh.
- Ban giao de phan tich.

Lam tot 5 diem nay la ban da di dung huong cua mot Data Engineer thuc chien.
