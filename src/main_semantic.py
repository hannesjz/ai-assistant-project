"""
Main Application with Semantic Search Integration

This enhanced version includes:
1. OCR for scanned documents
2. Metadata extraction
3. Semantic search and analysis
4. Document clustering and trend analysis

Dependencies:
- All dependencies from main_enhanced.py
- nltk
- scikit-learn
- numpy
- spacy (optional, for better entity recognition)
"""

import os
import sys
import json
import logging
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

# Import our modules
from pdf_extractor.enhanced_pdf_extractor import PDFExtractor
from semantic_search.semantic_search import SemanticSearch

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

def format_search_results(results, show_metadata=True, max_results=10):
    """Format search results for display."""
    output = []
    
    for i, (doc_id, score, metadata) in enumerate(results[:max_results]):
        output.append(f"{i+1}. {doc_id} (relevance: {score:.2f})")
        
        # Show metadata if available and requested
        if show_metadata and metadata:
            # Filter to most important metadata fields
            important_fields = ['document_type', 'date', 'total_amount', 'supplier', 'invoice_number']
            metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items() 
                                     if k in important_fields and v])
            if metadata_str:
                output.append(f"   {metadata_str}")
    
    if len(results) > max_results:
        output.append(f"... and {len(results) - max_results} more")
    
    return output

def format_cluster_results(clusters, keywords, metadata=None, max_clusters=5, max_docs_per_cluster=5):
    """Format cluster results for display."""
    output = []
    
    for cluster_id, doc_ids in list(clusters.items())[:max_clusters]:
        output.append(f"Cluster {cluster_id} ({len(doc_ids)} documents):")
        
        # Show keywords if available
        if keywords and cluster_id in keywords:
            output.append(f"  Keywords: {', '.join(keywords[cluster_id])}")
        
        # Show documents in cluster
        output.append(f"  Documents:")
        for i, doc_id in enumerate(doc_ids[:max_docs_per_cluster]):
            doc_info = f"    {i+1}. {doc_id}"
            
            # Add metadata if available
            if metadata and doc_id in metadata:
                doc_metadata = metadata[doc_id]
                if 'document_type' in doc_metadata:
                    doc_info += f" ({doc_metadata['document_type']})"
                if 'date' in doc_metadata:
                    doc_info += f", {doc_metadata['date']}"
                if 'total_amount' in doc_metadata:
                    doc_info += f", {doc_metadata['total_amount']} kr"
            
            output.append(doc_info)
        
        if len(doc_ids) > max_docs_per_cluster:
            output.append(f"    ... and {len(doc_ids) - max_docs_per_cluster} more")
    
    if len(clusters) > max_clusters:
        output.append(f"... and {len(clusters) - max_clusters} more clusters")
    
    return output

def format_entity_results(entities, max_entities=10):
    """Format entity results for display."""
    output = []
    
    for entity_type, entity_set in entities.items():
        output.append(f"{entity_type.capitalize()} ({len(entity_set)}):")
        
        # Show examples
        entity_list = list(entity_set)
        examples = entity_list[:max_entities]
        output.append(f"  {', '.join(examples)}")
        
        if len(entity_list) > max_entities:
            output.append(f"  ... and {len(entity_list) - max_entities} more")
    
    return output

