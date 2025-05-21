"""
Integration Test Script for File Processing

This script tests the complete file integration pipeline:
1. File discovery and classification
2. Text extraction from PDF files
3. Data extraction from Excel and CSV files
4. Document indexing and search
"""

import os
import sys
import logging
import json
import datetime
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
        logging.FileHandler("file_integration_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_file_integration(directory_path, output_dir, max_files_per_type=5):
    """
    Test the complete file integration pipeline.
    
    Args:
        directory_path (str): Path to the directory containing files to process.
        output_dir (str): Directory to save test results.
        max_files_per_type (int): Maximum number of files to process per type.
    
    Returns:
        dict: Test results summary.
    """
    logger.info(f"Starting file integration test on directory: {directory_path}")
    
    # Create output directory
    create_directory_if_not_exists(output_dir)
    
    # Initialize extractors
    pdf_extractor = PDFExtractor(use_ocr=False)
    excel_csv_extractor = ExcelCSVExtractor()
    
    # Initialize indexer (in-memory for testing)
    index_path = os.path.join(output_dir, "document_index.db")
    indexer = DocumentIndexer(index_type="sqlite", db_path=index_path)
    
    # List files by type
    try:
        files_by_type = list_files_by_type(directory_path, recursive=True)
        logger.info(f"Found files: {json.dumps({k: len(v) for k, v in files_by_type.items()})}")
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return {"error": str(e)}
    
    # Test results
    results = {
        "pdf_extraction": [],
        "excel_extraction": [],
        "csv_extraction": [],
        "indexing": [],
        "search": []
    }
    
    # Process PDF files
    pdf_files = files_by_type.get('.pdf', [])[:max_files_per_type]
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing PDF file: {pdf_file}")
            
            # Extract text
            text = pdf_extractor.extract_text(pdf_file)
            text_length = len(text)
            
            # Extract metadata
            metadata = pdf_extractor.extract_metadata(pdf_file)
            
            # Index document
            doc_id = indexer.index_pdf(pdf_file, pdf_extractor)
            
            results["pdf_extraction"].append({
                "file": pdf_file,
                "text_length": text_length,
                "metadata": metadata,
                "doc_id": doc_id,
                "success": True
            })
            
            logger.info(f"Successfully processed PDF file: {pdf_file}")
        except Exception as e:
            logger.error(f"Failed to process PDF file {pdf_file}: {e}")
            results["pdf_extraction"].append({
                "file": pdf_file,
                "error": str(e),
                "success": False
            })
    
    # Process Excel files
    excel_files = files_by_type.get('.xlsx', []) + files_by_type.get('.xls', [])
    excel_files = excel_files[:max_files_per_type]
    
    for excel_file in excel_files:
        try:
            logger.info(f"Processing Excel file: {excel_file}")
            
            # Extract data
            data = excel_csv_extractor.extract_from_excel(excel_file)
            
            # Get metadata
            metadata = excel_csv_extractor.get_excel_metadata(excel_file)
            
            # Index document
            doc_id = indexer.index_excel_csv(excel_file, excel_csv_extractor)
            
            results["excel_extraction"].append({
                "file": excel_file,
                "sheet_count": len(data),
                "metadata": metadata,
                "doc_id": doc_id,
                "success": True
            })
            
            logger.info(f"Successfully processed Excel file: {excel_file}")
        except Exception as e:
            logger.error(f"Failed to process Excel file {excel_file}: {e}")
            results["excel_extraction"].append({
                "file": excel_file,
                "error": str(e),
                "success": False
            })
    
    # Process CSV files
    csv_files = files_by_type.get('.csv', [])[:max_files_per_type]
    
    for csv_file in csv_files:
        try:
            logger.info(f"Processing CSV file: {csv_file}")
            
            # Extract data
            data = excel_csv_extractor.extract_from_csv(csv_file)
            
            # Get metadata
            metadata = excel_csv_extractor.get_csv_metadata(csv_file)
            
            # Index document
            doc_id = indexer.index_excel_csv(csv_file, excel_csv_extractor)
            
            results["csv_extraction"].append({
                "file": csv_file,
                "row_count": len(data),
                "column_count": len(data.columns),
                "metadata": metadata,
                "doc_id": doc_id,
                "success": True
            })
            
            logger.info(f"Successfully processed CSV file: {csv_file}")
        except Exception as e:
            logger.error(f"Failed to process CSV file {csv_file}: {e}")
            results["csv_extraction"].append({
                "file": csv_file,
                "error": str(e),
                "success": False
            })
    
    # Test search functionality
    try:
        logger.info("Testing search functionality")
        
        # Get index stats
        index_stats = indexer.get_stats()
        results["indexing"] = index_stats
        
        # Perform some test searches
        search_queries = [
            "faktura",
            "belopp",
            "moms",
            "datum",
            "kvitto"
        ]
        
        for query in search_queries:
            search_results = indexer.search(query, limit=5)
            results["search"].append({
                "query": query,
                "result_count": len(search_results),
                "results": search_results
            })
        
        logger.info("Successfully tested search functionality")
    except Exception as e:
        logger.error(f"Failed to test search functionality: {e}")
        results["search"].append({
            "error": str(e)
        })
    
    # Save results to file
    result_file = os.path.join(output_dir, "integration_test_results.json")
    try:
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Saved test results to {result_file}")
    except Exception as e:
        logger.error(f"Failed to save test results: {e}")
    
    # Generate summary
    summary = {
        "pdf_files_processed": len(results["pdf_extraction"]),
        "pdf_success_rate": sum(1 for r in results["pdf_extraction"] if r.get("success", False)) / max(1, len(results["pdf_extraction"])),
        "excel_files_processed": len(results["excel_extraction"]),
        "excel_success_rate": sum(1 for r in results["excel_extraction"] if r.get("success", False)) / max(1, len(results["excel_extraction"])),
        "csv_files_processed": len(results["csv_extraction"]),
        "csv_success_rate": sum(1 for r in results["csv_extraction"] if r.get("success", False)) / max(1, len(results["csv_extraction"])),
        "total_documents_indexed": index_stats.get("document_count", 0) + index_stats.get("structured_document_count", 0),
        "search_queries_tested": len(results["search"]),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Save summary to file
    summary_file = os.path.join(output_dir, "integration_test_summary.json")
    try:
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved test summary to {summary_file}")
    except Exception as e:
        logger.error(f"Failed to save test summary: {e}")
    
    logger.info("File integration test completed")
    return summary

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Test file integration pipeline")
    parser.add_argument("directory", help="Directory containing files to process")
    parser.add_argument("--output", default="./test_results", help="Directory to save test results")
    parser.add_argument("--max-files", type=int, default=5, help="Maximum number of files to process per type")
    
    args = parser.parse_args()
    
    # Run test
    test_file_integration(args.directory, args.output, args.max_files)
