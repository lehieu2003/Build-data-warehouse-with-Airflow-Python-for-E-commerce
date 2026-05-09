# CD mien phi len Render cho repo nay

Tai lieu nay huong dan cach deploy tu dong repo Airflow nay len Render free chi de hoc `CD`.

## 1. Ban can hieu gioi han truoc

Ban dang deploy theo kieu demo, khong phai production.

Ban build 1 Airflow service duy nhat bang `airflow standalone`.

No co cac gioi han:

- dung SQLite noi bo
- filesystem ephemereal
- service free co the sleep khi idle
- khong phu hop de chay warehouse production that

No du cho muc tieu hoc:

- push code
- CI chay
- CI xanh
- GitHub Actions goi Render deploy hook
- Render build va cap nhat service

## 2. File da duoc them

- [Dockerfile.render](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Dockerfile.render)
- [render.yaml](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/render.yaml)
- [scripts/render-start.sh](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/scripts/render-start.sh)
- [cd-render.yml](/c:/Users/daong/Downloads/Build-data-warehouse-with-Airflow-Python-for-E-commerce/Build-data-warehouse-with-Airflow-Python-for-E-commerce/.github/workflows/cd-render.yml)

## 3. Luong CD sau khi setup xong

Luong se la:

1. ban push code len `main`
2. workflow `Airflow CI` chay
3. neu CI pass
4. workflow `Render CD` moi chay
5. workflow goi `RENDER_DEPLOY_HOOK_URL`
6. Render tu build va deploy service moi

## 4. Cach tao service tren Render

### Cach nhanh nhat

1. Dang nhap Render.
2. Chon `New`.
3. Chon `Blueprint`.
4. Ket noi GitHub repo nay.
5. Chon branch `main`.
6. Render se doc file `render.yaml`.
7. Approve tao service `airflow-demo`.

Luu y:

- trong `render.yaml`, service dang de `autoDeployTrigger: off`
- ly do la deploy se do GitHub Actions chu dong trigger qua deploy hook
- tranh bi deploy 2 lan

## 5. Lay deploy hook URL

Sau khi service duoc tao tren Render:

1. Mo service `airflow-demo`
2. Vao `Settings`
3. Tim `Deploy Hook`
4. Copy URL nay

Theo Render docs, moi service co mot deploy hook URL rieng va co the trigger bang `GET` hoac `POST`.

Nguon:

- https://render.com/docs/deploy-hooks

## 6. Tao GitHub Secret

Trong repo GitHub:

1. `Settings`
2. `Secrets and variables`
3. `Actions`
4. `New repository secret`

Tao secret:

- Name: `RENDER_DEPLOY_HOOK_URL`
- Value: URL ban vua copy tu Render

## 7. Push code de chay CD

Khi secret da co, push len `main`:

```powershell
git add .
git commit -m "Add Render CD demo workflow"
git push
```

Sau do tren GitHub:

1. vao tab `Actions`
2. xem `Airflow CI`
3. doi `Airflow CI` pass
4. xem `Render CD` tu chay tiep

Neu `Render CD` xanh, Render da nhan lenh deploy.

## 8. Cach test nhanh

Test an toan nhat:

1. sua 1 dong nho trong `README.md`
2. merge vao `main`
3. vao `Actions`
4. thay `Airflow CI` pass
5. thay `Render CD` pass
6. vao Render xem co deploy moi duoc tao khong

## 9. Cach mo Airflow tren Render

Sau khi deploy xong:

1. mo URL `onrender.com` cua service
2. neu service dang sleep, doi no wake len
3. vao Airflow UI

Vi project dang dung `airflow standalone`, tai khoan admin thuong duoc tao luc startup va thong tin dang nhap co the xuat hien trong log startup.

Neu can, vao `Logs` tren Render de xem.

## 10. Neu CD khong chay

Kiem tra theo thu tu:

1. `Airflow CI` co pass khong
2. ban co push vao `main` khong
3. secret `RENDER_DEPLOY_HOOK_URL` da tao chua
4. service Render da ton tai chua
5. deploy hook URL co dung service khong

## 11. Dieu quan trong

CD nay la de hoc quy trinh:

- source control
- CI gate
- secret
- deploy trigger
- cloud build
- release moi

No khong phai cach nen dung de van hanh Airflow production lau dai tren free tier.
