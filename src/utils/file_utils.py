"""
Utility functions for file operations and system integration.

This module provides helper functions for:
1. File system operations
2. Path handling and normalization
3. File type detection
4. Configuration management
"""

import os
import sys
import logging
import json
import hashlib
import mimetypes
import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, Set
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_file_type(file_path: str) -> str:
    """
    Determine the type of a file based on extension and content.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        str: File type ('pdf', 'excel', 'csv', 'text', 'unknown').
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check extension first
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return 'pdf'
    elif file_ext in ['.xlsx', '.xls', '.xlsm']:
        return 'excel'
    elif file_ext == '.csv':
        return 'csv'
    elif file_ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm']:
        return 'text'
    
    # If extension is not conclusive, check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type:
        if mime_type == 'application/pdf':
            return 'pdf'
        elif 'spreadsheet' in mime_type or 'excel' in mime_type:
            return 'excel'
        elif mime_type == 'text/csv':
            return 'csv'
        elif mime_type.startswith('text/'):
            return 'text'
    
    # If still unknown, check file signature (magic bytes)
    try:
        with open(file_path, 'rb') as f:
            signature = f.read(4)
        
        # PDF signature: %PDF
        if signature.startswith(b'%PDF'):
            return 'pdf'
        
        # Excel signatures
        if signature in [b'PK\x03\x04', b'\xd0\xcf\x11\xe0']:
            return 'excel'
    except:
        pass
    
    return 'unknown'

def normalize_path(path: str) -> str:
    """
    Normalize a file path for cross-platform compatibility.
    
    Args:
        path (str): File path to normalize.
    
    Returns:
        str: Normalized path.
    """
    # Convert to absolute path
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # Normalize path separators
    path = os.path.normpath(path)
    
    return path

def create_directory_if_not_exists(directory_path: str) -> bool:
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to the directory.
    
    Returns:
        bool: True if directory exists or was created, False otherwise.
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False

def get_file_hash(file_path: str) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        str: MD5 hash of the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_md5 = hashlib.md5()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest()

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get metadata for a file.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        Dict[str, Any]: File metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_stat = os.stat(file_path)
    file_path_obj = Path(file_path)
    
    return {
        'file_path': file_path,
        'file_name': file_path_obj.name,
        'file_extension': file_path_obj.suffix.lower(),
        'file_size': file_stat.st_size,
        'file_created': datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
        'file_modified': datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        'file_accessed': datetime.datetime.fromtimestamp(file_stat.st_atime).isoformat(),
        'file_directory': str(file_path_obj.parent),
        'file_type': get_file_type(file_path),
        'file_hash': get_file_hash(file_path)
    }

def list_files_by_type(directory_path: str, file_types: Optional[List[str]] = None, 
                      recursive: bool = True) -> Dict[str, List[str]]:
    """
    List files in a directory, grouped by file type.
    
    Args:
        directory_path (str): Path to the directory.
        file_types (Optional[List[str]]): List of file extensions to include (e.g., ['.pdf', '.xlsx']).
        recursive (bool): Whether to recursively search subdirectories.
    
    Returns:
        Dict[str, List[str]]: Dictionary mapping file types to lists of file paths.
    """
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Directory not found: {directory_path}")
    
    # Default file types if not specified
    if file_types is None:
        file_types = ['.pdf', '.xlsx', '.xls', '.csv', '.txt']
    
    # Convert to lowercase for case-insensitive matching
    file_types = [ft.lower() for ft in file_types]
    
    # Initialize result dictionary
    result = {ft: [] for ft in file_types}
    result['other'] = []
    
    # Walk directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in file_types:
                result[file_ext].append(file_path)
            else:
                result['other'].append(file_path)
        
        # Stop if not recursive
        if not recursive:
            break
    
    return result

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to a JSON file.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary.
        config_path (str): Path to save the configuration file.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # Convert non-serializable objects to strings
        def json_serializer(obj):
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=json_serializer)
        
        logger.info(f"Saved configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_path}: {e}")
        return False

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str): Path to the configuration file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    if not os.path.exists(config_path):
        logger.warning(f"Configuration file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration from {config_path}: {e}")
        return {}