def format_trend_results(trends):
    """Format trend analysis results for display."""
    output = []
    
    for group, stats in trends.items():
        output.append(f"{group}:")
        
        for stat, value in stats.items():
            if stat == 'most_common':
                output.append(f"  {stat}: {', '.join([f'{item[0]} ({item[1]})' for item in value])}")
            else:
                output.append(f"  {stat}: {value}")
    
    return output

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Ekonomisk Rådgivare - Semantic Search Edition")
    parser.add_argument("--index", help="Index files in directory")
    parser.add_argument("--search", help="Search for documents")
    parser.add_argument("--fuzzy", action="store_true", help="Use fuzzy search")
    parser.add_argument("--semantic", action="store_true", help="Use semantic search")
    parser.add_argument("--analyze", action="store_true", help="Analyze documents")
    parser.add_argument("--type", help="Filter by document type (invoice, receipt, etc.)")
    parser.add_argument("--cluster", action="store_true", help="Show document clusters")
    parser.add_argument("--entities", action="store_true", help="Show extracted entities")
    parser.add_argument("--trends", help="Analyze trends in field (e.g., total_amount)")
    parser.add_argument("--group-by", default="date", help="Field to group by for trend analysis")
    parser.add_argument("--related", help="Show terms related to input term")
    parser.add_argument("--output", help="Save results to file")
    
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
        
        # Initialize semantic search
        logger.info("Initializing semantic search...")
        try:
            semantic_search = SemanticSearch(data_dir)
            logger.info("Semantic search initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing semantic search: {e}")
    
    # Initialize semantic search for other operations
    semantic_search = None
    try:
        semantic_search = SemanticSearch(data_dir)
    except Exception as e:
        if args.search or args.analyze or args.cluster or args.entities or args.trends or args.related:
            logger.error(f"Error initializing semantic search: {e}")
            return
    
    # Prepare output
    output_lines = []
    
    # Search if query specified
    if args.search and semantic_search:
        logger.info(f"Searching for: {args.search}")
        
        # Apply document type filter if specified
        metadata_filter = {}
        if args.type:
            metadata_filter['document_type'] = args.type
        
        # Search documents
        matches = semantic_search.search(args.search, fuzzy=args.fuzzy, 
                                        semantic=args.semantic,
                                        metadata_filter=metadata_filter)
        
        logger.info(f"Found {len(matches)} matches for '{args.search}'")
        
        # Format and display results
        search_results = format_search_results(matches)
        for line in search_results:
            logger.info(line)
            output_lines.append(line)
    
    # Show clusters if requested
    if args.cluster and semantic_search:
        logger.info("Retrieving document clusters...")
        
        # Get clusters and keywords
        clusters = semantic_search.get_document_clusters()
        keywords = semantic_search.get_cluster_keywords()
        
        # Format and display results
        cluster_results = format_cluster_results(clusters, keywords, semantic_search.metadata)
        for line in cluster_results:
            logger.info(line)
            output_lines.append(line)
    
    # Show entities if requested
    if args.entities and semantic_search:
        logger.info("Retrieving extracted entities...")
        
        # Get entities
        entities = semantic_search.get_entities()
        
        # Format and display results
        entity_results = format_entity_results(entities)
        for line in entity_results:
            logger.info(line)
            output_lines.append(line)
    
    # Show related terms if requested
    if args.related and semantic_search:
        logger.info(f"Finding terms related to '{args.related}'...")
        
        # Get related terms
        related_terms = semantic_search.get_related_terms(args.related)
        
        logger.info(f"Found {len(related_terms)} terms related to '{args.related}'")
        
        # Display results
        for term, score in related_terms:
            line = f"  {term} (similarity: {score:.2f})"
            logger.info(line)
            output_lines.append(line)
    
    # Analyze trends if requested
    if args.trends and semantic_search:
        logger.info(f"Analyzing trends in '{args.trends}' grouped by '{args.group_by}'...")
        
        # Analyze trends
        trends = semantic_search.analyze_trends(field=args.trends, 
                                              group_by=args.group_by,
                                              document_type=args.type)
        
        # Format and display results
        trend_results = format_trend_results(trends)
        for line in trend_results:
            logger.info(line)
            output_lines.append(line)
    
    # Analyze documents if requested
    if args.analyze and semantic_search:
        logger.info("Analyzing documents...")
        
        # Get clusters and keywords
        clusters = semantic_search.get_document_clusters()
        keywords = semantic_search.get_cluster_keywords()
        
        # Get entities
        entities = semantic_search.get_entities()
        
        # Format and display results
        logger.info("Document clusters:")
        cluster_results = format_cluster_results(clusters, keywords, semantic_search.metadata)
        for line in cluster_results:
            logger.info(line)
            output_lines.append(line)
        
        logger.info("\nExtracted entities:")
        entity_results = format_entity_results(entities)
        for line in entity_results:
            logger.info(line)
            output_lines.append(line)
        
        # Analyze trends in total amount by date if available
        if any('total_amount' in metadata for metadata in semantic_search.metadata.values()) and \
           any('date' in metadata for metadata in semantic_search.metadata.values()):
            logger.info("\nTrend analysis (total_amount by date):")
            trends = semantic_search.analyze_trends(field='total_amount', group_by='date')
            trend_results = format_trend_results(trends)
            for line in trend_results:
                logger.info(line)
                output_lines.append(line)
    
    # Save output to file if requested
    if args.output and output_lines:
        try:
            with open(args.output, 'w') as f:
                for line in output_lines:
                    f.write(f"{line}\n")
            logger.info(f"Saved results to {args.output}")
        except Exception as e:
            logger.error(f"Error saving results to {args.output}: {e}")
    
    # If no action specified, show status
    if not args.index and not args.search and not args.analyze and not args.cluster and \
       not args.entities and not args.trends and not args.related:
        logger.info("Ekonomisk Rådgivare - Semantic Search Edition")
        
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
        
        # Check semantic search
        if semantic_search:
            logger.info("Semantic search is initialized")
            
            # Show cluster info
            clusters = semantic_search.get_document_clusters()
            logger.info(f"Documents are clustered into {len(clusters)} groups")
            
            # Show entity info
            entities = semantic_search.get_entities()
            for entity_type, entity_set in entities.items():
                logger.info(f"Extracted {len(entity_set)} {entity_type}")
        else:
            logger.info("Semantic search is not initialized")
        
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
            import sklearn
            logger.info(f"scikit-learn {sklearn.__version__} is installed")
        except ImportError:
            logger.warning("scikit-learn is not installed")
        
        try:
            import numpy
            logger.info(f"numpy {numpy.__version__} is installed")
        except ImportError:
            logger.warning("numpy is not installed")
        
        try:
            import spacy
            logger.info(f"spacy {spacy.__version__} is installed")
            
            try:
                nlp = spacy.load("sv_core_news_sm")
                logger.info("Swedish spaCy model is installed")
            except:
                logger.warning("Swedish spaCy model is not installed")
        except ImportError:
            logger.warning("spacy is not installed")
        
        # Show usage examples
        logger.info("\nUsage examples:")
        logger.info("  Index files:           python main_semantic.py --index ./test_files")
        logger.info("  Search:                python main_semantic.py --search \"faktura\" --semantic")
        logger.info("  Filter by type:        python main_semantic.py --search \"belopp\" --type invoice")
        logger.info("  Show clusters:         python main_semantic.py --cluster")
        logger.info("  Show entities:         python main_semantic.py --entities")
        logger.info("  Find related terms:    python main_semantic.py --related \"faktura\"")
        logger.info("  Analyze trends:        python main_semantic.py --trends total_amount --group-by date")
        logger.info("  Full analysis:         python main_semantic.py --analyze")
        logger.info("  Save results:          python main_semantic.py --search \"faktura\" --output results.txt")

if __name__ == "__main__":
    main()