# CI/CD cho project nay

Tai lieu nay giai thich theo cach thuc te nhat cho nguoi chua tung lam CI/CD.

## 1. Hien trang cua repo

Hien tai project chua co CI/CD.

Project nay van co the setup CI/CD duoc vi da co cac thanh phan rat hop:

- `Dockerfile`
- `docker-compose.yaml`
- Airflow DAG ro rang
- code Python va plugin tach rieng

Voi repo nay, buoc di dung nhat cho nguoi moi la:

1. setup `CI` truoc
2. chay on dinh tren GitHub Actions
3. sau do moi setup `CD`

Khong nen nhay thang vao deploy tu dong neu ban chua co moi truong production ro rang.

## 2. CI va CD la gi?

### CI

CI = Continuous Integration.

Y nghia don gian:

- Moi lan ban `push` code hoac tao `pull request`
- GitHub tu dong chay mot loat kiem tra
- Neu co loi, ban biet ngay truoc khi merge

Voi project nay, CI nen kiem tra:

- file `docker-compose.yaml` co hop le khong
- image Airflow co build duoc khong
- Airflow co khoi tao metadata duoc khong
- DAG co parse duoc khong

### CD

CD = Continuous Deployment hoac Continuous Delivery.

Y nghia don gian:

- Sau khi CI pass
- He thong tu dong hoac ban tu bam nut deploy
- Code moi duoc dua len moi truong chay that

Voi project nay, CD phu thuoc ban muon deploy di dau:

- 1 may ao VPS dung Docker Compose
- 1 server Linux rieng
- Airflow managed service nhu Astronomer, MWAA, GCP Composer

## 3. Toi da them gi trong repo

Da them workflow:

- [ci.yml](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/.github/workflows/ci.yml)

Workflow nay se:

1. checkout code
2. validate `docker compose`
3. build image Airflow
4. start PostgreSQL metadata cua Airflow
5. chay `airflow-init`
6. chay `airflow dags list` de dam bao DAG load duoc

Day la muc CI co gia tri thuc te nhat cho repo hien tai.

## 4. Cach setup CI tren GitHub

Neu ban chua tung lam, di theo dung thu tu nay:

1. Tao repository tren GitHub.
2. Push code len GitHub.
3. Vao tab `Actions`.
4. GitHub se tu dong nhan file `.github/workflows/ci.yml`.
5. Moi lan ban `push` code, workflow se tu chay.

Lenh co ban:

```powershell
git init
git add .
git commit -m "Add starter CI workflow"
git branch -M main
git remote add origin <github-repo-url>
git push -u origin main
```

Sau do mo GitHub:

- vao repo
- chon `Actions`
- xem job `Airflow CI`

Neu workflow fail, bam vao tung step de doc log.

## 5. CI nay kiem tra duoc gi va chua kiem tra duoc gi

### Da kiem tra

- cau hinh Docker Compose hop le
- image build thanh cong
- Airflow init duoc
- DAG load duoc trong Airflow

### Chua kiem tra

- ket noi that toi MySQL va PostgreSQL warehouse
- chay full ETL end-to-end
- kiem tra data quality
- unit test cho tung ham transform

Ly do: full pipeline cua project nay phu thuoc nhieu service va dataset, nen voi nguoi moi lam CI/CD, bat dau bang muc parse/build la hop ly nhat.

## 6. CD nen lam kieu nao cho repo nay?

Neu ban moi hoc, toi khuyen dung 2 giai doan.

### Giai doan 1: CI + deploy thu cong

Sau khi CI pass:

- SSH vao server
- `git pull`
- `docker compose build`
- `docker compose up -d`

Day van la quy trinh rat binh thuong va de debug.

### Giai doan 2: CD ban tu dong

Khi ban da co 1 VPS hoac server Linux, ban co the them workflow deploy nhu sau:

1. CI pass tren branch `main`
2. GitHub Actions SSH vao server
3. chay:

```bash
cd /path/to/project
git pull
docker compose build
docker compose up -d
```

Luc do CD se la `manual trigger` hoac `auto deploy khi merge main`.

## 7. Neu muon lam CD bang GitHub Actions can chuan bi gi?

Toi thieu can:

- 1 server Linux/VPS
- Docker va Docker Compose da cai san tren server
- SSH key
- GitHub Secrets

Cac secret thuong dung:

- `HOST`
- `USERNAME`
- `SSH_PRIVATE_KEY`
- co the them `PORT`

Khong nen hard-code thong tin nay trong workflow.

## 8. Dieu quan trong voi project nay

Project hien tai dang dung credential local trong `.env`:

- MySQL `admin/admin`
- PostgreSQL `admin/admin`
- Airflow user local

Dieu nay on cho hoc tap, nhung khong duoc dung nhu vay khi deploy that.

Khi lam CD that, ban nen:

- tach `.env` cho server
- dung GitHub Secrets hoac secret manager
- khong commit password production vao repo

## 9. Lo trinh hoc de nhat cho ban

Neu ban chua tung lam CI/CD, di theo thu tu nay:

1. hieu `git push` va `pull request`
2. hieu GitHub Actions la gi
3. chay duoc CI workflow vua them
4. sua 1 file nho va xem CI chay lai
5. doc log khi workflow fail
6. sau do moi hoc deploy len VPS

Neu hoc theo cach nay, ban se de nam hon rat nhieu so voi viec hoc ca CI va CD cung luc.

## 10. De xuat nang cap tiep theo

Sau khi CI chay on, ban co the nang cap tiep:

- them `pytest` cho logic transform
- them check format/lint cho Python
- them end-to-end test bang sample dataset nho
- them workflow deploy len VPS qua SSH
- tach `dev` va `prod` config rieng

## 11. Viec ban nen lam tren GitHub ngay bay gio

Co mot vai viec quan trong khong the commit bang code ma ban phai bam tren giao dien GitHub.

### Bat branch protection cho `main`

Vao:

`Settings` -> `Branches` -> `Add branch protection rule`

Dung cac tuy chon co ban nay:

- Branch name pattern: `main`
- check `Require a pull request before merging`
- check `Require status checks to pass before merging`
- chon check `validate-airflow-project`

Y nghia:

- khong merge thang vao `main`
- moi thay doi di qua pull request
- CI phai xanh moi merge duoc

### Cach lam viec an toan hon

Thay vi sua tren `main`, dung quy trinh:

```powershell
git checkout -b feature/update-sql
git add .
git commit -m "Update mart query"
git push -u origin feature/update-sql
```

Sau do:

1. len GitHub
2. tao Pull Request vao `main`
3. doi CI chay xong
4. merge neu pass

### Badge CI trong README

Repo da duoc them badge CI o dau file `README.md`.

Khi workflow pass, badge se hien trang thai xanh.
Khi workflow fail, badge se hien trang thai do.

## 12. Ket luan ngan

Co, project nay setup CI/CD duoc.

Nhung voi repo nay va voi nguoi moi, cach dung nhat la:

1. bat dau bang `CI`
2. chi kiem tra build + Airflow DAG parse
3. sau do moi them `CD` khi da co server deploy ro rang
