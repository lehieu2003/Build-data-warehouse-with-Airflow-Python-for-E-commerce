# ETL Runner bang GitHub Actions

Tai lieu nay mo ta workflow `ETL Runner` dung de chay toan bo pipeline ETL cua project tren GitHub Actions ma khong can host Airflow 24/7.

Doc nay danh cho:

- nguoi moi hoc CI/CD
- nguoi muon chay ETL theo lich mien phi
- nguoi muon debug khi workflow pass/fail

Sau khi doc xong, ban co the:

- tu chay workflow bang tay
- hieu workflow dang lam gi
- doc log de biet loi nam o dau

## 1. Muc dich cua workflow nay

Thay vi deploy Airflow len mot server online lien tuc, workflow nay dung GitHub Actions de tao mot moi truong chay tam thoi moi lan can ETL.

Moi lan workflow chay, no se:

1. build Docker image cua project
2. khoi dong MySQL, PostgreSQL va Airflow bang `docker compose`
3. nap dataset nguon vao MySQL
4. tao schema `staging`, `warehouse`, `mart` trong PostgreSQL
5. tao Airflow connections cho `mysql` va `postgres`
6. trigger DAG `e_commerce_dw_etl`
7. cho DAG chay xong
8. kiem tra bang fact va mart co du lieu
9. in log neu fail va tat toan bo container

Day la mot kieu automation rat hop ly cho project hoc Data Engineering:

- khong ton phi host
- van co lich chay
- van co log, verify va fail/success ro rang

## 2. Workflow chay khi nao

Workflow co 2 cach chay:

- `workflow_dispatch`: ban bam tay trong tab `Actions`
- `schedule`: tu dong chay theo cron

Cron hien tai la:

```yaml
0 1 * * 1
```

Nghia la workflow chay vao `01:00 UTC` moi thu Hai.

Neu doi lich, sua phan `schedule` trong workflow.

## 3. Cach chay bang tay

1. Mo repo tren GitHub.
2. Vao tab `Actions`.
3. Chon workflow `ETL Runner`.
4. Bam `Run workflow`.
5. Cho workflow chay xong.

Neu pass, ban se thay dau xanh cho job `run-etl-pipeline`.

## 4. Workflow dang lam gi

### `Create GitHub Actions .env file`

Step nay tao file `.env` tam tren GitHub runner de stack Docker co du bien moi truong can thiet.

No cung set:

```env
AIRFLOW__CORE__UNIT_TEST_MODE=True
```

Muc dich la tat schedule tu dong cua DAG trong moi truong GitHub Actions, de chi con manual run do workflow trigger. Cach nay tranh sinh them scheduled run khong mong muon.

### `Prepare mounted directories for Airflow`

Tao cac thu muc mount nhu `logs`, `config`, `plugins` va mo permission de Airflow trong container ghi duoc file.

Neu thieu buoc nay, Airflow rat de loi permission.

### `Build Docker images`

Build image dung chinh source code hien tai trong repo.

Y nghia:

- code vua push len la code duoc test/chay
- khong phu thuoc vao image cu

### `Start services`

Khoi dong toan bo stack bang `docker compose up -d`.

### `Wait for Airflow webserver and scheduler`

Step nay khong chi doi webserver mo cong, ma con check API `/health` de chac chan:

- `metadatabase` healthy
- `scheduler` healthy

Neu 1 trong 2 chua healthy, workflow tiep tuc cho.

### `Prepare source and warehouse databases`

Step nay chuan bi du lieu nguon va kho du lieu:

- bat `local_infile` cho MySQL
- import schema + data vao database `olist`
- tao schema `staging`, `warehouse`, `mart` trong PostgreSQL

### `Configure Airflow connections`

Step nay tao 2 connection ma DAG dang dung:

- `mysql`
- `postgres`

Neu khong co 2 connection nay, tasks trong DAG se fail ngay tu dau.

### `Unpause DAG`

Mo DAG `e_commerce_dw_etl` de Airflow cho phep trigger run.

### `Trigger DAG run`

Workflow goi Airflow REST API de tao mot manual run:

