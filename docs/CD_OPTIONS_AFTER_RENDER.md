# Sau khi Render free that bai thi lam gi?

Tai lieu nay noi ngan gon cac huong thuc te sau khi da biet Render free khong du RAM cho Airflow.

## 1. Ket luan ky thuat

Render free deploy da di den muc runtime, nhung bi:

- `Out of memory (used over 512Mi)`

Nen van de la ha tang, khong phai workflow CD.

## 2. Cac huong tiep theo

### Huong 1: Dung case nay de hoc CD

Giu nguyen workflow hien tai de hoc:

- CI gate
- workflow chaining
- GitHub secret
- cloud hook
- image build

Huong nay phu hop neu muc tieu cua ban la hoc.

### Huong 2: Chuyen sang GitHub Actions schedule

Khong host Airflow web UI nua.

Dung GitHub Actions de:

- chay ETL theo lich
- hoac chay bang tay

Huong nay thuc te hon neu ban muon free.

### Huong 3: Doi target deploy

Neu ban muon giu Airflow web UI, thuong ban can:

- VPS rieng
- hoac plan tra phi

## 3. Khuyen nghi cho nguoi moi

Neu ban dang hoc:

1. giu lai toan bo tai lieu debug nay
2. xem nhu CD pipeline da thanh cong ve mat hoc tap
3. sau do chuyen sang huong GitHub Actions schedule neu muon free that su
