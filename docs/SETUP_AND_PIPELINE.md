# Huong dan setup, chay va hieu data pipeline E-commerce DW

Tai lieu nay viet cho nguoi moi hoc Data Engineering. Sau khi doc xong, ban co the dung Docker de chay project, nap du lieu Olist tu CSV vao MySQL, chay Airflow DAG de dua du lieu sang PostgreSQL data warehouse, va kiem tra bang fact/dimension phuc vu dashboard Power BI.

## 1. Project nay lam gi?

Project mo phong mot data pipeline cho bai toan e-commerce:

1. Du lieu nguon nam trong cac file CSV cua bo du lieu Olist.
2. CSV duoc nap vao MySQL, dong vai tro source database cua he thong ban hang.
3. Airflow doc du lieu tu MySQL.
4. Airflow load du lieu tho sang PostgreSQL schema `staging`.
5. Airflow transform du lieu staging thanh cac bang dimension va fact trong PostgreSQL schema `warehouse`.
6. Airflow publish data marts trong schema `mart` de BI su dung truc tiep.
7. Power BI doc mart/warehouse de ve dashboard doanh thu, don hang, san pham, khu vuc.

Theo ngon ngu Data Engineering, day la pipeline dang ELT:

- Extract: lay du lieu tu MySQL.
- Load: ghi du lieu tho vao PostgreSQL staging.
- Transform: bien doi du lieu trong Python/Pandas roi ghi vao warehouse.

## 2. Cac thanh phan chinh

Project chay bang Docker Compose va gom cac service quan trong:

- Airflow webserver: giao dien web de xem DAG, trigger DAG, xem log task.
- Airflow scheduler: thanh phan lap lich va dieu phoi task.
- Airflow metadata PostgreSQL: database rieng cua Airflow, chi luu metadata cua Airflow.
- MySQL: source database, luu cac bang raw cua Olist sau khi nap CSV.
- PostgreSQL warehouse: database dich, gom schema `staging`, `warehouse`, `mart`.
- Power BI file: dashboard mau doc tu warehouse.

Can phan biet hai PostgreSQL trong project:

- PostgreSQL cua Airflow metadata: Airflow dung noi bo de quan ly DAG run, task run, user.
- PostgreSQL warehouse: noi pipeline ghi du lieu staging va data warehouse.

## 3. Dieu kien can co truoc khi chay

Ban can cai:

- Docker Desktop.
- Docker Compose V2, thuong co san trong Docker Desktop.
- Git Bash, PowerShell, hoac terminal bat ky co the chay lenh Docker.
- Toi thieu 4 GB RAM free cho Docker; 8 GB se on dinh hon.
- Power BI Desktop neu muon mo file dashboard.

Kiem tra nhanh:

```powershell
docker --version
docker compose version
```

Neu lenh tren khong chay, hay mo Docker Desktop truoc, cho Docker khoi dong xong roi thu lai.

## 4. Cau truc du lieu nguon

Bo du lieu CSV gom cac file ve khach hang, don hang, san pham, seller, thanh toan, review va geolocation.

Sau khi nap vao MySQL, source database co cac bang:

- `product_category_name_translation`
- `geolocation`
- `sellers`
- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `order_reviews`

Day la lop source. Trong thuc te, no co the la database cua website/app e-commerce. Trong project hoc tap nay, ta nap CSV vao MySQL de gia lap source system.

## 5. Khoi dong Docker va Airflow

Tu thu muc goc cua project, chay:

```powershell
docker compose build
docker compose up -d
```

Kiem tra container:

```powershell
docker compose ps
```

Ban nen thay cac service nhu `airflow-webserver`, `airflow-scheduler`, `mysql`, `de_psql` dang chay.

Mo Airflow UI:

```text
http://localhost:8080
```

Tai khoan mac dinh:

```text
username: airflow
password: airflow
```

Neu lan dau build hoi lau, hay cho vai phut de Airflow migrate database va webserver khoi dong.

## 6. Tao source database trong MySQL

MySQL container da mount san folder dataset va SQL script. Truoc tien bat `local_infile` de MySQL cho phep nap CSV local:

```powershell
docker exec -it mysql mysql -uroot -padmin -e "SET GLOBAL local_infile=1;"
```

Tao cac bang source:

```powershell
docker exec -it mysql mysql --local-infile=1 -uadmin -padmin olist -e "source /tmp/load_dataset/olist.sql"
```

