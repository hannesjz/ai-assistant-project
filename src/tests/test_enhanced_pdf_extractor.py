"""
Test script for the enhanced PDF extractor with OCR and metadata extraction.

This script tests the functionality of the enhanced PDF extractor by:
1. Testing text extraction from a regular PDF
2. Testing text extraction from a scanned PDF (if available)
3. Testing metadata extraction from different document types
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.pdf_extractor.enhanced_pdf_extractor import PDFExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pdf_extraction(pdf_path, use_ocr=True):
    """
    Test PDF text extraction and metadata extraction.
    
    Args:
        pdf_path (str): Path to the PDF file to test
        use_ocr (bool): Whether to use OCR for text extraction
    """
    logger.info(f"Testing PDF extraction on: {pdf_path}")
    
    # Initialize the PDF extractor
    extractor = PDFExtractor(use_ocr=use_ocr)
    
    # Extract text and metadata
    text, metadata = extractor.extract_text(pdf_path)
    
    # Print results
    logger.info(f"Extracted {len(text)} characters of text")
    logger.info(f"Document type: {metadata.get('document_type', 'unknown')}")
    
    # Print metadata
    logger.info("Extracted metadata:")
    for key, value in metadata.items():
        logger.info(f"  {key}: {value}")
    
    # Save extracted text to file
    output_path = f"{pdf_path}.test.txt"
    with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(text)
    
    logger.info(f"Saved extracted text to {output_path}")
    
    return text, metadata

def test_document_type_detection(pdf_paths):
    """
    Test document type detection on multiple PDFs.
    
    Args:
        pdf_paths (list): List of paths to PDF files
    """
    logger.info("Testing document type detection")
    
    # Initialize the PDF extractor
    extractor = PDFExtractor(use_ocr=False)  # Disable OCR for faster testing
    
    results = {}
    
    for pdf_path in pdf_paths:
        try:
            # Extract just enough text for document type detection
            with open(pdf_path, 'rb') as f:
                import PyPDF2
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()
                else:
                    text = ""
            
            # Determine document type
            doc_type = extractor._determine_document_type(text, pdf_path)
            
            # Store result
            results[pdf_path] = doc_type
            logger.info(f"{os.path.basename(pdf_path)}: {doc_type}")
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
    
    # Count document types
    type_counts = {}
    for doc_type in results.values():
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    logger.info("Document type counts:")
    for doc_type, count in type_counts.items():
        logger.info(f"  {doc_type}: {count}")
    
    return results

def test_metadata_extraction(pdf_path):
    """
    Test detailed metadata extraction from a specific PDF.
    
    Args:
        pdf_path (str): Path to the PDF file to test
    """
    logger.info(f"Testing metadata extraction on: {pdf_path}")
    
    # Initialize the PDF extractor
    extractor = PDFExtractor(use_ocr=True)
    
    # Extract text and metadata
    text, metadata = extractor.extract_text(pdf_path)
    
    # Print all metadata
    logger.info("Extracted metadata:")
    for key, value in metadata.items():
        logger.info(f"  {key}: {value}")
    
    # Test specific metadata extraction based on document type
    doc_type = metadata.get('document_type', 'unknown')
    
    if doc_type == 'invoice':
        logger.info("Testing invoice-specific metadata:")
        invoice_fields = ['invoice_number', 'total_amount', 'vat_amount', 'supplier', 'due_date']
        for field in invoice_fields:
            logger.info(f"  {field}: {metadata.get(field, 'Not found')}")
    
    elif doc_type == 'receipt':
        logger.info("Testing receipt-specific metadata:")
        receipt_fields = ['receipt_number', 'total_amount', 'store', 'payment_method']
        for field in receipt_fields:
            logger.info(f"  {field}: {metadata.get(field, 'Not found')}")
    
    return metadata

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Enhanced PDF Extractor")
    parser.add_argument("--pdf", help="Path to a PDF file to test")
    parser.add_argument("--dir", help="Directory containing PDF files to test")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR")
    parser.add_argument("--test-types", action="store_true", help="Test document type detection")
    parser.add_argument("--test-metadata", action="store_true", help="Test detailed metadata extraction")
    
    args = parser.parse_args()
    
    # Test a single PDF file
    if args.pdf:
        if not os.path.exists(args.pdf):
            logger.error(f"PDF file not found: {args.pdf}")
            return
        
        use_ocr = not args.no_ocr
        
        if args.test_metadata:
            test_metadata_extraction(args.pdf)
        else:
            test_pdf_extraction(args.pdf, use_ocr)
    
    # Test multiple PDF files in a directory
    elif args.dir:
        if not os.path.exists(args.dir):
            logger.error(f"Directory not found: {args.dir}")
            return
        
        # Find all PDF files in the directory
        pdf_files = []
        for root, _, files in os.walk(args.dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {args.dir}")
        
        if args.test_types:
            # Test document type detection
            test_document_type_detection(pdf_files)
        else:
            # Test the first few PDFs
            max_files = 5
            for pdf_file in pdf_files[:max_files]:
                use_ocr = not args.no_ocr
                test_pdf_extraction(pdf_file, use_ocr)
            
            if len(pdf_files) > max_files:
                logger.info(f"Tested {max_files} out of {len(pdf_files)} PDF files")
    
    else:
        logger.error("Please specify either --pdf or --dir")

if __name__ == "__main__":
    main()