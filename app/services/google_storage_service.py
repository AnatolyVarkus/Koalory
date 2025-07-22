from google.cloud import storage
from app.core import settings
from fastapi import HTTPException

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