Nap CSV vao cac bang:

```powershell
docker exec -it mysql mysql --local-infile=1 -uadmin -padmin olist -e "source /tmp/load_dataset/load_data.sql"
```

Kiem tra nhanh so dong:

```powershell
docker exec -it mysql mysql -uadmin -padmin olist -e "SELECT COUNT(*) AS orders_count FROM orders; SELECT COUNT(*) AS customers_count FROM customers;"
```

Neu count tra ve so lon hon 0, MySQL source da san sang.

## 7. Tao schema staging va warehouse trong PostgreSQL

Pipeline ghi vao ba schema:

- `staging`: luu ban copy du lieu tho tu MySQL, ten bang co tien to `stg_`.
- `warehouse`: luu bang da transform, gom dimension va fact.
- `mart`: luu bang tong hop phuc vu BI/dashboard.

Tao schema:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "CREATE SCHEMA IF NOT EXISTS staging; CREATE SCHEMA IF NOT EXISTS warehouse; CREATE SCHEMA IF NOT EXISTS mart;"
```

Kiem tra schema:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "\dn"
```

## 8. Cau hinh Airflow Connections

DAG dung hai connection id:

- `mysql`: tro toi source MySQL.
- `postgres`: tro toi PostgreSQL warehouse.

Them connection bang CLI:

```powershell
docker compose run --rm airflow-cli connections add mysql --conn-type mysql --conn-host mysql --conn-login admin --conn-password admin --conn-schema olist --conn-port 3306
```

```powershell
docker compose run --rm airflow-cli connections add postgres --conn-type postgres --conn-host de_psql --conn-login admin --conn-password admin --conn-schema postgres --conn-port 5432
```

Kiem tra:

```powershell
docker compose run --rm airflow-cli connections get mysql
docker compose run --rm airflow-cli connections get postgres
```

Ban cung co the tao trong Airflow UI:

1. Vao Admin.
2. Chon Connections.
3. Tao connection id `mysql` voi host `mysql`, schema `olist`, login/password `admin/admin`, port `3306`.
4. Tao connection id `postgres` voi host `de_psql`, schema `postgres`, login/password `admin/admin`, port `5432`.

## 9. Chay DAG pipeline

Trong Airflow UI, tim DAG:

```text
e_commerce_dw_etl
```

DAG nay co lich daily, nhung project da cau hinh `catchup=False` de khi bat DAG no khong backfill hang tram ngay qua khu. Voi muc dich hoc tap, ban nen trigger thu cong:

1. Mo Airflow UI.
2. Tim DAG `e_commerce_dw_etl`.
3. Bam nut Trigger DAG.
4. Mo Graph hoac Grid view de theo doi task.
5. Neu task fail, bam vao task, mo Logs de xem loi.

Co the trigger bang CLI:

```powershell
docker compose run --rm airflow-cli dags trigger e_commerce_dw_etl
```

Xem danh sach DAG:

```powershell
docker compose run --rm airflow-cli dags list
```

## 10. Workflow cua DAG

DAG chinh co 4 nhom task:

```text
extract -> transform -> load -> publish_marts
```

### Extract group

Task `extract_and_load_to_staging` doc lan luot cac bang source trong MySQL:

- category translation
- geolocation
- sellers
- customers
- products
- orders
- order_items
- payments
- order_reviews

Moi bang duoc doc bang Pandas DataFrame, sau do ghi vao PostgreSQL schema `staging`.

Vi du:

- MySQL `orders` thanh PostgreSQL `staging.stg_orders`.
- MySQL `customers` thanh PostgreSQL `staging.stg_customers`.
- MySQL `payments` thanh PostgreSQL `staging.stg_payments`.

`if_exists='replace'` nghia la moi lan chay, bang staging cu bi thay bang du lieu moi. Cach nay de hoc va de lap lai pipeline, nhung chua phai chien luoc incremental load.

### Transform group

Nhom transform tao cac bang dimension:

- `warehouse.dim_customers`
- `warehouse.dim_products`
- `warehouse.dim_sellers`
- `warehouse.dim_geolocation`
- `warehouse.dim_dates`
- `warehouse.dim_payments`

Moi transform doc du lieu tu `staging`, lam sach hoac enrich, roi ghi sang `warehouse`.

Mot so bien doi dang chu y:

