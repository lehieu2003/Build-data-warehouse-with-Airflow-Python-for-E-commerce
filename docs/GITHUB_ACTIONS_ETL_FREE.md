# Chay ETL mien phi bang GitHub Actions

Tai lieu nay la huong thay the cho viec deploy Airflow len free hosting.

Muc tieu:

- khong can VPS
- khong can Render
- van tu dong hoa pipeline
- van hoc duoc CI/CD va automation

## 1. Y tuong chinh

Thay vi host Airflow web UI 24/7, workflow GitHub Actions se:

1. build image va dung `docker compose`
2. khoi dong Airflow + MySQL + PostgreSQL tam thoi tren runner
3. nap dataset vao MySQL
4. tao schema warehouse
5. tao Airflow connections
6. trigger DAG qua Airflow REST API
7. cho DAG chay xong
8. verify bang fact va mart co du lieu
9. tat tat ca container

Day la automation mien phi va phu hop hon Airflow tren free hosting.

## 2. File workflow

Workflow da duoc them tai:

- [etl-runner.yml](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/.github/workflows/etl-runner.yml)

## 3. Workflow nay chay khi nao

Workflow dang co 2 cach chay:

- `workflow_dispatch`: ban bam tay tren GitHub
- `schedule`: chay tu dong vao `01:00 UTC` moi thu Hai

Cron hien tai:

```yaml
0 1 * * 1
```

Neu muon doi lich, sua phan `schedule` trong workflow.

## 4. Cach chay bang tay

1. Vao repo tren GitHub
2. Mo tab `Actions`
3. Chon workflow `ETL Runner`
4. Bam `Run workflow`

## 5. Cach doc workflow

### `Create GitHub Actions .env file`

Tao file `.env` tam tren GitHub runner.

### `Prepare mounted directories for Airflow`

Tranh loi permission khi Airflow ghi vao volume local.

### `Build Docker images` va `Start services`

Dung lai chinh stack local cua project.

### `Wait for Airflow webserver`

Cho webserver san sang truoc khi goi API.

### `Prepare source and warehouse databases`

- bat `local_infile`
- tao bang MySQL
- load CSV
- tao schema `staging`, `warehouse`, `mart`

### `Configure Airflow connections`

Them 2 connection:

- `mysql`
- `postgres`

### `Trigger DAG run`

Khong can bam UI.

Workflow goi REST API:

- `POST /api/v1/dags/e_commerce_dw_etl/dagRuns`

### `Wait for DAG success`

Workflow poll Airflow API cho toi khi:

- `success`
- `failed`
- hoac timeout

### `Verify mart tables contain data`

Kiem tra ket qua that bang SQL trong PostgreSQL warehouse.

## 6. Tai sao day duoc xem la free CD/automation?

Vi moi lan workflow chay:

- source code moi duoc dua vao mot moi truong chay tam
- he thong tu build
- he thong tu khoi dong stack
- he thong tu chay pipeline
- he thong tu verify ket qua

No khong phai deploy web app 24/7, nhung van la tu dong hoa delivery/execution rat thuc te.

## 7. Gioi han cua cach nay

- khong co Airflow UI online 24/7
- moi lan chay deu build va start lai stack
- phu thuoc vao GitHub Actions minutes neu repo private

Nhung no co uu diem lon:

- free hon
- on dinh hon free hosting web
- khong bi loi RAM nhu Render free

## 8. Cach doc ket qua

Neu workflow pass:

- DAG da chay xong
- warehouse va mart da duoc tao
- SQL verify da pass

Neu workflow fail:

- doc step do
- doc `Dump logs on failure`
- doi chieu voi [Case study debug CD Render tu log](docs/CD_DEBUG_CASE_STUDY.md)

## 9. Khuyen nghi cho repo nay

Neu ban muon free:

- giu Airflow de hoc local
- dung GitHub Actions de chay pipeline tren cloud theo lich

Day la huong hop ly nhat cho project hien tai.
