from google.cloud import storage
from app.core import settings
from fastapi import HTTPException
from io import BytesIO

class GCSUploader:
    """
    Handles uploading images to Google Cloud Storage
    """

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.BUCKET_NAME)

    def upload_avatar(self, photo_url: str, photo_bytes: bytes, content_type: str = "image/png"):
        """
        Upload photo to GCS under name {job_id}_avatar_image

        Args:
            job_id (int): Job ID used as filename
            photo_bytes (bytes): Image data
            content_type (str): MIME type of the image

        Returns:
            str: Public URL of the uploaded image
        """
        blob_name = f"{photo_url}.png"
        blob = self.bucket.blob(blob_name)

        blob.upload_from_string(photo_bytes, content_type=content_type)
        blob.make_public()

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
        blob_name = f"{pdf_name}.pdf"
        blob = self.bucket.blob(blob_name)

        blob.upload_from_file(pdf_buffer, content_type=content_type)
        blob.make_public()

        return blob.public_url

    def get_avatar_link(self, job_id: int):
        """
        Retrieves the avatar image from GCS for the given job_id as bytes.

        Args:
            job_id (int): Job ID used as filename

        Returns:
            bytes: Image data

        Raises:
            FileNotFoundError: If the blob does not exist
        """
        blob_name = f"{job_id}_avatar_image.png"
        blob = self.bucket.blob(blob_name)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"No avatar image found for job_id {job_id}")



gcs_uploader = GCSUploader()