- Zip code duoc chuyen ve string va them so 0 dau neu thieu.
- City duoc chuan hoa dang title case.
- State duoc chuan hoa uppercase.
- Product category duoc join voi bang translation de co ten category tieng Anh.
- Cac gia tri thieu cua kich thuoc/can nang san pham duoc thay bang 0.
- Date dimension duoc tao tu 2016-01-01 den 2025-12-31.
- Payment dimension chuan hoa `payment_type` ve lowercase.

### Load group

Task `transform_fact_orders` tao bang fact:

```text
warehouse.fact_orders
```

Bang fact duoc tao bang cach merge:

- orders
- order_items
- payments
- customers

Sau do tinh cac metric:

- `total_amount = price + freight_value`
- `delivery_time`: so ngay tu luc mua den luc giao hang cho customer.
- `estimated_delivery_time`: so ngay tu luc mua den ngay giao hang du kien.

Bang fact chua cac khoa lien ket toi dimension va cac chi so phan tich doanh thu/don hang.

### Publish marts group

Nhom `publish_marts` tao 3 bang tong hop trong schema `mart`:

- `mart.mart_sales_daily`: doanh thu theo ngay, so don, AOV.
- `mart.mart_product_performance`: doanh thu va so luong theo san pham + category.
- `mart.mart_city_revenue`: doanh thu va so don theo city/state.

Tat ca mart dang theo che do full refresh: moi lan DAG chay se truncate va insert lai toan bo du lieu.

## 11. Mo hinh data warehouse

Warehouse trong project theo huong star schema don gian:

```text
dim_customers    dim_products    dim_sellers
       \              |              /
        \             |             /
         \            |            /
          fact_orders
         /     |       \
dim_dates  dim_payments  dim_geolocation
```

Bang fact nam o trung tam vi day la noi ghi nhan su kien ban hang: mot order item/payment sau khi merge. Dimension dung de cat lat va group by du lieu fact.

Vi du cau hoi business:

- Doanh thu theo thang: join `fact_orders` voi `dim_dates`.
- So don theo trang thai: group by `order_status` trong `fact_orders`.
- San pham ban chay theo category: join `fact_orders` voi `dim_products`.
- Doanh thu theo khu vuc: join `fact_orders` voi `dim_geolocation`.

## 12. Kiem tra ket qua trong PostgreSQL

Sau khi DAG thanh cong, kiem tra cac bang staging:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "\dt staging.*"
```

Kiem tra cac bang warehouse:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "\dt warehouse.*"
```

Kiem tra so dong bang fact:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "SELECT COUNT(*) FROM warehouse.fact_orders;"
```

Kiem tra cac bang mart:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "\dt mart.*"
docker exec -it de_psql psql -U admin -d postgres -c "SELECT COUNT(*) FROM mart.mart_sales_daily; SELECT COUNT(*) FROM mart.mart_product_performance; SELECT COUNT(*) FROM mart.mart_city_revenue;"
```

