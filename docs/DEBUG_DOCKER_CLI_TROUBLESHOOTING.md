# Debug Docker CLI cho project Airflow Data Warehouse

Tai lieu nay ghi lai qua trinh debug thuc te khi chay project bang Docker CLI, gom:

- Loi da gap.
- Nguyen nhan goc.
- Cach xu ly.
- Giai thich tung lenh da dung trong qua trinh debug.

Muc tieu: lan sau gap lai ban co the tu khoanh vung va sua loi nhanh.

## 1) Trieu chung ban dau

Sau khi chay:

```powershell
docker compose run --rm airflow-cli dags trigger e_commerce_dw_etl
```

Airflow bao:

- `DagNotFound: Dag id e_commerce_dw_etl not found in DagModel`
- `docker compose run --rm airflow-cli dags list` tra ve `No data found`

## 2) Nguyen nhan goc

### Nguyen nhan 1: Airflow khong nhin thay file DAG

Kiem tra trong container scheduler:

```powershell
docker compose exec airflow-scheduler ls -la /opt/airflow/dags
```

ket qua thu muc `/opt/airflow/dags` rong.

Khi khong co file DAG, Airflow metadata khong co ban ghi DAG => trigger bi `DagNotFound`.

### Nguyen nhan 2: service `git-sync` ghi de vao thu muc `dags`

Compose co service `git-sync` mount truc tiep vao `./dags`. Trong qua trinh dong bo repo/thu muc dich, no co the lam mat file local trong `dags` (hoac de trang thu muc), dan den Airflow khong con file de parse.

### Nguyen nhan 3: bind mount `./dags:/opt/airflow/dags` khong dong bo on dinh tren may hien tai

Sau khi thu ghi file vao host, container van thay thu muc rong. Nghia la mount giua host va container trong case nay khong dang tin cay cho `dags`.

## 3) Cach fix da ap dung

### Buoc A: bo `git-sync` khoi `docker-compose.yaml`

Ly do:

- Loai bo nguon can thiep vao `./dags`.
- Tranh tiep tuc bi mat DAG.

### Buoc B: dua DAG vao image thay vi phu thuoc mount

Thay doi:

- Tao thu muc `embedded_dags` trong source.
- Copy DAG vao image qua Dockerfile:

```dockerfile
COPY embedded_dags /opt/airflow/dags
```

Ly do:

- Airflow luon co DAG ben trong image.
- Khong phu thuoc vao tinh on dinh cua bind mount `dags` tren host.

### Buoc C: bo mount `dags` trong phan `x-airflow-common`

Truoc do:

```yaml
- ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
```

Sau khi bo dong nay, Airflow doc DAG tu image (duoc `COPY` san).

### Buoc D: khoi dong lai stack theo chu trinh sach

```powershell
docker compose down --remove-orphans
docker compose build airflow-scheduler airflow-webserver airflow-init airflow-cli
docker compose up -d --remove-orphans
```

Ly do:

- `down --remove-orphans` don container cu (dac biet orphan `git-sync`).
- `build` dam bao image moi co DAG da embed.
- `up -d` khoi tao lai service tu image moi.

## 4) Lenh debug da dung va y nghia

### 4.1 Kiem tra Airflow co parse duoc DAG khong

```powershell
docker compose run --rm airflow-cli dags list
```

Y nghia:

- Liet ke DAG da dang ky trong Airflow metadata.
- `No data found` => Airflow chua co DAG nao.

```powershell
docker compose run --rm airflow-cli dags list-import-errors
```

Y nghia:

- Liet ke loi import/parse DAG.
- Neu rong ma `dags list` van rong, thuong la do khong co file DAG de parse.

### 4.2 Kiem tra thu muc DAG trong container

```powershell
docker compose exec airflow-scheduler ls -la /opt/airflow/dags
```

Y nghia:

- Xac minh DAG file co that su ton tai ben trong runtime container hay khong.

### 4.3 Kiem tra log scheduler

```powershell
docker compose logs airflow-scheduler --tail=300
```

Y nghia:

- Tim loi parse DAG, loi import module, loi ket noi metadata DB.

### 4.4 Kiem tra compose config da render cuoi cung

```powershell
docker compose config
docker compose config --quiet
```

Y nghia:

- Xem file compose sau khi da no bien env.
- `--quiet` tra ve exit code de xac nhan config hop le.

### 4.5 Kiem tra mount that su cua container

```powershell
docker inspect <container_name> --format "{{json .Mounts}}"
```

Y nghia:

- Xac minh container dang mount thu muc nao tu host.
- Huu ich khi nghi ngo bind mount sai path hoac khong dong bo.

### 4.6 Khoi dong lai service Airflow

```powershell
docker compose restart airflow-scheduler airflow-webserver
```

Y nghia:

- Buoc nhanh de scheduler parse lai DAG sau khi sua file.

### 4.7 Don orphan container

```powershell
docker compose down --remove-orphans
docker compose up -d --remove-orphans
```

Y nghia:

- Xoa cac container khong con khai bao trong compose (vi du `git-sync` cu).
- Tranh service cu tiep tuc anh huong.

### 4.8 Kiem tra trang thai container thuc te

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Y nghia:

- Co cai nhin truc tiep tat ca container dang chay (khong phu thuoc compose context).

### 4.9 Trigger DAG bang CLI sau khi fix

```powershell
docker exec <airflow-scheduler-container> airflow dags unpause e_commerce_dw_etl
docker exec <airflow-scheduler-container> airflow dags trigger e_commerce_dw_etl
docker exec <airflow-scheduler-container> airflow dags list-runs -d e_commerce_dw_etl --no-backfill
```

Y nghia:

- `unpause`: bo trang thai tam dung.
- `trigger`: tao dag run moi.
- `list-runs`: xac nhan run da vao `queued/running/success`.

## 5) Kiem tra sau fix

Sau khi DAG chay xong can xac nhan:

```powershell
docker exec de_psql psql -U admin -d postgres -c "\dt staging.*"
docker exec de_psql psql -U admin -d postgres -c "\dt warehouse.*"
docker exec de_psql psql -U admin -d postgres -c "SELECT COUNT(*) AS fact_rows FROM warehouse.fact_orders;"
```

Ket qua mong doi:

- Staging co 9 bang `stg_*`.
- Warehouse co 7 bang (`dim_*`, `fact_orders`).
- `fact_rows > 0`.

Sau khi xac nhan bang CLI, co the mo them pgAdmin de kiem tra du lieu bang GUI:

```powershell
docker compose up -d pgadmin
```

Truy cap `http://localhost:5050` voi tai khoan `admin@local.com/admin`, sau do dang ky server `de_psql:5432`.

## 6) Bai hoc rut ra

1. `DagNotFound` khong phai luc nao cung do code DAG sai; co the do Airflow khong thay file DAG.
2. Luon check `/opt/airflow/dags` trong container truoc khi sua logic DAG.
3. Khi co `git-sync` cung thu muc voi DAG local, can than nguy co ghi de.
4. Neu bind mount khong on dinh tren may local, embed DAG vao image la cach chay on dinh de hoc/demo.
5. Khi sua compose, nen dung `--remove-orphans` de don service cu.

## 7) Lenh chuan de chay lai toan bo sau khi da fix

```powershell
docker compose down --remove-orphans
docker compose build
docker compose up -d --remove-orphans
docker exec <airflow-scheduler-container> airflow dags list
docker exec <airflow-scheduler-container> airflow dags trigger e_commerce_dw_etl
```

Neu can tim ten scheduler container:

```powershell
docker ps --format "{{.Names}}" | Select-String "airflow-scheduler"
```
