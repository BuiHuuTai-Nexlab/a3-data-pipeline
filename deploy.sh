#!/bin/bash
set -e
MAIN_FILE="${1:-src/bronze/ingest_merchant.py}"

# --- Phase 1: Sync code (src/ + utils.zip) to GCS ---
echo "=== Syncing code to GCS ==="
ZIP_PATH=$(python -c "
import zipfile, os, tempfile
fd, zip_path = tempfile.mkstemp(suffix='.zip')
os.close(fd)
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('utils'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                zf.write(path, path)
print(zip_path)
")
trap 'rm -f "$ZIP_PATH"' EXIT

gsutil -m rsync -r src gs://a3-data-pipeline-code/src
gsutil cp "$ZIP_PATH" gs://a3-data-pipeline-code/utils.zip
echo "Sync done."

# --- Phase 2: Submit batch job to Dataproc Serverless ---
echo "=== Submitting batch to Dataproc ==="
JOB_NAME=$(basename "$MAIN_FILE" .py | tr '_' '-')
BATCH_ID="ingest-${JOB_NAME}-$(date +%Y%m%d%H%M%S)"

gcloud dataproc batches submit pyspark \
  "gs://a3-data-pipeline-code/$MAIN_FILE" \
  --project=a3-retail-dwh-project \
  --region=asia-southeast1 \
  --service-account=ingest-bronze-sa@a3-retail-dwh-project.iam.gserviceaccount.com \
  --py-files=gs://a3-data-pipeline-code/utils.zip \
  --batch="$BATCH_ID"
