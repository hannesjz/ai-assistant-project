"""
Document Indexing Module

This module provides functionality to index and search documents:
1. Index extracted text from PDF files
2. Index structured data from Excel and CSV files
3. Provide search capabilities across all indexed documents
4. Store document metadata for quick retrieval

Dependencies:
- sqlite3 (built-in)
- whoosh (for text indexing and searching)
- json (for storing structured data)
"""

import os
import json
import logging
import sqlite3
import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Class for indexing and searching documents."""
    
    def __init__(self, index_dir: str = "data", db_name: str = "document_index.db"):
        """
        Initialize the Document Indexer.
        
        Args:
            index_dir (str): Directory to store the index files.
            db_name (str): Name of the SQLite database file.
        """
        self.index_dir = index_dir
        self.db_path = os.path.join(index_dir, db_name)
        
        # Create index directory if it doesn't exist
        os.makedirs(index_dir, exist_ok=True)
def _check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        try:
            import whoosh
            logger.info(f"whoosh version {whoosh.__version__} is installed.")
            self.whoosh_available = True
        except ImportError:
            logger.warning("whoosh is not installed. Full-text search will be limited.")
            logger.warning("Install with: pip install whoosh")
            self.whoosh_available = False
    
    def _init_database(self) -> None:
        """Initialize the SQLite database for document indexing."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_name TEXT,
                file_type TEXT,
                file_size INTEGER,
                last_modified TEXT,
                indexed_date TEXT,
                content_type TEXT,
                metadata TEXT,
                extracted_text TEXT,
                structured_data TEXT
            )
            ''')
            
            # Create search index table (for simple search without whoosh)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                term TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on term for faster searches
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_term ON search_index (term)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def index_document(self, file_path: str, content_type: str, 
                      extracted_text: Optional[str] = None,
                      structured_data: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Index a document in the database.
        
        Args:
            file_path (str): Path to the document file.
            content_type (str): Type of content ('pdf', 'excel', 'csv', etc.).
            extracted_text (Optional[str]): Extracted text from the document.
            structured_data (Optional[Dict[str, Any]]): Structured data extracted from the document.
            metadata (Optional[Dict[str, Any]]): Metadata about the document.
            
        Returns:
            int: Document ID in the database.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        try:
            # Get file information
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1].lower()
            file_size = file_stat.st_size
            last_modified = datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            indexed_date = datetime.datetime.now().isoformat()
            
            # Convert structured data and metadata to JSON strings
            structured_data_json = json.dumps(structured_data) if structured_data else None
            metadata_json = json.dumps(metadata) if metadata else None
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if document already exists
            cursor.execute('SELECT id FROM documents WHERE file_path = ?', (file_path,))
            existing_doc = cursor.fetchone()
            
            if existing_doc:
                # Update existing document
                doc_id = existing_doc[0]
                cursor.execute('''
                UPDATE documents SET
                    file_name = ?,
                    file_type = ?,
                    file_size = ?,
                    last_modified = ?,
                    indexed_date = ?,
                    content_type = ?,
                    metadata = ?,
                    extracted_text = ?,
                    structured_data = ?
                WHERE id = ?
                ''', (
                    file_name, file_type, file_size, last_modified, indexed_date,
                    content_type, metadata_json, extracted_text, structured_data_json,
                    doc_id
                ))
                
                # Delete existing search index entries
                cursor.execute('DELETE FROM search_index WHERE document_id = ?', (doc_id,))
            else:
                # Insert new document
                cursor.execute('''
                INSERT INTO documents (
                    file_path, file_name, file_type, file_size, last_modified,
                    indexed_date, content_type, metadata, extracted_text, structured_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_path, file_name, file_type, file_size, last_modified,
                    indexed_date, content_type, metadata_json, extracted_text, structured_data_json
                ))
                
                doc_id = cursor.lastrowid
            
            # Index text content for searching
            if extracted_text:
                self._index_text(cursor, doc_id, extracted_text)
            
            # Index structured data for searching
            if structured_data:
                self._index_structured_data(cursor, doc_id, structured_data)
            
            conn.commit()
            
            # If whoosh is available, update the full-text index
            if self.whoosh_available and extracted_text:
                self._update_whoosh_index(doc_id, file_name, content_type, extracted_text, metadata)
            
            conn.close()
            
            logger.info(f"Successfully indexed document: {file_path}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to index document {file_path}: {e}")
            raise
        
        # Initialize database
