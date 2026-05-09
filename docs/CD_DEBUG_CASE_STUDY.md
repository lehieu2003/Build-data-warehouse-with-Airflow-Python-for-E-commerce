# Case Study: Cach debug CD Render cho nguoi moi

Tai lieu nay khong chi noi ket qua, ma giai thich **toi da doc log nhu the nao**, **suy luan ra sao**, va **vi sao chon buoc sua tiep theo**.

Day la cach ban nen hoc khi gap loi CI/CD:

1. doc dung dong loi that
2. xac dinh loi dang o giai doan nao
3. sua 1 gia thuyet moi lan
4. push lai
5. doc log moi
6. lap lai cho den khi tim ra root cause

## 1. Muc tieu ban dau

Muc tieu cua chung ta la:

- push code len GitHub
- CI chay truoc
- neu CI pass thi trigger CD
- Render tu build va deploy

Noi ngan gon:

`push -> CI -> CD -> Render deploy`

## 2. Cach chia mot loi CD thanh tung tang

Khi 1 deploy fail, dung nhin no nhu mot khoi mo ho.

Hay tach no thanh 4 tang:

1. Tang trigger
   - GitHub Actions co chay workflow CD khong
2. Tang hook
   - GitHub co goi duoc Render hook khong
3. Tang build
   - Render co build image thanh cong khong
4. Tang runtime
   - container chay len co mo port, co du RAM, co boot xong app khong

Day la cach toi debug trong ca qua trinh nay.

## 3. Loi 1: GitHub Actions fail vi khong co `.env`

### Dau hieu trong log

Log CI bao:

- `env file ... .env not found`

### Suy luan

Dieu nay cho thay:

- workflow da chay
- `docker compose` da duoc goi
- nhung runner tren GitHub khong co file `.env` local cua ban

Loi nay nam o tang `CI environment`, chua lien quan den Render.

### Cach sua

Toi them step tao `.env` tam trong workflow CI.

### Bai hoc

Dung gia dinh moi truong CI giong may local.

Neu file config local khong duoc commit, CI phai tu tao no hoac lay tu secret.

## 4. Loi 2: Permission denied voi thu muc `logs`

### Dau hieu trong log

Log bao:

- `Permission denied: '/opt/airflow/logs/scheduler'`

### Suy luan

Docker Compose mount thu muc local vao container.

Airflow trong container can ghi vao `logs`, nhung thu muc local tren GitHub runner chua co quyen phu hop.

### Cach sua

Toi tao san:

- `logs`
- `config`
- `plugins`

va `chmod` cho phep container ghi.

### Bai hoc

Nhieu loi Docker/Airflow khong phai do code Python, ma do volume va permission.

## 5. Loi 3: Tren Render khong thay `Deploy Hook`

### Dau hieu

Ban vao Render va thay `Sync Hook` trong `Blueprint Settings`, khong thay `Deploy Hook`.

### Suy luan

Ban dang deploy theo kieu `Blueprint`.

Voi Blueprint:

- hook tu nhien nhat la `Sync Hook`

Voi service rieng le:

- hook tu nhien nhat la `Deploy Hook`

### Cach sua

Toi sua workflow CD de chap nhan ca:

- `RENDER_SYNC_HOOK_URL`
- `RENDER_DEPLOY_HOOK_URL`

### Bai hoc

Khong phai luc nao giao dien cloud cung giong tutorial. Phai nhin ban dang dung loai tai nguyen nao.

## 6. Loi 4: `chown` fail trong Docker build

### Dau hieu trong log

Log Render build bao lenh:

- `chown -R airflow:0 ...`

fail.

### Suy luan

`chown` can quyen `root`.

Neu dang o user `airflow` ma chay `chown`, no se fail.

### Cach sua

Toi chuyen `Dockerfile.render` sang:

- `USER airflow` cho `pip install`
- `USER root` cho `COPY`, `chmod`, `chown`
- `USER airflow` truoc khi chay app

### Bai hoc

Dockerfile cua Airflow co 2 quy tac de nho:

1. `pip install` nen chay bang user `airflow`
2. thao tac quyen file nen chay bang `root`

## 7. Loi 5: `pip install` fail vi dang chay bang `root`

### Dau hieu trong log

Log bao:

- `You are running pip as root. Please use 'airflow' user to run pip!`

### Suy luan

Airflow image khong khuyen khich va co the chan install package bang `root`.

### Cach sua

Toi doi thu tu user trong Dockerfile:

- `USER airflow`
- `RUN pip install ...`
- `USER root`

### Bai hoc

Khi base image in thong diep huong dan ro rang, dung co co sua meo. Lam theo pattern cua base image.

## 8. Loi 6: Render bao `No open ports detected`

### Dau hieu trong log

Log bao:

- `No open ports detected, continuing to scan...`

### Suy luan

Dieu nay thuong co 2 kha nang:

1. app chua bind vao `0.0.0.0:$PORT`
2. app chua kip boot xong de mo cong

Luc nay chua du du lieu de ket luan la do config port hay do app boot cham.

### Cach sua

Toi sua script startup de:

- bind ro `0.0.0.0`
- dung `${PORT:-10000}`

sau do push lai de lay them log moi.

### Bai hoc

Khi gap loi port tren cloud:

- dung sua 10 thu cung luc
- sua toi thieu de log tiep theo no noi nhieu hon

