from minio import Minio
from minio.error import S3Error
import io
import logging
from .config import settings
import uuid
from functools import lru_cache # Optional: Could use for caching client

logger = logging.getLogger(__name__)


class MinioClient:
    """Client for interacting with MinIO object storage with lazy initialization."""
    
    def __init__(self):
        # Store config but defer client creation
        self._endpoint = settings.MINIO_ENDPOINT
        self._access_key = settings.MINIO_ACCESS_KEY
        self._secret_key = settings.MINIO_SECRET_KEY
        self._secure = settings.MINIO_SECURE
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._client = None # Defer client instantiation

    def _get_client(self) -> Minio:
        """Lazily initializes the Minio client and ensures bucket exists on first call."""
        if self._client is None:
            logger.info(f"Initializing Minio client for endpoint: {self._endpoint}")
            try:
                self._client = Minio(
                    self._endpoint,
                    access_key=self._access_key,
                    secret_key=self._secret_key,
                    secure=self._secure
                )
                # Ensure bucket exists only after successful client creation
                self._ensure_bucket_exists()
                logger.info(f"Minio client initialized successfully for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Minio client or ensure bucket: {e}")
                self._client = None # Ensure client remains None on failure
                raise # Re-raise the exception to indicate connection failure
        return self._client

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, creating it if necessary.
        Assumes the client object is already created (called by _get_client).
        """
        # This check now relies on _get_client() being called first elsewhere
        # Or we ensure client is not None before proceeding
        client = self._client # Should not be None if called from _get_client
        if not client:
             # This case should ideally not happen if called correctly, but safety check
             logger.error("Attempted to ensure bucket exists before client initialization.")
             raise ConnectionError("Minio client not initialized.") 
             
        try:
            if not client.bucket_exists(self.bucket_name):
                client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(self, file_data: bytes, content_type: str, filename: str = None) -> str:
        """
        Upload a file to MinIO
        """
        if filename is None:
            filename = f"{uuid.uuid4()}.xlsx" # Assuming default, adjust if needed
            
        client = self._get_client() # Get or initialize client
        if not client: 
             raise ConnectionError("Failed to get Minio client for upload.")
             
        try:
            file_stream = io.BytesIO(file_data)
            client.put_object(
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
        """
        client = self._get_client() # Get or initialize client
        if not client: 
             raise ConnectionError("Failed to get Minio client for download.")
             
        try:
            response = client.get_object(
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
        """
        client = self._get_client() # Get or initialize client
        if not client: 
             raise ConnectionError("Failed to get Minio client for delete.")
             
        try:
            client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            logger.info(f"Deleted file from MinIO: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {e}")
            return False


# Create a singleton instance (instantiation itself is now safe)
minio_client = MinioClient()
