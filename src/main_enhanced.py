"""
Enhanced Main Application for Ekonomisk Rådgivare

This version includes:
1. OCR for scanned documents
2. Metadata extraction
3. Improved search functionality
4. Basic data analysis
"""

import os
import sys
import json
import logging
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

# Import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdf_extractor.enhanced_pdf_extractor import PDFExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def list_files(directory, extensions=None):
    """List files in a directory with specific file extensions."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if extensions is None or any(filename.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files

def extract_csv_data(csv_path):
    """Extract data from CSV file."""
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error extracting data from CSV: {e}")
        return []

def search_documents(query, data_dir, fuzzy=True, metadata_filter=None):
    """
    Search in documents with support for fuzzy search and metadata filtering.
    
    Args:
        query (str): Search query
        data_dir (str): Directory containing indexed data
        fuzzy (bool): Whether to use fuzzy matching
        metadata_filter (dict): Filters to apply on metadata
        
    Returns:
        list: List of matching documents with relevance scores
    """
    import os
    from difflib import SequenceMatcher
    
    # Read extracted text files
    text_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    # Read metadata if available
    metadata_file = os.path.join(data_dir, "metadata.json")
    metadata = {}
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except:
            logger.warning(f"Could not read metadata from {metadata_file}")
    
    # Apply metadata filters if specified
    filtered_files = text_files
    if metadata_filter and metadata:
        filtered_files = []
        for file_path in text_files:
            file_id = os.path.basename(file_path)
            if file_id in metadata:
                file_metadata = metadata[file_id]
                include = True
                for key, value in metadata_filter.items():
                    if key not in file_metadata or file_metadata[key] != value:
                        include = False
                        break
                if include:
                    filtered_files.append(file_path)
    
    # Search in text files
    matches = []
    for text_file in filtered_files:
        try:
            with open(text_file, 'r', errors='ignore') as f:
                content = f.read().lower()
            
            # Get file metadata
            file_id = os.path.basename(text_file)
            file_metadata = metadata.get(file_id, {})
            
            # Exact search
            if query.lower() in content:
                # Count occurrences for relevance
                count = content.count(query.lower())
                matches.append((text_file, 1.0 + (count * 0.01), file_metadata))
            # Fuzzy search
            elif fuzzy:
                # Split content into words
                words = content.split()
                
                # Calculate best match for each word
                best_match = 0
                for word in words:
                    similarity = SequenceMatcher(None, query.lower(), word).ratio()
                    if similarity > best_match:
                        best_match = similarity
                
                # If match is good enough, add to results
                if best_match > 0.8:
                    matches.append((text_file, best_match, file_metadata))
        except Exception as e:
            logger.error(f"Error searching in {text_file}: {e}")
    
    # Sort by relevance
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches

def analyze_documents(data_dir, document_type=None):
    """
    Analyze documents and extract insights.
    
    Args:
        data_dir (str): Directory containing indexed data
        document_type (str): Type of documents to analyze (invoice, receipt, etc.)
        
    Returns:
        dict: Analysis results
    """
    # Read metadata
    metadata_file = os.path.join(data_dir, "metadata.json")
    if not os.path.exists(metadata_file):
        logger.error(f"Metadata file not found: {metadata_file}")
        return {}
    
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        logger.error(f"Error reading metadata: {e}")
        return {}
    
    # Filter by document type if specified
    if document_type:
        filtered_metadata = {k: v for k, v in metadata.items()
                            if v.get('document_type') == document_type}
    else:
        filtered_metadata = metadata
    
    if not filtered_metadata:
        logger.warning(f"No documents found with type: {document_type}")
        return {}
    
    # Extract data for analysis
    dates = []
    amounts = []
    suppliers = set()
    
    for doc_id, doc_metadata in filtered_metadata.items():
        if 'date' in doc_metadata:
            try:
                # Convert date string to datetime object
                date_str = doc_metadata['date']
                # Handle different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d.%m.%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        dates.append(date_obj)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Could not parse date: {doc_metadata['date']}")
        
        if 'total_amount' in doc_metadata:
            amounts.append(doc_metadata['total_amount'])
        
        if 'supplier' in doc_metadata:
            suppliers.add(doc_metadata['supplier'])
    
    # Perform analysis
    analysis = {
        'document_count': len(filtered_metadata),
        'suppliers': list(suppliers),
        'supplier_count': len(suppliers),
    }
    
    if amounts:
        analysis['total_amount'] = sum(amounts)
        analysis['average_amount'] = sum(amounts) / len(amounts)
        analysis['min_amount'] = min(amounts)
        analysis['max_amount'] = max(amounts)
    
    if dates:
        analysis['date_range'] = {
            'earliest': min(dates).strftime('%Y-%m-%d'),
            'latest': max(dates).strftime('%Y-%m-%d')
        }
    
    return analysis


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Ekonomisk Rådgivare - Enhanced Version")
    parser.add_argument("--index", help="Index files in directory")
    parser.add_argument("--search", help="Search for documents")
    parser.add_argument("--fuzzy", action="store_true", help="Use fuzzy search")
    parser.add_argument("--analyze", action="store_true", help="Analyze documents")
    parser.add_argument("--type", help="Filter by document type (invoice, receipt, etc.)")
    
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    data_dir = "./data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Index directory if specified
    if args.index:
        if not os.path.exists(args.index):
            logger.error(f"Directory {args.index} does not exist")
            return
        
        extensions = [".pdf", ".csv", ".md", ".txt"]
        files = list_files(args.index, extensions)
        
        logger.info(f"Found {len(files)} files with extensions {', '.join(extensions)}")
        
        # Show first 10 files
        for i, file in enumerate(files[:10]):
            logger.info(f"  {i+1}. {file}")
        
        if len(files) > 10:
            logger.info(f"  ... and {len(files) - 10} more")
        
        # Extract text and metadata from PDF files
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        logger.info(f"Extracting text from {len(pdf_files)} PDF files...")
        
        # Initialize PDF extractor with OCR
        pdf_extractor = PDFExtractor(use_ocr=True, ocr_language="swe+eng")
        
        # Process PDF files and collect metadata
        metadata = {}
        
        for pdf_file in pdf_files:
            try:
                # Extract text and metadata
                text, doc_metadata = pdf_extractor.extract_text(pdf_file)
                
                # Save extracted text
                text_file = os.path.join(data_dir, os.path.basename(pdf_file) + ".txt")
                with open(text_file, 'w', errors='ignore') as f:
                    f.write(text)
                
                # Store metadata
                metadata[os.path.basename(text_file)] = doc_metadata
                
                logger.info(f"Extracted {len(text)} characters from {pdf_file}")
                logger.info(f"Saved extracted text to {text_file}")
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
        
        # Process CSV files
        csv_files = [f for f in files if f.lower().endswith('.csv')]
        logger.info(f"Processing {len(csv_files)} CSV files...")
        
        for csv_file in csv_files:
            try:
                # Extract data
                data = extract_csv_data(csv_file)
                
                # Save data as JSON
                json_file = os.path.join(data_dir, os.path.basename(csv_file) + ".json")
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Extracted {len(data)} records from {csv_file}")
                logger.info(f"Saved extracted data to {json_file}")
            except Exception as e:
                logger.error(f"Error processing {csv_file}: {e}")
        
        # Process text and markdown files
        text_md_files = [f for f in files if f.lower().endswith(('.txt', '.md'))]
        logger.info(f"Processing {len(text_md_files)} text and markdown files...")
        
        for text_file in text_md_files:
            try:
                # Copy file to data directory
                dest_file = os.path.join(data_dir, os.path.basename(text_file))
                with open(text_file, 'r', errors='ignore') as src:
                    with open(dest_file, 'w', errors='ignore') as dst:
                        dst.write(src.read())
                
                logger.info(f"Copied {text_file} to {dest_file}")
            except Exception as e:
                logger.error(f"Error processing {text_file}: {e}")
        
        # Save metadata
        metadata_file = os.path.join(data_dir, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata to {metadata_file}")
        
        # Save file list
        with open(os.path.join(data_dir, "file_list.txt"), 'w') as f:
            for file in files:
                f.write(f"{file}\n")
        
        logger.info(f"Saved file list to {os.path.join(data_dir, 'file_list.txt')}")
    
    # Search if query specified
    if args.search:
        logger.info(f"Searching for: {args.search}")
        
        # Apply document type filter if specified
        metadata_filter = {}
        if args.type:
            metadata_filter['document_type'] = args.type
        
        # Search documents
        matches = search_documents(args.search, data_dir, fuzzy=args.fuzzy, 
                                  metadata_filter=metadata_filter)
        
        logger.info(f"Found {len(matches)} matches for '{args.search}'")
        
        # Show results
        for i, (match, score, metadata) in enumerate(matches[:10]):  # Show top 10
            logger.info(f"  {i+1}. {match} (relevance: {score:.2f})")
            
            # Show metadata if available
            if metadata:
                metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()
                                         if k in ['document_type', 'date', 'total_amount', 'supplier']])
                logger.info(f"     {metadata_str}")
        
        if len(matches) > 10:
            logger.info(f"  ... and {len(matches) - 10} more")
    
    # Analyze documents if requested
    if args.analyze:
        logger.info("Analyzing documents...")
        
        # Perform analysis
        analysis = analyze_documents(data_dir, document_type=args.type)
        
        if analysis:
            logger.info("Analysis results:")
            for key, value in analysis.items():
                if isinstance(value, dict):
                    logger.info(f"  {key}:")
                    for k, v in value.items():
                        logger.info(f"    {k}: {v}")
                elif isinstance(value, list) and len(value) > 10:
                    logger.info(f"  {key}: {value[:10]} ... and {len(value)-10} more")
                else:
                    logger.info(f"  {key}: {value}")
            
            # Save analysis results
            analysis_file = os.path.join(data_dir, "analysis_results.json")
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            logger.info(f"Saved analysis results to {analysis_file}")
            
        else:
            logger.warning("No analysis results available")
    
    # If no action specified, show status
    if not args.index and not args.search and not args.analyze:
        logger.info("Ekonomisk Rådgivare - Enhanced Version")
        
        # Check if data directory exists and contains files
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            logger.info(f"Data directory contains {len(files)} files")
            
            # Check if metadata exists
            metadata_file = os.path.join(data_dir, "metadata.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Count document types
                    doc_types = {}
                    for doc_id, doc_metadata in metadata.items():
                        doc_type = doc_metadata.get('document_type', 'unknown')
                        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                    
                    logger.info(f"Indexed documents by type:")
                    for doc_type, count in doc_types.items():
                        logger.info(f"  {doc_type}: {count}")
                except:
                    logger.warning(f"Could not read metadata from {metadata_file}")
        else:
            logger.info("No data directory found. Use --index to index files.")
        
        # Check dependencies
        try:
            import nltk
            logger.info("NLTK is installed")
            
            try:
                nltk.data.find('tokenizers/punkt')
                logger.info("NLTK punkt tokenizer is installed")
            except LookupError:
                logger.warning("NLTK punkt tokenizer is not installed")
            
            try:
                nltk.data.find('corpora/stopwords')
                logger.info("NLTK stopwords are installed")
            except LookupError:
                logger.warning("NLTK stopwords are not installed")
        except ImportError:
            logger.warning("NLTK is not installed")
        
        try:
            import pandas
            logger.info(f"pandas {pandas.__version__} is installed")
        except ImportError:
            logger.warning("pandas is not installed")
        
        try:
            import PyPDF2
            logger.info(f"PyPDF2 {PyPDF2.__version__} is installed")
        except ImportError:
            logger.warning("PyPDF2 is not installed")
        
        # Check system tools
        import subprocess
        try:
            result = subprocess.run(['pdftotext', '-v'], stderr=subprocess.PIPE, text=True)
            logger.info(f"poppler-utils (pdftotext) is installed")
        except:
            logger.warning("poppler-utils (pdftotext) is not installed")
        
        try:
            result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, text=True)
            logger.info(f"tesseract-ocr is installed")
        except:
            logger.warning("tesseract-ocr is not installed")

if __name__ == "__main__":
    main()