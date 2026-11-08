# A3 Data Pipeline

Spark ingest pipeline (bronze/silver/gold) cho A3 Retail DWH, chạy trên Dataproc Serverless, ghi vào BigQuery.

## Quy trình dev

1. **Sửa code** trong `src/` hoặc `utils/` ở local (`D:\Downloads\a3-data-pipeline`).

2. **Sync code lên GCS** để test (không cần commit/push trước):
   ```bash
   bash sync.sh
   ```

3. **Submit job test trên Dataproc**:
   ```bash
   gcloud dataproc batches submit pyspark \
     gs://a3-data-pipeline-code/src/bronze/ingest_merchant.py \
     --project=a3-retail-dwh-project \
     --region=asia-southeast1 \
     --service-account=ingest-bronze-sa@a3-retail-dwh-project.iam.gserviceaccount.com \
     --py-files=gs://a3-data-pipeline-code/utils.zip \
     --batch=ingest-merchant-$(date +%s)
   ```

4. **Check kết quả**:
   ```bash
   bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `a3-retail-dwh-project.bronze_layer.merchant`'
   gcloud dataproc batches describe <batch-id> --region=asia-southeast1
   ```

5. **Pass thì mới commit + push** lên GitHub:
   ```bash
   git add -A
   git commit -m "mô tả thay đổi"
   git push
   ```
   - Push nhánh khác / mở PR → **CI** chạy (lint + compile check).
   - Push vào `master` → **CD** tự build `utils.zip` và sync `src/` + `utils.zip` lên `gs://a3-data-pipeline-code/` (ghi đè lại y hệt bản đã test ở bước 2, coi như xác nhận cuối).

> Tóm gọn: **sửa code → sync → submit test → pass thì mới push → (CD tự re-sync).**
> Không chạy local — test trực tiếp trên Dataproc Serverless, tránh push code chưa test lên `master`.
