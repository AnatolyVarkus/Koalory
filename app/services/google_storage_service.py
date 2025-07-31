from __future__ import annotations

import requests
from io import BytesIO
from fastapi import HTTPException
from google.cloud import storage
from google.oauth2 import service_account
from app.core import settings

KEY_PATH = "/home/koalory_bot/Koalory/app/koalory_google.json"


def _build_client() -> storage.Client:
    creds = service_account.Credentials.from_service_account_file(KEY_PATH)
    return storage.Client(project=creds.project_id, credentials=creds)


def get_storage_client() -> storage.Client:
    if not hasattr(get_storage_client, "_client"):
        get_storage_client._client = _build_client()
    return get_storage_client._client

def _get_bucket() -> storage.bucket.Bucket:
    if not hasattr(_get_bucket, "_bucket"):
        _get_bucket._bucket = get_storage_client().bucket(settings.BUCKET_NAME)
    return _get_bucket._bucket

def upload_avatar(photo_get_url: str, blob_name: str,
                  content_type: str = "image/png") -> str:
    response = requests.get(photo_get_url)
    response.raise_for_status()

    blob = _get_bucket().blob(blob_name)
    blob.upload_from_string(response.content, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"

def upload_image(content: bytes | str, blob_name: str,
                 content_type: str = "image/png") -> str:
    data = content.encode() if isinstance(content, str) else content

    blob = _get_bucket().blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"

def upload_pdf(blob_name: str, pdf_buffer: BytesIO,
               content_type: str = "application/pdf") -> str:
    blob = _get_bucket().blob(blob_name)
    blob.upload_from_file(pdf_buffer, content_type=content_type)

    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"

def get_blob_link(blob_name: str) -> str:
    blob = _get_bucket().blob(blob_name)
    if not blob.exists():
        raise HTTPException(status_code=404, detail=f"Blob '{blob_name}' not found")
    return f"https://storage.googleapis.com/{settings.BUCKET_NAME}/{blob_name}"