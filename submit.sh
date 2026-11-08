#!/bin/bash
set -e
MAIN_FILE="${1:-src/bronze/ingest_merchant.py}"
JOB_NAME=$(basename "$MAIN_FILE" .py | tr '_' '-')
BATCH_ID="ingest-${JOB_NAME}-$(date +%Y%m%d%H%M%S)"

gcloud dataproc batches submit pyspark \
  "gs://a3-data-pipeline-code/$MAIN_FILE" \
  --project=a3-retail-dwh-project \
  --region=asia-southeast1 \
  --service-account=ingest-bronze-sa@a3-retail-dwh-project.iam.gserviceaccount.com \
  --py-files=gs://a3-data-pipeline-code/utils.zip \
  --batch="$BATCH_ID"
