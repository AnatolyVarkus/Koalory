"""
app/services/google_storage_service.py
Lazy, singleton GCS client; no globals created at import time.
"""

from __future__ import annotations

import requests
from io import BytesIO
from fastapi import HTTPException
from google.cloud import storage
from google.oauth2 import service_account
from app.core import settings

# ──────────────────────────────────────────────────────────────────────────────
#  Auth
# ──────────────────────────────────────────────────────────────────────────────
KEY_PATH = "/home/koalory_bot/Koalory/app/koalory_google.json"


def _build_client() -> storage.Client:
    """Create a Storage client that always uses the service-account key file."""
    creds = service_account.Credentials.from_service_account_file(KEY_PATH)
    return storage.Client(project=creds.project_id, credentials=creds)


def get_storage_client() -> storage.Client:
    """
    Thread-safe, lazy singleton.

    The attribute trick avoids module-level state at import; the first call
    builds the client, subsequent calls reuse it.
    """
    if not hasattr(get_storage_client, "_client"):
        get_storage_client._client = _build_client()
    return get_storage_client._client


def _get_bucket() -> storage.bucket.Bucket:
    """Same lazy pattern for the bucket object."""
    if not hasattr(_get_bucket, "_bucket"):
        _get_bucket._bucket = get_storage_client().bucket(settings.BUCKET_NAME)
    return _get_bucket._bucket


# ──────────────────────────────────────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────────────────────────────────────
def upload_avatar(photo_get_url: str, blob_name: str,
                  content_type: str = "image/png") -> str:
    """Fetch an image from `photo_get_url` and upload it to GCS."""
    response = requests.get(photo_get_url)
    response.raise_for_status()

    blob = _get_bucket().blob(blob_name)
    blob.upload_from_string(response.content, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"


def upload_image(content: bytes | str, blob_name: str,
                 content_type: str = "image/png") -> str:
    """Upload raw bytes/str already in memory."""
    data = content.encode() if isinstance(content, str) else content

    blob = _get_bucket().blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"


def upload_pdf(blob_name: str, pdf_buffer: BytesIO,
               content_type: str = "application/pdf") -> str:
    """Upload a PDF held in a BytesIO buffer."""
    blob = _get_bucket().blob(blob_name)
    blob.upload_from_file(pdf_buffer, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"


def get_blob_link(blob_name: str) -> str:
    """Return a public URL if the blob exists, else 404."""
    blob = _get_bucket().blob(blob_name)
    if not blob.exists():
        raise HTTPException(status_code=404, detail=f"Blob '{blob_name}' not found")
    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"