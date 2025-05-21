"""
Google Cloud Storage Integration

This module provides functionality for interacting with Google Cloud Storage,
including authentication, file operations, and change monitoring.
"""

import os
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from google.cloud import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GCSIntegration:
    """Class for interacting with Google Cloud Storage."""
    
    def __init__(self, bucket_name: str, credentials_path: str = None):
        """
        Initialize Google Cloud Storage integration.
        
        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to service account credentials JSON file
        """
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Initialized GCS integration for bucket: {bucket_name}")
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files in the bucket with the given prefix.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file names
        """
        logger.info(f"Listing files with prefix: {prefix}")
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]
    
    def download_file(self, source_blob_name: str, destination_file_name: str) -> bool:
        """
        Download a file from GCS to local filesystem.
        
        Args:
            source_blob_name: Path to the file in GCS
            destination_file_name: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading {source_blob_name} to {destination_file_name}")
            blob = self.bucket.blob(source_blob_name)
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
            blob.download_to_filename(destination_file_name)
            return os.path.exists(destination_file_name)
        except Exception as e:
            logger.error(f"Error downloading file {source_blob_name}: {e}")
            return False
    
    def upload_file(self, source_file_name: str, destination_blob_name: str) -> bool:
        """
        Upload a file from local filesystem to GCS.
        
        Args:
            source_file_name: Local path of the file to upload
            destination_blob_name: Path in GCS to store the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Uploading {source_file_name} to {destination_blob_name}")
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            return True
        except Exception as e:
            logger.error(f"Error uploading file {source_file_name}: {e}")
            return False
    
    async def download_files_async(self, file_mappings: List[Dict[str, str]]) -> List[bool]:
        """
        Download multiple files asynchronously.
        
        Args:
            file_mappings: List of dicts with 'source' and 'destination' keys
        
        Returns:
            List of booleans indicating success for each download
        """
        logger.info(f"Downloading {len(file_mappings)} files asynchronously")
        
        async def download_single(source: str, destination: str) -> bool:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self.download_file, source, destination)
        
        tasks = [download_single(
            mapping['source'], mapping['destination']) for mapping in file_mappings]
        return await asyncio.gather(*tasks)
    
    def watch_for_changes(self, callback: Callable[[set, set], None], interval: int = 60):
        """
        Watch for changes in the bucket and call callback when changes are detected.
        
        Args:
            callback: Function to call when changes are detected
            interval: Polling interval in seconds
        """
        logger.info(f"Starting change monitoring with interval {interval}s")
        
        known_files = set(self.list_files())
        
        while True:
            time.sleep(interval)
            current_files = set(self.list_files())
            
            new_files = current_files - known_files
            deleted_files = known_files - current_files
            
            if new_files or deleted_files:
                logger.info(f"Detected changes: {len(new_files)} new files, {len(deleted_files)} deleted files")
                callback(new_files, deleted_files)
                known_files = current_files
    
    def get_file_metadata(self, blob_name: str) -> Dict[str, Any]:
        """
        Get metadata for a file in GCS.
        
        Args:
            blob_name: Path to the file in GCS
            
        Returns:
            Dictionary of metadata
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.reload()
            return {
                'name': blob.name,
                'size': blob.size,
                'updated': blob.updated,
                'content_type': blob.content_type,
                'metadata': blob.metadata or {}
            }
        except Exception as e:
            logger.error(f"Error getting metadata for {blob_name}: {e}")
            return {}
    
    def update_file_metadata(self, blob_name: str, metadata: Dict[str, str]) -> bool:
        """
        Update metadata for a file in GCS.
        
        Args:
            blob_name: Path to the file in GCS
            metadata: Dictionary of metadata to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.metadata = metadata
            blob.patch()
            return True
        except Exception as e:
            logger.error(f"Error updating metadata for {blob_name}: {e}")
            return False
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from GCS.
        
        Args:
            blob_name: Path to the file in GCS
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting file {blob_name}: {e}")
            return False