## 9. Loi 7: `airflow standalone` khong phu hop

### Dau hieu

Du da bind port, Render van khong thay cong mo.

### Suy luan

`airflow standalone` la mot lenh tien cho local demo, nhung khong phai luc nao cung hop cho web service cloud.

No gom nhieu buoc:

- init db
- tao user
- chay scheduler
- chay webserver

Nhieu buoc hon nghia la kho debug hon.

### Cach sua

Toi tach thanh tung buoc ro rang:

- `airflow db migrate` hoac `db init`
- `airflow users create`
- `airflow webserver`

### Bai hoc

Khi mot lenh “all-in-one” kho debug, hay tach no thanh nhieu buoc ro rang.

## 10. Loi 8: Script startup co the chua thuc su duoc chay

### Dau hieu

Van khong thay log `echo` cua script.

### Suy luan

Base image `apache/airflow` co `ENTRYPOINT` rieng.

Neu `CMD` khong dung dang, no co the bi Airflow entrypoint xu ly nhu tham so cho `airflow`, thay vi chay shell script cua ban.

### Cach sua

Toi doi:

```dockerfile
CMD ["/opt/airflow/scripts/render-start.sh"]
```

thanh:

```dockerfile
CMD ["bash", "-c", "/opt/airflow/scripts/render-start.sh"]
```

### Bai hoc

Voi base image phuc tap, can luon de y `ENTRYPOINT` va `CMD` tuong tac voi nhau the nao.

## 11. Loi 9: Gunicorn boot qua cham

### Dau hieu trong log

Log moi bao:

- `Starting gunicorn`
- `Host: 0.0.0.0:10000`
- `No response from gunicorn master within 120 seconds`

### Suy luan

Luc nay ta biet:

- script startup da chay
- webserver dang co gang boot
- port config da dung

Loi da chuyen tu “khong chay” sang “chay nhung qua cham”.

### Cach sua

Toi thu:

- giam `workers` xuong `1`
- tang timeout len `300`

### Bai hoc

Khi log cho thay mot tang da ok, dung quay lai sua tang cu. Phai day debug sang tang tiep theo.

## 12. Loi 10: Het RAM

### Dau hieu trong log

Log cuoi cung bao ro:

- `Out of memory (used over 512Mi)`

### Suy luan

Day la root cause that su cua free tier.

Khong con la loi config nua.

Khong con la loi Dockerfile nua.

Khong con la loi GitHub Actions nua.

Render free instance chi co `512Mi`, va Airflow webserver + dependencies vuot qua muc nay.

### Ket luan ky thuat

CD pipeline cua ban **co hoat dong**:

- GitHub Actions trigger dung
- hook Render goi dung
- Render build image dung
- container chay duoc toi muc boot Airflow

Nhung **target free khong du RAM de van hanh Airflow**.

### Bai hoc

Debug tot khong phai luc nao cung dan den “fix duoc”.

Nhieu luc debug tot dan den mot ket luan quan trong hon:

- bai toan nay khong phai loi code
- bai toan nay la gioi han ha tang

Do cung la mot ket qua dung.

## 13. Cach toi lua chon buoc tiep theo moi lan

Moi lan doc log, toi tu hoi 3 cau:

1. Loi nay thuoc tang nao?
   - trigger
   - build
   - runtime
   - memory/network/permission

2. Co bang chung nao moi xuat hien so voi lan truoc?
   - vi du tu `No open ports detected`
   - sang `Starting gunicorn`
   - sang `Out of memory`

3. Buoc sua tiep theo co thu hep pham vi gia thuyet duoc khong?
   - neu co, lam
   - neu khong, dung sua qua nhieu thu cung luc

## 14. Cach ban nen doc log trong tuong lai

Cho nguoi moi, hay doc log theo thu tu nay:

### Buoc 1: Tim dong `ERROR`, `failed`, `Permission denied`, `Out of memory`

Dung tim toan bo log truoc.

Tim dong khoanh vung loi that.

### Buoc 2: Xac dinh no xay ra luc nao

- trong CI?
- trong build image?
- sau khi deploy?
- khi app da start?

### Buoc 3: Doc 10-20 dong truoc dong loi

Rat nhieu nguoi moi chi doc dong cuoi. Nhu vay thuong khong du.

### Buoc 4: Dat 1 gia thuyet

Vi du:

- thieu file
- sai quyen
- sai user
- sai port
- boot cham
- het RAM

### Buoc 5: Sua toi thieu

Khong sua 5 file cung luc neu khong can.

Sua it de log lan sau noi ro hon.

## 15. Ket luan cho case nay

Neu noi dung va thang vao van de:

- CI: thanh cong
- CD workflow: thanh cong
- Render hook: thanh cong
- Render build: thanh cong
- runtime Airflow: that bai vi free tier `512Mi` khong du RAM

Nen ket luan dung la:

`CD pipeline hoc tap da hoat dong, nhung Render free khong phai target phu hop de chay Airflow`

## 16. Ban hoc duoc gi tu case nay

Ban da di qua gan nhu du het cac nhom loi pho bien cua CI/CD:

- thieu env
- volume permission
- nham loai hook cloud
- Docker user/quyen
- entrypoint/CMD
- port binding
- boot timeout
- memory limit

Neu ban hieu duoc chuoi nay, ban da co mot nen tang rat tot de debug nhung he thong khac.
