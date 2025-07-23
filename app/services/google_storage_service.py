from google.cloud import storage
from app.core import settings
from fastapi import HTTPException
from io import BytesIO
import requests

class GCSUploader:
    """
    Handles uploading images to Google Cloud Storage
    """

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.BUCKET_NAME)

    def upload_avatar(self, photo_get_url: str, photo_url: str, content_type: str = "image/png"):
        """
        Upload photo to GCS under name {job_id}_avatar_image

        Args:
            job_id (int): Job ID used as filename
            photo_bytes (bytes): Image data
            content_type (str): MIME type of the image

        Returns:
            str: Public URL of the uploaded image
        """
        response = requests.get(photo_get_url)
        response.raise_for_status()

        blob = self.bucket.blob(photo_url)
        blob.upload_from_string(response.content, content_type=content_type)

        return f"https://storage.googleapis.com/koalory_bucket/{photo_url}"

    def upload_image(self, content: str, photo_url: str, content_type: str = "image/png"):
        """
        Upload photo to GCS under name {job_id}_avatar_image

        Args:
            job_id (int): Job ID used as filename
            photo_bytes (bytes): Image data
            content_type (str): MIME type of the image

        Returns:
            str: Public URL of the uploaded image
        """

        blob = self.bucket.blob(photo_url)
        blob.upload_from_string(content, content_type=content_type)

        return f"https://storage.googleapis.com/koalory_bucket/{photo_url}"

    def upload_pdf(self, pdf_name: str, pdf_buffer: BytesIO, content_type: str = "application/pdf") -> str:
        """
        Uploads a PDF file to Google Cloud Storage.

        Args:
            pdf_name (str): Desired name (without extension) for the uploaded PDF.
            pdf_buffer (BytesIO): In-memory PDF file.
            content_type (str): MIME type, defaults to "application/pdf".

        Returns:
            str: Public URL to the uploaded PDF.
        """
        print(f"Uploading {pdf_name} to Google Cloud Storage")


        blob = self.bucket.blob(pdf_name)

        blob.upload_from_file(pdf_buffer, content_type=content_type)

        return f"https://storage.googleapis.com/koalory_bucket/{pdf_name}"

    def get_avatar_link(self, photo_url: str):
        """
        Retrieves the avatar image from GCS for the given job_id as bytes.

        Args:
            job_id (int): Job ID used as filename

        Returns:
            bytes: Image data

        Raises:
            FileNotFoundError: If the blob does not exist
        """
        blob_name = (photo_url.split("/")[-1])
        blob = self.bucket.blob(blob_name)

        print(f"{blob.exists() = }")
        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"No avatar image found {photo_url}")

        return photo_url

    def get_pdf_link(self, user_id: int, job_id: int):
        """
        Retrieves the avatar image from GCS for the given job_id as bytes.

        Args:
            job_id (int): Job ID used as filename

        Returns:
            bytes: Image data

        Raises:
            FileNotFoundError: If the blob does not exist
        """
        blob_name = f"{user_id}|{job_id}.pdf"
        blob = self.bucket.blob(blob_name)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"No avatar image found for job_id {job_id}")

gcs_uploader = None

def get_gcs_uploader():
    global gcs_uploader
    if gcs_uploader is None:
        gcs_uploader = GCSUploader()
    return gcs_uploader