"""
Core AI System

This module provides the main AI Assistant class that orchestrates all components
and manages the overall workflow of the system.
"""

import os
import json
import logging
import asyncio
import time
from typing import List, Dict, Any, Optional, Set, Tuple, Callable
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIAssistant:
    """Main AI Assistant class that orchestrates all components."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the AI Assistant.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize components
        self._initialize_components()
        
        logger.info("AI Assistant initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            "data_dir": "./data",
            "models_dir": "./models",
            "db_path": "./data/memory.db",
            "vector_dimension": 768,
            "gcs": {
                "bucket_name": "ai-assistant-documents",
                "credentials_path": None
            },
            "github": {
                "repo_url": None,
                "local_path": "./repo",
                "username": "ai-assistant",
                "email": "ai-assistant@example.com"
            },
            "huggingface": {
                "cache_dir": "./models",
                "device": None,
                "default_models": {
                    "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
                    "classification": "distilbert-base-uncased-finetuned-sst-2-english",
                    "ner": "dslim/bert-base-NER",
                    "qa": "distilbert-base-cased-distilled-squad"
                }
            },
            "document_processing": {
                "use_ocr": True,
                "supported_file_types": [".pdf", ".xlsx", ".xls", ".csv", ".txt", ".docx"]
            }
        }
        
        if not config_path or not os.path.exists(config_path):
            logger.info("Using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults (deep merge)
            merged_config = self._deep_merge(default_config, config)
            
            logger.info(f"Loaded configuration from {config_path}")
            return merged_config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return default_config
    
    def _deep_merge(self, default: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            default: Default dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _initialize_components(self):
        """Initialize all components of the AI Assistant."""
        # Create necessary directories
        os.makedirs(self.config["data_dir"], exist_ok=True)
        os.makedirs(self.config["models_dir"], exist_ok=True)
        
        # Initialize Google Cloud Storage integration
        if self.config["gcs"]["bucket_name"]:
            try:
                from src.ai_assistant.gcs_integration.gcs_client import GCSIntegration
                
                self.gcs = GCSIntegration(
                    bucket_name=self.config["gcs"]["bucket_name"],
                    credentials_path=self.config["gcs"]["credentials_path"]
                )
                logger.info("GCS integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GCS integration: {e}")
                self.gcs = None
        else:
            logger.warning("GCS integration disabled (no bucket name provided)")
            self.gcs = None
        
        # Initialize GitHub integration
        if self.config["github"]["repo_url"]:
            try:
                from src.ai_assistant.github_integration.github_client import GitHubIntegration
                
                self.github = GitHubIntegration(
                    repo_url=self.config["github"]["repo_url"],
                    local_path=self.config["github"]["local_path"],
                    username=self.config["github"]["username"],
                    email=self.config["github"]["email"]
                )
                logger.info("GitHub integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GitHub integration: {e}")
                self.github = None
        else:
            logger.warning("GitHub integration disabled (no repo URL provided)")
            self.github = None
        
        # Initialize Memory Management System
        try:
            from src.ai_assistant.memory_management.memory_system import MemoryManagementSystem
            
            self.memory = MemoryManagementSystem(
                db_path=self.config["db_path"],
                vector_dimension=self.config["vector_dimension"]
            )
            logger.info("Memory Management System initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Memory Management System: {e}")
            raise
        
        # Initialize Hugging Face integration
        try:
            from src.ai_assistant.huggingface_integration.model_client import HuggingFaceIntegration
            
            self.hf = HuggingFaceIntegration(
                cache_dir=self.config["huggingface"]["cache_dir"],
                device=self.config["huggingface"]["device"]
            )
            logger.info("Hugging Face integration initialized")
            
            # Load default models if specified
            default_models = self.config["huggingface"]["default_models"]
            for task, model_name in default_models.items():
                try:
                    self.hf.load_model(task, model_name)
                    logger.info(f"Loaded default model for {task}: {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to load default model for {task}: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face integration: {e}")
            self.hf = None
    
    def process_document(self, document_path: str) -> Optional[str]:
        """
        Process a document and store it in memory.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            logger.info(f"Processing document: {document_path}")
            
            # Extract text from document
            text, metadata = self._extract_text_and_metadata(document_path)
            
            if not text:
                logger.warning(f"No text extracted from document: {document_path}")
                return None
            
            # Generate document ID
            import uuid
            document_id = str(uuid.uuid4())
            
            # Extract title from metadata or filename
            title = metadata.get('title', os.path.basename(document_path))
            
            # Determine document type from file extension
            document_type = os.path.splitext(document_path)[1].lower()
            
            # Store document in memory
            success = self.memory.store_document(
                document_id=document_id,
                source_path=document_path,
                document_type=document_type,
                title=title,
                content=text,
                metadata=metadata
            )
            
            if not success:
                logger.error(f"Failed to store document in memory: {document_path}")
                return None
            
            # Generate and store document vector if Hugging Face is available
            if self.hf:
                try:
                    # Generate embedding
                    vector = self.hf.get_embeddings(text)
                    
                    # Store vector
                    self.memory.store_document_vector(document_id, vector[0])
                    
                    logger.info(f"Stored vector for document: {document_id}")
                except Exception as e:
                    logger.error(f"Failed to generate and store vector: {e}")
            
            logger.info(f"Document processed successfully: {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Error processing document {document_path}: {e}")
            return None
    
    def _extract_text_and_metadata(self, document_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Tuple of (text, metadata)
        """
        # Get file extension
        ext = os.path.splitext(document_path)[1].lower()
        
        # Extract text based on file type
        if ext == '.pdf':
            return self._extract_from_pdf(document_path)
        elif ext in ['.xlsx', '.xls', '.csv']:
            return self._extract_from_tabular(document_path)
        elif ext in ['.txt', '.md']:
            return self._extract_from_text(document_path)
        elif ext == '.docx':
            return self._extract_from_docx(document_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return "", {}
    
    def _extract_from_pdf(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from PDF."""
        try:
            # Use existing PDF extractor if available
            try:
                from src.pdf_extractor.enhanced_pdf_extractor import extract_text_from_pdf
                text = extract_text_from_pdf(pdf_path, use_ocr=self.config["document_processing"]["use_ocr"])
            except ImportError:
                # Fallback to simple extraction
                import subprocess
                with open(os.devnull, 'w') as devnull:
                    text = subprocess.check_output(['pdftotext', pdf_path, '-'], stderr=devnull).decode('utf-8')
            
            # Extract metadata
            metadata = {
                'title': os.path.basename(pdf_path),
                'pages': 0,  # Would need PyPDF2 to get actual page count
                'file_size': os.path.getsize(pdf_path)
            }
            
            return text, metadata
        except Exception as e:
            logger.error(f"Error extracting from PDF {pdf_path}: {e}")
            return "", {}
    
    def _extract_from_tabular(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from Excel/CSV."""
        try:
            import pandas as pd
            
            # Read file
            df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
            
            # Convert to string representation
            text = df.to_string()
            
            # Extract metadata
            metadata = {
                'title': os.path.basename(file_path),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'file_size': os.path.getsize(file_path)
            }
            
            return text, metadata
        except Exception as e:
            logger.error(f"Error extracting from tabular file {file_path}: {e}")
            return "", {}
    
    def _extract_from_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract metadata
            metadata = {
                'title': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'lines': text.count('\n') + 1
            }
            
            return text, metadata
        except Exception as e:
            logger.error(f"Error extracting from text file {file_path}: {e}")
            return "", {}
    
    def _extract_from_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text and metadata from DOCX."""
        try:
            import docx
            
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            # Extract metadata
            metadata = {
                'title': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'paragraphs': len(doc.paragraphs)
            }
            
            return text, metadata
        except Exception as e:
            logger.error(f"Error extracting from DOCX {file_path}: {e}")
            return "", {}
    
    def process_documents_from_gcs(self, prefix: str = "", local_dir: str = "./temp") -> List[str]:
        """
        Process documents from Google Cloud Storage.
        
        Args:
            prefix: Prefix for files in GCS
            local_dir: Local directory to download files to
            
        Returns:
            List of processed document IDs
        """
        if not self.gcs:
            logger.error("GCS integration not initialized")
            return []
        
        try:
            # Create local directory
            os.makedirs(local_dir, exist_ok=True)
            
            # List files in GCS
            files = self.gcs.list_files(prefix)
            
            if not files:
                logger.info(f"No files found in GCS with prefix: {prefix}")
                return []
            
            logger.info(f"Found {len(files)} files in GCS with prefix: {prefix}")
            
            # Download and process each file
            document_ids = []
            for file_path in files:
                # Skip directories
                if file_path.endswith('/'):
                    continue
                
                # Check if file type is supported
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in self.config["document_processing"]["supported_file_types"]:
                    logger.info(f"Skipping unsupported file type: {file_path}")
                    continue
                
                # Download file
                local_path = os.path.join(local_dir, os.path.basename(file_path))
                success = self.gcs.download_file(file_path, local_path)
                
                if not success:
                    logger.error(f"Failed to download file: {file_path}")
                    continue
                
                # Process document
                document_id = self.process_document(local_path)
                
                if document_id:
                    document_ids.append(document_id)
                
                # Clean up local file
                os.remove(local_path)
            
            logger.info(f"Processed {len(document_ids)} documents from GCS")
            return document_ids
        except Exception as e:
            logger.error(f"Error processing documents from GCS: {e}")
            return []
    
    def watch_gcs_for_changes(self, prefix: str = "", interval: int = 60):
        """
        Watch GCS for changes and process new documents.
        
        Args:
            prefix: Prefix for files in GCS
            interval: Polling interval in seconds
        """
        if not self.gcs:
            logger.error("GCS integration not initialized")
            return
        
        def handle_changes(new_files: Set[str], deleted_files: Set[str]):
            """Handle changes in GCS."""
            # Process new files
            if new_files:
                logger.info(f"Processing {len(new_files)} new files")
                
                temp_dir = os.path.join(self.config["data_dir"], "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                for file_path in new_files:
                    # Skip directories
                    if file_path.endswith('/'):
                        continue
                    
                    # Check if file type is supported
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext not in self.config["document_processing"]["supported_file_types"]:
                        logger.info(f"Skipping unsupported file type: {file_path}")
                        continue
                    
                    # Download and process file
                    local_path = os.path.join(temp_dir, os.path.basename(file_path))
                    success = self.gcs.download_file(file_path, local_path)
                    
                    if success:
                        self.process_document(local_path)
                        os.remove(local_path)
        
        # Start watching for changes
        logger.info(f"Watching GCS for changes with prefix: {prefix}")
        self.gcs.watch_for_changes(handle_changes, interval)
    
    def search_documents(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        try:
            # Generate query vector if Hugging Face is available
            if self.hf:
                try:
                    # Generate embedding
                    query_vector = self.hf.get_embeddings(query)[0]
                    
                    # Search using vector
                    results = self.memory.search_documents(query_vector, top_k)
                    
                    # Get full documents
                    documents = []
                    for doc_id, score in results:
                        doc = self.memory.get_document(doc_id)
                        if doc:
                            doc['similarity_score'] = score
                            documents.append(doc)
                    
                    logger.info(f"Found {len(documents)} documents matching query: {query}")
                    return documents
                except Exception as e:
                    logger.error(f"Error searching with vector: {e}")
            
            # Fallback to simple text search
            logger.warning("Vector search not available, using simple text search")
            # This would require implementing a text search method in the memory system
            return []
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question based on stored documents.
        
        Args:
            question: Question to answer
            
        Returns:
            Answer with supporting documents
        """
        try:
            # Search for relevant documents
            documents = self.search_documents(question, top_k=5)
            
            if not documents:
                return {
                    'answer': "I don't have enough information to answer that question.",
                    'confidence': 0.0,
                    'sources': []
                }
            
            # Extract contexts from documents
            contexts = [doc['content'][:1000] for doc in documents]
            
            # Use Hugging Face QA model to answer the question
            if self.hf:
                try:
                    # Combine contexts
                    combined_context = " ".join(contexts)
                    
                    # Get answer
                    result = self.hf.answer_question(question, combined_context)
                    
                    return {
                        'answer': result['answer'],
                        'confidence': result['score'],
                        'sources': [{'document_id': doc['document_id'], 'title': doc['title']} for doc in documents]
                    }
                except Exception as e:
                    logger.error(f"Error answering question with Hugging Face: {e}")
            
            # Fallback to simple answer
            return {
                'answer': "I found some relevant documents, but I'm not able to generate a specific answer.",
                'confidence': 0.0,
                'sources': [{'document_id': doc['document_id'], 'title': doc['title']} for doc in documents]
            }
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': "An error occurred while trying to answer the question.",
                'confidence': 0.0,
                'sources': []
            }
    
    def update_code_in_github(self, file_path: str, content: str, commit_message: str = None) -> bool:
        """
        Update code in GitHub repository.
        
        Args:
            file_path: Path to the file in the repository
            content: New content for the file
            commit_message: Commit message (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.github:
            logger.error("GitHub integration not initialized")
            return False
        
        try:
            # Pull latest changes
            self.github.pull_changes()
            
            # Write file
            full_path = os.path.join(self.github.local_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Stage file
            self.github.stage_file(file_path)
            
            # Commit and push
            if not commit_message:
                commit_message = f"Update {file_path}"
            
            commit = self.github.commit_changes(commit_message)
            if commit:
                self.github.push_changes()
                logger.info(f"Successfully updated {file_path} in GitHub")
                return True
            else:
                logger.warning(f"No changes to commit for {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error updating code in GitHub: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the AI Assistant system.
        
        Returns:
            Dictionary of statistics
        """
        stats = {
            'memory': self.memory.get_stats() if hasattr(self, 'memory') else {},
            'components': {
                'gcs': self.gcs is not None,
                'github': self.github is not None,
                'huggingface': self.hf is not None
            }
        }
        
        # Add GitHub stats if available
        if self.github:
            try:
                stats['github'] = {
                    'repo_url': self.github.repo_url,
                    'has_changes': self.github.has_changes(),
                    'recent_commits': self.github.get_commit_history(5)
                }
            except Exception as e:
                logger.error(f"Error getting GitHub stats: {e}")
        
        # Add Hugging Face stats if available
        if self.hf:
            try:
                stats['huggingface'] = {
                    'device': self.hf.device,
                    'loaded_models': list(self.hf.models.keys())
                }
            except Exception as e:
                logger.error(f"Error getting Hugging Face stats: {e}")
        
        return stats