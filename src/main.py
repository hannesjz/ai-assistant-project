"""
Main application module for the Economic Advisor

This module integrates all components and provides the main application functionality:
1. File discovery and processing
2. Document indexing and search
3. Knowledge integration
4. User interface
"""

import os
import sys
import logging
import json
import argparse
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_extractor.pdf_extractor import PDFExtractor
from src.excel_csv_extractor.excel_csv_extractor import ExcelCSVExtractor
from src.indexing.document_indexer import DocumentIndexer
from src.utils.file_utils import list_files_by_type, get_file_metadata, create_directory_if_not_exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ekonomisk_radgivare.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EkonomiskRadgivare:
    """Main application class for the Economic Advisor."""
    
    def __init__(self, config_path=None):
        """
        Initialize the Economic Advisor.
        
        Args:
            config_path (str): Path to configuration file.
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Create data directory
        data_dir = self.config.get('data_dir', './data')
        create_directory_if_not_exists(data_dir)
        
        # Initialize components
        self.pdf_extractor = PDFExtractor(use_ocr=self.config.get('use_ocr', False))
        self.excel_csv_extractor = ExcelCSVExtractor()
        
        # Initialize indexer
        index_type = self.config.get('index_type', 'sqlite')
        index_path = os.path.join(data_dir, "document_index.db")
        self.indexer = DocumentIndexer(index_type=index_type, db_path=index_path)
        
        logger.info("Initialized Ekonomisk Radgivare")
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file.
        
        Returns:
            dict: Configuration dictionary.
        """
        default_config = {
            'data_dir': './data',
            'index_type': 'sqlite',
            'use_ocr': False,
            'max_files_per_batch': 100,
            'supported_file_types': ['.pdf', '.xlsx', '.xls', '.csv']
        }
        
        if not config_path or not os.path.exists(config_path):
            logger.info("Using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            return default_config
    
    def index_directory(self, directory_path, recursive=True):
        """
        Index all supported files in a directory.
        
        Args:
            directory_path (str): Path to the directory.
            recursive (bool): Whether to recursively index subdirectories.
        
        Returns:
            dict: Statistics about the indexing operation.
        """
        logger.info(f"Indexing directory: {directory_path}")
        
        # List files by type
        supported_types = self.config.get('supported_file_types', ['.pdf', '.xlsx', '.xls', '.csv'])
        files_by_type = list_files_by_type(directory_path, file_types=supported_types, recursive=recursive)
        
        # Batch process files
        max_files = self.config.get('max_files_per_batch', 100)
        
        # Statistics
        stats = {
            'total_files': 0,
            'indexed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'by_type': {}
        }
        
        # Process PDF files
        pdf_files = files_by_type.get('.pdf', [])[:max_files]
        stats['by_type']['.pdf'] = {'total': len(pdf_files), 'success': 0, 'failed': 0}
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Indexing PDF file: {pdf_file}")
                doc_id = self.indexer.index_pdf(pdf_file, self.pdf_extractor)
                stats['indexed_files'] += 1
                stats['by_type']['.pdf']['success'] += 1
            except Exception as e:
                logger.error(f"Failed to index PDF file {pdf_file}: {e}")
                stats['failed_files'] += 1
                stats['by_type']['.pdf']['failed'] += 1
        
        # Process Excel files
        excel_files = []
        for ext in ['.xlsx', '.xls', '.xlsm']:
            excel_files.extend(files_by_type.get(ext, []))
        
        excel_files = excel_files[:max_files]
        stats['by_type']['.excel'] = {'total': len(excel_files), 'success': 0, 'failed': 0}
        
        for excel_file in excel_files:
            try:
                logger.info(f"Indexing Excel file: {excel_file}")
                doc_id = self.indexer.index_excel_csv(excel_file, self.excel_csv_extractor)
                stats['indexed_files'] += 1
                stats['by_type']['.excel']['success'] += 1
            except Exception as e:
                logger.error(f"Failed to index Excel file {excel_file}: {e}")
                stats['failed_files'] += 1
                stats['by_type']['.excel']['failed'] += 1
        
        # Process CSV files
        csv_files = files_by_type.get('.csv', [])[:max_files]
        stats['by_type']['.csv'] = {'total': len(csv_files), 'success': 0, 'failed': 0}
        
        for csv_file in csv_files:
            try:
                logger.info(f"Indexing CSV file: {csv_file}")
                doc_id = self.indexer.index_excel_csv(csv_file, self.excel_csv_extractor)
                stats['indexed_files'] += 1
                stats['by_type']['.csv']['success'] += 1
            except Exception as e:
                logger.error(f"Failed to index CSV file {csv_file}: {e}")
                stats['failed_files'] += 1
                stats['by_type']['.csv']['failed'] += 1
        
        # Update total files
        stats['total_files'] = sum(stats['by_type'][t]['total'] for t in stats['by_type'])
        
        # Get index stats
        index_stats = self.indexer.get_stats()
        stats['index_stats'] = index_stats
        
        logger.info(f"Indexed {stats['indexed_files']} files, failed {stats['failed_files']} files")
        return stats
    
    def search(self, query, filters=None, limit=10):
        """
        Search for documents matching the query.
        
        Args:
            query (str): Search query.
            filters (dict): Metadata filters to apply.
            limit (int): Maximum number of results to return.
        
        Returns:
            list: List of matching documents with metadata.
        """
        logger.info(f"Searching for: {query}")
        return self.indexer.search(query, filters, limit)
    
    def search_structured(self, field_queries, filters=None, limit=10):
        """
        Search for structured documents matching field queries.
        
        Args:
            field_queries (dict): Field-specific queries.
            filters (dict): Metadata filters to apply.
            limit (int): Maximum number of results to return.
        
        Returns:
            list: List of matching documents with metadata.
        """
        logger.info(f"Performing structured search: {field_queries}")
        return self.indexer.search_structured(field_queries, filters, limit)
    
    def get_document(self, doc_id):
        """
        Retrieve a document by ID.
        
        Args:
            doc_id (str): Document ID to retrieve.
        
        Returns:
            dict: Document data if found, None otherwise.
        """
        return self.indexer.get_document(doc_id)
    
    def get_stats(self):
        """
        Get statistics about the index.
        
        Returns:
            dict: Statistics about the index.
        """
        return self.indexer.get_stats()

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Ekonomisk Radgivare - Personal Economic Advisor")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--index", help="Index files in directory")
    parser.add_argument("--search", help="Search for documents")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of search results")
    
    args = parser.parse_args()
    
    # Initialize application
    app = EkonomiskRadgivare(args.config)
    
    # Index directory if specified
    if args.index:
        stats = app.index_directory(args.index)
        print(json.dumps(stats, indent=2, default=str))
    
    # Search if specified
    if args.search:
        results = app.search(args.search, limit=args.limit)
        print(json.dumps(results, indent=2, default=str))
    
    # If no action specified, print stats
    if not args.index and not args.search:
        stats = app.get_stats()
        print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    main()
