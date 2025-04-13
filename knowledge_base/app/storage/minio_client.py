"""
MinIO client for object storage.
This module provides file storage functionality using MinIO.
"""
import os
import logging
from typing import Optional, Dict, Any
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

class MinioClient:
    """Client for MinIO object storage operations."""
    
    def __init__(self):
        """Initialize the MinIO client."""
        self.minio_endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        self.minio_secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
        self.minio_bucket = os.environ.get("MINIO_BUCKET", "sophiathoth")
        self.use_ssl = os.environ.get("MINIO_USE_SSL", "false").lower() == "true"
        
        self.client = Minio(
            self.minio_endpoint,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=self.use_ssl
        )
        
        # Ensure bucket exists
        try:
            if not self.client.bucket_exists(self.minio_bucket):
                self.client.make_bucket(self.minio_bucket)
        except S3Error as e:
            logger.error(f"Error initializing MinIO bucket: {e}")
    
    def upload_file(
        self,
        file_data: bytes,
        object_name: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to MinIO.
        
        Args:
            file_data: File data as bytes
            object_name: Name of the object in MinIO
            content_type: Content type of the file
            
        Returns:
            Dictionary with upload details
        """
        try:
            result = self.client.put_object(
                bucket_name=self.minio_bucket,
                object_name=object_name,
                data=file_data,
                length=len(file_data),
                content_type=content_type
            )
            
            return {
                "bucket": result.bucket_name,
                "object": result.object_name,
                "version_id": result.version_id,
                "etag": result.etag
            }
            
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from MinIO.
        
        Args:
            object_name: Name of the object in MinIO
            
        Returns:
            File data as bytes
        """
        try:
            response = self.client.get_object(
                bucket_name=self.minio_bucket,
                object_name=object_name
            )
            return response.read()
            
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            object_name: Name of the object in MinIO
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.remove_object(
                bucket_name=self.minio_bucket,
                object_name=object_name
            )
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {e}")
            return False

# Create a singleton instance
minio_client = MinioClient()
