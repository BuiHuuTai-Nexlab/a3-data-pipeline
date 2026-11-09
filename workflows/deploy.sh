#!/bin/bash
# Tao (hoac cap nhat) workflow + lich chay. Chay lai nhieu lan van an toan.
# usage: bash workflows/deploy.sh [cron]   (mac dinh 02:00 moi ngay, gio Viet Nam)
set -e
PROJECT=a3-retail-dwh-project
REGION=asia-southeast1
CRON="${1:-0 2 * * *}"

WORKFLOW_SA=pipeline-workflow-sa
SCHEDULER_SA=pipeline-scheduler-sa
WORKFLOW_SA_EMAIL="$WORKFLOW_SA@$PROJECT.iam.gserviceaccount.com"
SCHEDULER_SA_EMAIL="$SCHEDULER_SA@$PROJECT.iam.gserviceaccount.com"

# --- Service account: workflow chay batch + SQL, scheduler chi duoc goi workflow ---
for sa in $WORKFLOW_SA $SCHEDULER_SA; do
  gcloud iam service-accounts describe "$sa@$PROJECT.iam.gserviceaccount.com" --project=$PROJECT >/dev/null 2>&1 ||
    gcloud iam service-accounts create "$sa" --project=$PROJECT
done

for role in roles/dataproc.editor roles/bigquery.jobUser roles/bigquery.dataEditor \
            roles/storage.objectViewer roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$WORKFLOW_SA_EMAIL" \
    --role="$role" --condition=None --quiet >/dev/null
done
# batch chay duoi ingest-bronze-sa nen workflow can quyen "actAs" SA do
gcloud iam service-accounts add-iam-policy-binding \
  ingest-bronze-sa@$PROJECT.iam.gserviceaccount.com \
  --member="serviceAccount:$WORKFLOW_SA_EMAIL" --role=roles/iam.serviceAccountUser \
  --project=$PROJECT --quiet >/dev/null
gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SCHEDULER_SA_EMAIL" \
  --role=roles/workflows.invoker --condition=None --quiet >/dev/null

# --- Workflow ---
gcloud workflows deploy a3-data-pipeline --project=$PROJECT --location=$REGION \
  --source="$(dirname "$0")/pipeline.yaml" --service-account="$WORKFLOW_SA_EMAIL"

# --- Lich chay (Cloud Scheduler -> goi Workflows API) ---
URI="https://workflowexecutions.googleapis.com/v1/projects/$PROJECT/locations/$REGION/workflows/a3-data-pipeline/executions"
if gcloud scheduler jobs describe a3-data-pipeline-daily --location=$REGION --project=$PROJECT >/dev/null 2>&1; then
  ACTION=update
else
  ACTION=create
fi
gcloud scheduler jobs $ACTION http a3-data-pipeline-daily --project=$PROJECT --location=$REGION \
  --schedule="$CRON" --time-zone="Asia/Ho_Chi_Minh" \
  --uri="$URI" --http-method=POST --message-body='{}' \
  --oauth-service-account-email="$SCHEDULER_SA_EMAIL"
