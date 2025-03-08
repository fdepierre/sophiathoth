from minio import Minio
from minio.error import S3Error
import io
import logging
from app.config import settings
import uuid

logger = logging.getLogger(__name__)


class MinioClient:
    """Client for interacting with MinIO object storage"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, creating it if necessary"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(self, file_data: bytes, content_type: str, filename: str = None) -> str:
        """
        Upload a file to MinIO
        
        Args:
            file_data: The file data as bytes
            content_type: The content type of the file
            filename: Optional filename to use
            
        Returns:
            The object name in MinIO
        """
        if filename is None:
            filename = f"attachment_{uuid.uuid4()}"
        
        try:
            file_stream = io.BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=file_stream,
                length=len(file_data),
                content_type=content_type
            )
            logger.info(f"Uploaded file to MinIO: {filename}")
            return filename
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from MinIO
        
        Args:
            object_name: The object name in MinIO
            
        Returns:
            The file data as bytes
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            file_data = response.read()
            response.close()
            response.release_conn()
            return file_data
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO
        
        Args:
            object_name: The object name in MinIO
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            logger.info(f"Deleted file from MinIO: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {e}")
            return False


# Create a singleton instance
minio_client = MinioClient()
