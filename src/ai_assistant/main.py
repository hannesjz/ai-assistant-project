#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Assistant Main Script

This script provides the entry point for running the AI Assistant with
Google Cloud Storage and GitHub integration.
"""

import os
import sys
import logging
import argparse
import json
from typing import Dict, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ai_assistant.core.ai_assistant import AIAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Assistant with Google Cloud Storage and GitHub integration")
    
    # Configuration
    parser.add_argument("--config", help="Path to configuration file")
    
    # GCS operations
    parser.add_argument("--gcs-process", action="store_true", help="Process documents from GCS")
    parser.add_argument("--gcs-prefix", default="", help="Prefix for files in GCS")
    parser.add_argument("--gcs-watch", action="store_true", help="Watch GCS for changes")
    parser.add_argument("--gcs-interval", type=int, default=60, help="GCS polling interval in seconds")
    
    # Document operations
    parser.add_argument("--process-document", help="Process a local document")
    parser.add_argument("--process-directory", help="Process all documents in a directory")
    parser.add_argument("--recursive", action="store_true", help="Recursively process directory")
    
    # Search and QA
    parser.add_argument("--search", help="Search for documents")
    parser.add_argument("--top-k", type=int, default=10, help="Number of search results to return")
    parser.add_argument("--question", help="Answer a question based on stored documents")
    
    # GitHub operations
    parser.add_argument("--update-code", help="Update code in GitHub repository (file:content)")
    parser.add_argument("--commit-message", help="Commit message for GitHub updates")
    
    # System operations
    parser.add_argument("--stats", action="store_true", help="Show system statistics")
    
    return parser.parse_args()

def process_directory(assistant: AIAssistant, directory: str, recursive: bool = False) -> Dict[str, Any]:
    """
    Process all documents in a directory.
    
    Args:
        assistant: AI Assistant instance
        directory: Directory to process
        recursive: Whether to recursively process subdirectories
        
    Returns:
        Statistics about the processing operation
    """
    logger.info(f"Processing directory: {directory} (recursive: {recursive})")
    
    # Get supported file types
    supported_types = assistant.config["document_processing"]["supported_file_types"]
    
    # Find all files
    processed_files = 0
    failed_files = 0
    document_ids = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in supported_types:
                logger.info(f"Processing file: {file_path}")
                document_id = assistant.process_document(file_path)
                
                if document_id:
                    processed_files += 1
                    document_ids.append(document_id)
                else:
                    failed_files += 1
        
        if not recursive:
            break
    
    stats = {
        "processed_files": processed_files,
        "failed_files": failed_files,
        "document_ids": document_ids
    }
    
    logger.info(f"Processed {processed_files} files, failed {failed_files} files")
    return stats

def main():
    """Main entry point for the AI Assistant."""
    args = parse_arguments()
    
    try:
        # Initialize AI Assistant
        assistant = AIAssistant(args.config)
        logger.info("AI Assistant initialized")
        
        # Process document if specified
        if args.process_document:
            document_id = assistant.process_document(args.process_document)
            if document_id:
                print(f"Document processed successfully: {document_id}")
            else:
                print("Failed to process document")
        
        # Process directory if specified
        if args.process_directory:
            stats = process_directory(assistant, args.process_directory, args.recursive)
            print(json.dumps(stats, indent=2))
        
        # Process documents from GCS if specified
        if args.gcs_process:
            document_ids = assistant.process_documents_from_gcs(args.gcs_prefix)
            print(f"Processed {len(document_ids)} documents from GCS")
            print(json.dumps(document_ids, indent=2))
        
        # Watch GCS for changes if specified
        if args.gcs_watch:
            print(f"Watching GCS for changes with prefix: {args.gcs_prefix}")
            print(f"Press Ctrl+C to stop")
            assistant.watch_gcs_for_changes(args.gcs_prefix, args.gcs_interval)
        
        # Search for documents if specified
        if args.search:
            results = assistant.search_documents(args.search, args.top_k)
            print(f"Found {len(results)} documents matching query: {args.search}")
            for i, doc in enumerate(results):
                print(f"\n--- Result {i+1} ---")
                print(f"Title: {doc['title']}")
                print(f"Document ID: {doc['document_id']}")
                print(f"Similarity Score: {doc.get('similarity_score', 'N/A')}")
                print(f"Content Preview: {doc['content'][:200]}...")
        
        # Answer question if specified
        if args.question:
            answer = assistant.answer_question(args.question)
            print(f"\nQuestion: {args.question}")
            print(f"Answer: {answer['answer']}")
            print(f"Confidence: {answer['confidence']}")
            print("\nSources:")
            for source in answer['sources']:
                print(f"- {source['title']} ({source['document_id']})")
        
        # Update code in GitHub if specified
        if args.update_code:
            file_path, content = args.update_code.split(':', 1)
            success = assistant.update_code_in_github(file_path, content, args.commit_message)
            if success:
                print(f"Successfully updated {file_path} in GitHub")
            else:
                print(f"Failed to update {file_path} in GitHub")
        
        # Show system statistics if specified
        if args.stats:
            stats = assistant.get_system_stats()
            print(json.dumps(stats, indent=2, default=str))
        
        # If no action specified, show help
        if not any([
            args.process_document, args.process_directory, args.gcs_process, 
            args.gcs_watch, args.search, args.question, args.update_code, args.stats
        ]):
            print("No action specified. Use --help to see available options.")
    
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        print("\nOperation interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())