Chay thu query doanh thu theo thang:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "SELECT d.month, SUM(f.total_amount) AS total_revenue FROM warehouse.fact_orders f JOIN warehouse.dim_dates d ON f.order_date_key = d.date_key GROUP BY d.month ORDER BY d.month;"
```

Luu y: trong SQL tu Power BI hoac psql, nen them prefix schema `warehouse.` hoac `mart.` truoc ten bang neu search path chua duoc cau hinh.

## 13. Ket noi Power BI

File dashboard Power BI trong project dung du lieu tu warehouse. De ket noi lai neu can:

1. Mo Power BI Desktop.
2. Chon Get Data.
3. Chon PostgreSQL database.
4. Server: `localhost:5433`.
5. Database: `postgres`.
6. Username/password: `admin/admin`.
7. Chon cac bang trong schema `mart` (uu tien) hoac `warehouse` neu can chi tiet.
8. Refresh dashboard.

Port `5433` la port tren may host. Ben trong Docker network, Airflow dung host `de_psql` va port `5432`.

## 14. Setup pgAdmin bang Docker

Project da bo sung them service `pgadmin` trong `docker-compose.yaml` de ban xem bang/du lieu warehouse bang giao dien GUI.

Khoi dong rieng pgAdmin:

```powershell
docker compose up -d pgadmin
```

Mo giao dien:

```text
http://localhost:5050
```

Tai khoan dang nhap pgAdmin:

```text
email: admin@local.com
password: admin
```

Sau khi dang nhap, tao server de ket noi PostgreSQL warehouse:

1. Register -> Server.
2. Tab General:
- Name: `warehouse-local` (hoac ten bat ky).
3. Tab Connection:
- Host name/address: `de_psql`
- Port: `5432`
- Maintenance database: `postgres`
- Username: `admin`
- Password: `admin`

Luu y quan trong ve host:

- Neu dung pgAdmin container (service `pgadmin`): host la `de_psql`.
- Neu dung pgAdmin Desktop tren Windows: host la `localhost`, port `5433`.

## 15. Cac loi thuong gap

### Airflow task bao khong connect duoc MySQL

Kiem tra connection id `mysql` trong Airflow. Host phai la `mysql`, port `3306`, schema `olist`, login/password `admin/admin`.

Kiem tra container MySQL dang chay:

```powershell
docker compose ps mysql
```

### Airflow task bao khong connect duoc Postgres

Kiem tra connection id `postgres`. Host phai la `de_psql`, port `5432`, schema `postgres`, login/password `admin/admin`.

Kiem tra container warehouse:

```powershell
docker compose ps de_psql
```

### Loi schema staging hoac warehouse khong ton tai

Chay lai lenh tao schema:

```powershell
docker exec -it de_psql psql -U admin -d postgres -c "CREATE SCHEMA IF NOT EXISTS staging; CREATE SCHEMA IF NOT EXISTS warehouse; CREATE SCHEMA IF NOT EXISTS mart;"
```

### Loi MySQL khong nap duoc CSV

Bat lai `local_infile`:

```powershell
docker exec -it mysql mysql -uroot -padmin -e "SET GLOBAL local_infile=1;"
```

Sau do chay lai lenh load CSV.

### DAG khong hien trong Airflow UI

Cho scheduler them 30-60 giay, sau do refresh UI. Neu van khong co, xem loi parse DAG:

```powershell
docker compose logs airflow-scheduler
```

### DAG fail o buoc transform fact

Mo log cua task `transform_fact_orders`. Buoc nay merge nhieu bang nen thuong fail neu:

- Du lieu source chua load du.
- Bang staging chua duoc tao.
- Connection PostgreSQL sai.
- Cot ngay thang co gia tri khong parse duoc.

## 16. Cach doc project de hoc Data Engineering

Nen hoc theo thu tu nay:

1. Doc SQL tao bang source de hieu raw data trong MySQL.
2. Xem Airflow DAG de hieu orchestration: task nao chay truoc, task nao chay sau.
3. Xem extract task de hieu cach di tu source sang staging.
4. Xem tung transform dimension de hieu lam sach du lieu.
5. Xem transform fact de hieu cach merge bang va tinh metric.
6. Chay query phan tich trong warehouse.
7. Mo Power BI de thay ket qua cuoi cung.

Diem quan trong nhat: Airflow khong xu ly du lieu thay cho ban. Airflow chi dieu phoi workflow. Logic xu ly du lieu nam trong Python/Pandas va SQL.

## 17. Don dep moi truong

Dung container:

```powershell
docker compose down
```

Dung container va xoa volume database de chay lai tu dau:

```powershell
docker compose down -v
```

Can than voi `down -v`: lenh nay xoa du lieu MySQL, PostgreSQL warehouse va Airflow metadata. Sau do ban phai nap lai CSV, tao lai schema va tao lai Airflow connections.

## 18. Gioi han cua project hien tai

Project phu hop de hoc luong end-to-end, nhung chua phai production pipeline:

- Moi lan chay dang replace bang, chua co incremental load.
- Chua co data quality checks tu dong.
- Chua co retry cho pipeline chinh.
- Chua co test tu dong cho transform logic.
- Surrogate key trong mot so dimension/fact van con don gian, chua dam bao quan he khoa ngoai chuan nhu production warehouse.
- Credentials dang de local trong file cau hinh, chi nen dung cho moi truong hoc tap.

Huong nang cap sau khi hoc xong:

- Them data quality task sau extract va sau transform.
- Them incremental load theo `order_purchase_timestamp`.
- Dung dbt cho transform SQL-based.
- Dung Great Expectations hoac Soda de validate data.
- Chuan hoa key mapping giua fact va dimension.
- Tach dev/prod config va dung secret manager cho credentials.