- `dag_id`: `e_commerce_dw_etl`
- `dag_run_id`: `github-actions-${GITHUB_RUN_ID}`

No khong can UI Airflow va khong can ban bam tay trong container.

### `Wait for DAG success`

Step nay poll Airflow API nhieu lan de doc state cua DAG run.

No se dung khi gap mot trong 3 truong hop:

- `success`
- `failed`
- timeout

Neu `failed`, workflow in them danh sach task instances va log scheduler/webserver de de debug.

### `Dump task logs when DAG fails`

Step nay chi chay khi workflow fail.

No se:

- lay JSON task instances cua DAG run
- in state cua tung task
- liet ke file log Airflow
- in log cua 3 task mart neu co:
  - `publish_mart_sales_daily`
  - `publish_mart_product_performance`
  - `publish_mart_city_revenue`

Day la step quan trong nhat khi can debug loi ETL.

### `Verify mart tables contain data`

Neu DAG success, workflow chay them SQL verify:

- `warehouse.fact_orders`
- `mart.mart_sales_daily`
- `mart.mart_product_performance`
- `mart.mart_city_revenue`

Muc tieu la tranh truong hop DAG success nhung bang ket qua rong.

### `Shut down services`

Du workflow pass hay fail, stack Docker deu duoc tat va xoa volume tam.

## 5. Cach doc ket qua

### Khi workflow pass

Ban co the ket luan:

- Airflow khoi dong duoc tren GitHub Actions
- DAG `e_commerce_dw_etl` chay xong
- bang fact va mart da co du lieu

Day la muc pass co gia tri, khong chi la "container da start".

### Khi workflow fail

Doc theo thu tu nay:

1. `Wait for DAG success`
2. `Dump task logs when DAG fails`
3. `Dump logs on failure`

Neu DAG fail o task nao, step dump log se cho biet task do va log lien quan.

## 6. Cach debug nhanh

### Truong hop `queued` lau

Neu `Current DAG state: queued` dung rat lau, thuong la do:

- scheduler chua healthy
- DAG bi pause
- co van de voi trigger/manual run

Trong workflow hien tai, cac van de nay da duoc giam rat nhieu nhờ:

- health check scheduler
- step `Unpause DAG`
- `AIRFLOW__CORE__UNIT_TEST_MODE=True`

### Truong hop chi fail o `publish_marts.*`

Neu extract, transform, load deu success nhung 3 task mart fail, thi loi thuong nam o:

- SQL publish mart
- ep kieu du lieu trong `fact_orders`
- du lieu khong hop voi aggregate/join

Luc nay hay doc phan:

```text
===== Failed publish_marts task logs =====
```

Do la phan log co gia tri nhat.

### Truong hop verify bang mart fail

Neu DAG success nhung step verify fail, thi can check:

- bang mart co rong khong
- logic SQL co tao du lieu dung khong
- co can bo sung data quality checks khong

## 7. Khi nao nen dung cach nay

Nen dung khi:

- ban muon hoc CI/CD voi project Airflow
- ban muon co lich chay tu dong mien phi
- ban khong can Airflow UI online 24/7

Khong phu hop neu:

- ban can mot Airflow server online lien tuc
- ban can trigger, monitor va rerun thuong xuyen qua UI
- ban can workload lon va chay rat nhieu lan moi ngay

## 8. Gioi han can biet

- moi lan chay deu build va start lai stack
- runtime cham hon server chay san
- phu thuoc vao GitHub Actions minutes, nhat la neu repo private
- day la automation runner, khong phai mot he thong orchestrator online 24/7

Nhung voi project hien tai, day la lua chon free va thuc dung nhat.

## 9. Khuyen nghi su dung cho repo nay

Huong dung tot nhat hien tai la:

- hoc va debug DAG local bang Docker + Airflow UI
- dung `ETL Runner` de chay ETL tren cloud theo lich
- dung workflow `CI` de bat loi syntax, import va Docker config som

Neu muon nang cap tiep, buoc hop ly tiep theo la:

- them data quality checks ro hon
- them workflow rieng cho test ETL
- neu can host that, chuyen sang VPS hoac cloud co du RAM hon
