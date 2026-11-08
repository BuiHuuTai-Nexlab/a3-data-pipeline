import base64
import io
import json
import subprocess
import sys

try:
    import openpyxl  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])

import pandas as pd
import requests
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account

from utils.logger import get_logger

logger = get_logger("gsheet_reader")

SPREADSHEET_ID = "1pFytw4w0qI2z_Y-QAP92ozzB5oY59loK"
MERCHANT_URL = f"https://www.googleapis.com/drive/v3/files/{SPREADSHEET_ID}?alt=media"
SHEET_NAME = "merchant"
SECRET_URL = (
    "https://secretmanager.googleapis.com/v1/"
    "projects/a3-retail-dwh-project/secrets/ingest-bronze-sa-key/versions/latest:access"
)


def _get_drive_credentials():
    # Ambient credentials (cloud-platform scope) work fine for Secret Manager,
    # but not for Drive — Drive needs an explicitly scoped service account key.
    ambient_creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    ambient_creds.refresh(Request())

    response = requests.get(SECRET_URL, headers={"Authorization": f"Bearer {ambient_creds.token}"})
    response.raise_for_status()
    key_info = json.loads(base64.b64decode(response.json()["payload"]["data"]))

    return service_account.Credentials.from_service_account_info(
        key_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )


def read_merchant_sheet(spark):
    try:
        credentials = _get_drive_credentials()
        credentials.refresh(Request())

        response = requests.get(MERCHANT_URL, headers={"Authorization": f"Bearer {credentials.token}"})
        response.raise_for_status()

        pdf = pd.read_excel(io.BytesIO(response.content), sheet_name=SHEET_NAME)
        pdf = pdf.astype(str).where(pdf.notna(), None)
        return spark.createDataFrame(pdf)

    except Exception:
        logger.exception("Failed to read merchant sheet from Google Drive")
        raise