def _index_text(self, cursor: sqlite3.Cursor, doc_id: int, text: str) -> None:
        """
        Index text content for simple searching.
        
        Args:
            cursor (sqlite3.Cursor): Database cursor.
            doc_id (int): Document ID.
            text (str): Text to index.
        """
        # Simple tokenization and indexing
        # This is a basic approach - whoosh provides more sophisticated indexing
        if not text:
            return
        
        # Normalize and tokenize text
        words = set(self._tokenize_text(text))
        
        # Add terms to search index
        for word in words:
            if len(word) > 2:  # Skip very short words
                cursor.execute(
                    'INSERT INTO search_index (document_id, term) VALUES (?, ?)',
                    (doc_id, word)
                )
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into words for indexing.
        
        Args:
            text (str): Text to tokenize.
            
        Returns:
            List[str]: List of tokens.
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace punctuation with spaces
        for char in '.,;:!?()[]{}"\'':
            text = text.replace(char, ' ')
        
        # Split into words and filter out empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        
        return words
    
    def _index_structured_data(self, cursor: sqlite3.Cursor, doc_id: int, data: Dict[str, Any]) -> None:
        """
        Index structured data for searching.
        
        Args:
            cursor (sqlite3.Cursor): Database cursor.
            doc_id (int): Document ID.
            data (Dict[str, Any]): Structured data to index.
        """
        # Extract searchable text from structured data
        text_values = self._extract_text_from_dict(data)
        
        # Index the extracted text
        if text_values:
            self._index_text(cursor, doc_id, ' '.join(text_values))
    
    def _extract_text_from_dict(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract text values from a nested dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary to extract text from.
            
        Returns:
            List[str]: List of text values.
        """
        text_values = []
        
        def extract_text(obj):
            if isinstance(obj, str):
                text_values.append(obj)
            elif isinstance(obj, (int, float)):
                text_values.append(str(obj))
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    text_values.append(str(key))
                    extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(data)
        return text_values
    
    def _update_whoosh_index(self, doc_id: int, file_name: str, content_type: str, 
                            text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the Whoosh full-text index.
        
        Args:
            doc_id (int): Document ID.
            file_name (str): Name of the file.
            content_type (str): Type of content.
            text (str): Text to index.
            metadata (Optional[Dict[str, Any]]): Document metadata.
        """
        try:
            from whoosh import index
            from whoosh.fields import Schema, ID, TEXT, KEYWORD, STORED
            from whoosh.analysis import StemmingAnalyzer
            import whoosh.index as index
            
            # Define schema
            schema = Schema(
                doc_id=ID(stored=True, unique=True),
                file_name=TEXT(stored=True),
                content_type=KEYWORD(stored=True),
                content=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                metadata=STORED
            )
            
            # Create or open index
            index_path = os.path.join(self.index_dir, "whoosh_index")
            if not os.path.exists(index_path):
                os.makedirs(index_path, exist_ok=True)
                ix = index.create_in(index_path, schema)
            else:
                ix = index.open_dir(index_path)
            
            # Update index
            writer = ix.writer()
            
            # Convert doc_id to string for Whoosh
            doc_id_str = str(doc_id)
            
            # Add document to index
            writer.update_document(
                doc_id=doc_id_str,
                file_name=file_name,
                content_type=content_type,
                content=text,
                metadata=metadata
            )
            
            writer.commit()
            
            logger.info(f"Updated Whoosh index for document ID {doc_id}")
        except Exception as e:
            logger.error(f"Failed to update Whoosh index: {e}")
    
    def search(self, query: str, content_type: Optional[str] = None, 
              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query (str): Search query.
            content_type (Optional[str]): Filter by content type.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[Dict[str, Any]]: List of matching documents.
        """
        # Try to use Whoosh for full-text search if available
        if self.whoosh_available:
            try:
                results = self._search_with_whoosh(query, content_type, limit)
                if results:
def _search_with_whoosh(self, query: str, content_type: Optional[str] = None, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search using Whoosh full-text index.
        
        Args:
            query (str): Search query.
            content_type (Optional[str]): Filter by content type.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[Dict[str, Any]]: List of matching documents.
        """
        from whoosh import index
        from whoosh.qparser import QueryParser, MultifieldParser
        
        # Open index
        index_path = os.path.join(self.index_dir, "whoosh_index")
        if not os.path.exists(index_path):
            return []
        
        ix = index.open_dir(index_path)
        
        # Create query parser
        parser = MultifieldParser(["content", "file_name"], ix.schema)
        q = parser.parse(query)
        
        # Search
        results = []
        with ix.searcher() as searcher:
            hits = searcher.search(q, limit=limit)
            
            # Filter by content type if specified
            if content_type:
                hits = [hit for hit in hits if hit["content_type"] == content_type]
            
            # Get document details from database
            for hit in hits:
                doc_id = int(hit["doc_id"])
                doc = self.get_document(doc_id)
                if doc:
                    results.append(doc)
        
        return results
    
    def _search_simple(self, query: str, content_type: Optional[str] = None, 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search using simple SQLite-based index.
        
        Args:
            query (str): Search query.
            content_type (Optional[str]): Filter by content type.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[Dict[str, Any]]: List of matching documents.
        """
        try:
            # Tokenize query
            query_terms = self._tokenize_text(query)
            
            if not query_terms:
                return []
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            sql_query = '''
            SELECT d.*, COUNT(s.id) as match_count
            FROM documents d
            JOIN search_index s ON d.id = s.document_id
            WHERE s.term IN ({})
            '''.format(','.join(['?'] * len(query_terms)))
            
            # Add content type filter if specified
            if content_type:
                sql_query += ' AND d.content_type = ?'
                params = query_terms + [content_type]
            else:
                params = query_terms
            
            # Group by document and order by match count
            sql_query += '''
            GROUP BY d.id
            ORDER BY match_count DESC
            LIMIT ?
            '''
            
            params.append(limit)
            
            # Execute query
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = []
            for row in rows:
                doc = dict(row)
                
                # Parse JSON fields
                if doc['metadata']:
                    doc['metadata'] = json.loads(doc['metadata'])
                
                if doc['structured_data']:
                    doc['structured_data'] = json.loads(doc['structured_data'])
                
                # Remove large text field from results
                doc.pop('extracted_text', None)
                
                results.append(doc)
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id (int): Document ID.
            
        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Convert row to dictionary
            doc = dict(row)
            
            # Parse JSON fields
            if doc['metadata']:
                doc['metadata'] = json.loads(doc['metadata'])
            
            if doc['structured_data']:
                doc['structured_data'] = json.loads(doc['structured_data'])
            
            conn.close()
            return doc
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def get_document_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by file path.
        
        Args:
            file_path (str): Path to the document file.
            
        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found.
        """
def list_documents(self, content_type: Optional[str] = None, 
                      limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List indexed documents.
        
        Args:
            content_type (Optional[str]): Filter by content type.
            limit (int): Maximum number of results to return.
            offset (int): Offset for pagination.
            
        Returns:
            List[Dict[str, Any]]: List of documents.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            sql_query = 'SELECT id, file_path, file_name, file_type, content_type, indexed_date FROM documents'
            params = []
            
            # Add content type filter if specified
            if content_type:
                sql_query += ' WHERE content_type = ?'
                params.append(content_type)
            
            # Add limit and offset
            sql_query += ' ORDER BY indexed_date DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            # Execute query
            cursor.execute(sql_query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            results = [dict(row) for row in rows]
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed documents.
        
        Returns:
            Dict[str, Any]: Statistics about the indexed documents.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total document count
            cursor.execute('SELECT COUNT(*) FROM documents')
            total_count = cursor.fetchone()[0]
            
            # Get document count by content type
            cursor.execute('SELECT content_type, COUNT(*) FROM documents GROUP BY content_type')
            content_type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get document count by file type
            cursor.execute('SELECT file_type, COUNT(*) FROM documents GROUP BY file_type')
            file_type_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get total index size
            index_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # Get whoosh index size if available
            whoosh_index_path = os.path.join(self.index_dir, "whoosh_index")
            whoosh_index_size = 0
            if os.path.exists(whoosh_index_path):
                for root, _, files in os.walk(whoosh_index_path):
                    for file in files:
                        whoosh_index_size += os.path.getsize(os.path.join(root, file))
            
            # Get most recent document
            cursor.execute('''
            SELECT file_name, indexed_date FROM documents 
            ORDER BY indexed_date DESC LIMIT 1
            ''')
            most_recent = cursor.fetchone()
            most_recent_doc = {
                'file_name': most_recent[0],
                'indexed_date': most_recent[1]
            } if most_recent else None
            
            conn.close()
            
            return {
                'total_documents': total_count,
                'by_content_type': content_type_counts,
                'by_file_type': file_type_counts,
                'database_size_bytes': index_size,
                'whoosh_index_size_bytes': whoosh_index_size,
                'most_recent_document': most_recent_doc
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total_documents': 0,
                'by_content_type': {},
                'by_file_type': {},
                'database_size_bytes': 0,
                'whoosh_index_size_bytes': 0,
                'most_recent_document': None,
                'error': str(e)
            }
    
    def delete_document(self, doc_id: int) -> bool:
        """
        Delete a document from the index.
        
        Args:
            doc_id (int): Document ID.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete document
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            
            # Delete search index entries
            cursor.execute('DELETE FROM search_index WHERE document_id = ?', (doc_id,))
            
            conn.commit()
            conn.close()
            
            # Update whoosh index if available
            if self.whoosh_available:
                self._delete_from_whoosh(doc_id)
            
            logger.info(f"Deleted document ID {doc_id} from index")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def _delete_from_whoosh(self, doc_id: int) -> None:
        """
        Delete a document from the Whoosh index.
        
        Args:
            doc_id (int): Document ID.
        """
        try:
            from whoosh import index
            
            # Open index
            index_path = os.path.join(self.index_dir, "whoosh_index")
            if not os.path.exists(index_path):
                return
            
            ix = index.open_dir(index_path)
            
            # Delete document
            writer = ix.writer()
            writer.delete_by_term('doc_id', str(doc_id))
            writer.commit()
            
            logger.info(f"Deleted document ID {doc_id} from Whoosh index")
        except Exception as e:
            logger.error(f"Failed to delete from Whoosh index: {e}")
    
    def clear_index(self) -> bool:
        """
        Clear the entire index.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all documents and search index entries
            cursor.execute('DELETE FROM search_index')
            cursor.execute('DELETE FROM documents')
            
            conn.commit()
            conn.close()
            
            # Clear whoosh index if available
            whoosh_index_path = os.path.join(self.index_dir, "whoosh_index")
            if os.path.exists(whoosh_index_path):
                import shutil
                shutil.rmtree(whoosh_index_path)
            
            logger.info("Cleared index")
            return True
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            return False


def main():
    """Command-line interface for document indexing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index and search documents")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index a document")
    index_parser.add_argument("file_path", help="Path to the document file")
    index_parser.add_argument("--content-type", "-t", required=True, 
                             help="Type of content (pdf, excel, csv, etc.)")
    index_parser.add_argument("--text-file", "-f", 
                             help="Path to a file containing extracted text")
    index_parser.add_argument("--data-file", "-d", 
                             help="Path to a JSON file containing structured data")
    index_parser.add_argument("--metadata-file", "-m", 
                             help="Path to a JSON file containing metadata")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--content-type", "-t", 
                              help="Filter by content type")
    search_parser.add_argument("--limit", "-l", type=int, default=10,
                              help="Maximum number of results to return")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List indexed documents")
    list_parser.add_argument("--content-type", "-t", 
                            help="Filter by content type")
    list_parser.add_argument("--limit", "-l", type=int, default=100,
                            help="Maximum number of results to return")
    list_parser.add_argument("--offset", "-o", type=int, default=0,
                            help="Offset for pagination")
    
    # Stats command
    subparsers.add_parser("stats", help="Get statistics about the indexed documents")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a document from the index")
    delete_parser.add_argument("doc_id", type=int, help="Document ID")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear the entire index")
    
    args = parser.parse_args()
    
    # Initialize indexer
    indexer = DocumentIndexer()
    
    if args.command == "index":
        # Load extracted text if provided
        extracted_text = None
        if args.text_file:
            with open(args.text_file, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        
        # Load structured data if provided
        structured_data = None
        if args.data_file:
            with open(args.data_file, 'r', encoding='utf-8') as f:
                structured_data = json.load(f)
        
        # Load metadata if provided
        metadata = None
        if args.metadata_file:
            with open(args.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Index document
        doc_id = indexer.index_document(
            args.file_path,
            args.content_type,
            extracted_text,
            structured_data,
            metadata
        )
        
        print(f"Document indexed with ID: {doc_id}")
    
    elif args.command == "search":
        # Search for documents
        results = indexer.search(args.query, args.content_type, args.limit)
        
        print(f"Found {len(results)} matching documents:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc['file_name']} ({doc['content_type']})")
            print(f"   Path: {doc['file_path']}")
            print(f"   Indexed: {doc['indexed_date']}")
            print()
    
    elif args.command == "list":
        # List documents
        results = indexer.list_documents(args.content_type, args.limit, args.offset)
        
        print(f"Found {len(results)} documents:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc['file_name']} ({doc['content_type']})")
            print(f"   Path: {doc['file_path']}")
            print(f"   Indexed: {doc['indexed_date']}")
            print()
    
    elif args.command == "stats":
        # Get statistics
        stats = indexer.get_statistics()
        
        print("Index Statistics:")
        print(f"Total documents: {stats['total_documents']}")
        print("Documents by content type:")
        for content_type, count in stats['by_content_type'].items():
            print(f"  {content_type}: {count}")
        print("Documents by file type:")
        for file_type, count in stats['by_file_type'].items():
            print(f"  {file_type}: {count}")
        print(f"Database size: {stats['database_size_bytes'] / 1024:.2f} KB")
        print(f"Whoosh index size: {stats['whoosh_index_size_bytes'] / 1024:.2f} KB")
        if stats['most_recent_document']:
            print(f"Most recent document: {stats['most_recent_document']['file_name']} "
                 f"({stats['most_recent_document']['indexed_date']})")
    
    elif args.command == "delete":
        # Delete document
        success = indexer.delete_document(args.doc_id)
        
        if success:
            print(f"Document with ID {args.doc_id} deleted successfully")
        else:
            print(f"Failed to delete document with ID {args.doc_id}")
    
    elif args.command == "clear":
        # Clear index
        success = indexer.clear_index()
        
        if success:
            print("Index cleared successfully")
        else:
            print("Failed to clear index")


if __name__ == "__main__":
    main()
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM documents WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Convert row to dictionary
            doc = dict(row)
            
            # Parse JSON fields
            if doc['metadata']:
                doc['metadata'] = json.loads(doc['metadata'])
            
            if doc['structured_data']:
                doc['structured_data'] = json.loads(doc['structured_data'])
            
            conn.close()
            return doc
        except Exception as e:
            logger.error(f"Failed to get document by path {file_path}: {e}")
            return None
                    return results
            except Exception as e:
                logger.error(f"Whoosh search failed: {e}. Falling back to simple search.")
        
        # Fall back to simple search
        return self._search_simple(query, content_type, limit)
        self._init_database()
        
        # Check for whoosh
        self._check_dependencies()