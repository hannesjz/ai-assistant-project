#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
End-to-End Test for AI Assistant

This script tests the complete workflow of the AI Assistant:
1. GCS integration
2. Document processing
3. Memory management
4. GitHub integration
5. Hugging Face model integration
"""

import os
import sys
import logging
import argparse
import json
import tempfile
import shutil
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai_assistant.core.ai_assistant import AIAssistant
from src.ai_assistant.gcs_integration.gcs_client import GCSIntegration
from src.ai_assistant.github_integration.github_client import GitHubIntegration
from src.ai_assistant.memory_management.memory_system import MemoryManagementSystem
from src.ai_assistant.huggingface_integration.model_client import HuggingFaceIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_e2e.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestAIAssistant(unittest.TestCase):
    """Test cases for AI Assistant end-to-end functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create temporary directories
        cls.temp_dir = tempfile.mkdtemp()
        cls.data_dir = os.path.join(cls.temp_dir, "data")
        cls.models_dir = os.path.join(cls.temp_dir, "models")
        cls.db_path = os.path.join(cls.temp_dir, "memory.db")
        cls.gcs_cache_dir = os.path.join(cls.temp_dir, "gcs_cache")
        cls.github_repo_dir = os.path.join(cls.temp_dir, "github_repo")
        
        os.makedirs(cls.data_dir, exist_ok=True)
        os.makedirs(cls.models_dir, exist_ok=True)
        os.makedirs(cls.gcs_cache_dir, exist_ok=True)
        os.makedirs(cls.github_repo_dir, exist_ok=True)
        
        # Create test config
        cls.config = {
            "data_dir": cls.data_dir,
            "models_dir": cls.models_dir,
            "db_path": cls.db_path,
            "vector_dimension": 768,
            "gcs": {
                "bucket_name": "test-bucket",
                "credentials_path": None,
                "local_cache_dir": cls.gcs_cache_dir
            },
            "github": {
                "repo_url": "https://github.com/test/test-repo.git",
                "local_path": cls.github_repo_dir,
                "username": "test-user",
                "email": "test@example.com",
                "auto_commit_interval_minutes": 30
            },
            "memory": {
                "db_path": cls.db_path,
                "vector_dimension": 768,
                "max_documents": 10000
            },
            "huggingface": {
                "cache_dir": cls.models_dir,
                "device": "cpu",
                "multi_gpu": False
            },
            "document_processing": {
                "use_ocr": True,
                "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv", ".txt", ".docx"]
            }
        }
        
        # Write test config to file
        with open(os.path.join(cls.temp_dir, "test_config.json"), "w") as f:
            json.dump(cls.config, f, indent=2)
        
        # Create test files
        cls.test_txt_file = os.path.join(cls.data_dir, "test.txt")
        with open(cls.test_txt_file, "w") as f:
            f.write("This is a test document for the AI Assistant.")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.temp_dir)
    
    @patch("src.ai_assistant.gcs_integration.gcs_client.storage.Client")
    @patch("src.ai_assistant.github_integration.github_client.git.Repo")
    def test_initialization(self, mock_git_repo, mock_storage_client):
        """Test initialization of AI Assistant."""
        # Mock GCS bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Mock Git repo
        mock_repo = MagicMock()
        mock_git_repo.return_value = mock_repo
        
        # Initialize AI Assistant
        config_path = os.path.join(self.temp_dir, "test_config.json")
        assistant = AIAssistant(config_path)
        
        # Verify components are initialized
        self.assertIsNotNone(assistant.memory)
        self.assertIsNotNone(assistant.gcs)
        self.assertIsNotNone(assistant.github)
        
        # Verify config is loaded
        self.assertEqual(assistant.config["data_dir"], self.data_dir)
        self.assertEqual(assistant.config["db_path"], self.db_path)
    
    @patch("src.ai_assistant.gcs_integration.gcs_client.storage.Client")
    @patch("src.ai_assistant.github_integration.github_client.git.Repo")
    def test_document_processing(self, mock_git_repo, mock_storage_client):
        """Test document processing functionality."""
        # Mock GCS bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Mock Git repo
        mock_repo = MagicMock()
        mock_git_repo.return_value = mock_repo
        
        # Initialize AI Assistant
        config_path = os.path.join(self.temp_dir, "test_config.json")
        assistant = AIAssistant(config_path)
        
        # Process test document
        document_id = assistant.process_document(self.test_txt_file)
        
        # Verify document was processed
        self.assertIsNotNone(document_id)
        
        # Verify document is in memory
        document = assistant.memory.get_document(document_id)
        self.assertIsNotNone(document)
        self.assertEqual(document["title"], "test.txt")
        self.assertEqual(document["document_type"], ".txt")
        self.assertIn("This is a test document", document["content"])
    
    @patch("src.ai_assistant.gcs_integration.gcs_client.storage.Client")
    @patch("src.ai_assistant.github_integration.github_client.git.Repo")
    @patch("src.ai_assistant.huggingface_integration.model_client.pipeline")
    def test_search_functionality(self, mock_pipeline, mock_git_repo, mock_storage_client):
        """Test search functionality."""
        # Mock GCS bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Mock Git repo
        mock_repo = MagicMock()
        mock_git_repo.return_value = mock_repo
        
        # Mock Hugging Face pipeline
        mock_pipeline.return_value = MagicMock()
        
        # Initialize AI Assistant
        config_path = os.path.join(self.temp_dir, "test_config.json")
        assistant = AIAssistant(config_path)
        
        # Process test document
        document_id = assistant.process_document(self.test_txt_file)
        
        # Mock vector for search
        import numpy as np
        mock_vector = np.random.rand(768)
        
        # Mock get_embeddings to return the vector
        assistant.hf = MagicMock()
        assistant.hf.get_embeddings.return_value = np.array([mock_vector])
        
        # Mock search_documents to return the document
        assistant.memory.search_documents = MagicMock()
        assistant.memory.search_documents.return_value = [(document_id, 0.95)]
        
        # Search for document
        results = assistant.search_documents("test document")
        
        # Verify search results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["document_id"], document_id)
    
    @patch("src.ai_assistant.gcs_integration.gcs_client.storage.Client")
    @patch("src.ai_assistant.github_integration.github_client.git.Repo")
    def test_github_integration(self, mock_git_repo, mock_storage_client):
        """Test GitHub integration."""
        # Mock GCS bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Mock Git repo
        mock_repo = MagicMock()
        mock_git_repo.return_value = mock_repo
        
        # Initialize AI Assistant
        config_path = os.path.join(self.temp_dir, "test_config.json")
        assistant = AIAssistant(config_path)
        
        # Mock GitHub operations
        assistant.github.pull_changes = MagicMock()
        assistant.github.stage_file = MagicMock()
        assistant.github.commit_changes = MagicMock()
        assistant.github.commit_changes.return_value = MagicMock()
        assistant.github.push_changes = MagicMock()
        
        # Update code in GitHub
        result = assistant.update_code_in_github("test.py", "print('Hello, World!')", "Add test.py")
        
        # Verify GitHub operations
        self.assertTrue(result)
        assistant.github.pull_changes.assert_called_once()
        assistant.github.stage_file.assert_called_once()
        assistant.github.commit_changes.assert_called_once()
        assistant.github.push_changes.assert_called_once()
    
    @patch("src.ai_assistant.gcs_integration.gcs_client.storage.Client")
    @patch("src.ai_assistant.github_integration.github_client.git.Repo")
    def test_gcs_integration(self, mock_git_repo, mock_storage_client):
        """Test GCS integration."""
        # Mock GCS bucket and blobs
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Mock list_blobs to return a test file
        mock_blob_list = [MagicMock()]
        mock_blob_list[0].name = "test.txt"
        mock_storage_client.return_value.list_blobs.return_value = mock_blob_list
        
        # Mock Git repo
        mock_repo = MagicMock()
        mock_git_repo.return_value = mock_repo
        
        # Initialize AI Assistant
        config_path = os.path.join(self.temp_dir, "test_config.json")
        assistant = AIAssistant(config_path)
        
        # Mock download_file to create a test file
        def mock_download_file(source, dest):
            with open(dest, "w") as f:
                f.write("This is a test document from GCS.")
            return True
        
        assistant.gcs.download_file = mock_download_file
        
        # Process documents from GCS
        document_ids = assistant.process_documents_from_gcs("", os.path.join(self.temp_dir, "gcs_files"))
        
        # Verify documents were processed
        self.assertEqual(len(document_ids), 1)

def main():
    """Run the end-to-end tests."""
    unittest.main()

if __name__ == "__main__":
    main()