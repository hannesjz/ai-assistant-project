"""
Memory Management System

This module provides functionality for storing and retrieving document information,
vector representations, and relationships between documents.
"""

import os
import json
import sqlite3
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemoryManagementSystem:
    """Class for managing document memory and relationships."""
    
    def __init__(self, db_path: str, vector_dimension: int = 768):
        """
        Initialize the memory management system.
        
        Args:
            db_path: Path to the SQLite database file
            vector_dimension: Dimension of document vectors
        """
        self.db_path = db_path
        self.vector_dimension = vector_dimension
        
        # Create database and tables if they don't exist
        self._initialize_database()
        
        logger.info(f"Initialized Memory Management System with database at {db_path}")
    
    def _initialize_database(self):
        """Initialize the database with required tables."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE,
                source_path TEXT,
                document_type TEXT,
                title TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
            ''')
            
            # Create vectors table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT UNIQUE,
                vector BLOB,
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
            ''')
            
            # Create relationships table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_document_id TEXT,
                target_document_id TEXT,
                relationship_type TEXT,
                strength REAL,
                metadata TEXT,
                FOREIGN KEY (source_document_id) REFERENCES documents (document_id),
                FOREIGN KEY (target_document_id) REFERENCES documents (document_id)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def store_document(self, document_id: str, source_path: str, document_type: str, 
                      title: str, content: str, metadata: Dict[str, Any]) -> bool:
        """
        Store a document in the memory system.
        
        Args:
            document_id: Unique identifier for the document
            source_path: Path to the source document
            document_type: Type of document (PDF, Excel, etc.)
            title: Document title
            content: Document content
            metadata: Document metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (document_id, source_path, document_type, title, content, metadata, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document_id, 
                source_path, 
                document_type, 
                title, 
                content, 
                json.dumps(metadata), 
                now, 
                now
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            return False
    
    def store_document_vector(self, document_id: str, vector: np.ndarray) -> bool:
        """
        Store a document vector in the memory system.
        
        Args:
            document_id: Unique identifier for the document
            vector: Document vector representation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert numpy array to bytes for storage
            vector_bytes = vector.tobytes()
            
            cursor.execute('''
            INSERT OR REPLACE INTO document_vectors 
            (document_id, vector)
            VALUES (?, ?)
            ''', (document_id, vector_bytes))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored vector for document: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing document vector: {e}")
            return False
    
    def store_relationship(self, source_id: str, target_id: str, 
                          relationship_type: str, strength: float, 
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Store a relationship between two documents.
        
        Args:
            source_id: Source document ID
            target_id: Target document ID
            relationship_type: Type of relationship
            strength: Strength of relationship (0-1)
            metadata: Additional metadata about the relationship
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO document_relationships 
            (source_document_id, target_document_id, relationship_type, strength, metadata)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                source_id, 
                target_id, 
                relationship_type, 
                strength, 
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored relationship: {source_id} -> {target_id} ({relationship_type})")
            return True
        except Exception as e:
            logger.error(f"Error storing relationship: {e}")
            return False
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from memory.
        
        Args:
            document_id: Unique identifier for the document
            
        Returns:
            Document data as a dictionary, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update last accessed time and increment access count
            now = datetime.now().isoformat()
            cursor.execute('''
            UPDATE documents 
            SET last_accessed = ?, access_count = access_count + 1
            WHERE document_id = ?
            ''', (now, document_id))
            
            # Retrieve document
            cursor.execute('''
            SELECT document_id, source_path, document_type, title, content, metadata, 
                   created_at, last_accessed, access_count
            FROM documents
            WHERE document_id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Document not found: {document_id}")
                return None
            
            conn.commit()
            conn.close()
            
            document = {
                'document_id': row[0],
                'source_path': row[1],
                'document_type': row[2],
                'title': row[3],
                'content': row[4],
                'metadata': json.loads(row[5]),
                'created_at': row[6],
                'last_accessed': row[7],
                'access_count': row[8]
            }
            
            logger.info(f"Retrieved document: {document_id}")
            return document
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            return None
    
    def get_document_vector(self, document_id: str) -> Optional[np.ndarray]:
        """
        Retrieve a document vector from memory.
        
        Args:
            document_id: Unique identifier for the document
            
        Returns:
            Document vector as numpy array, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT vector
            FROM document_vectors
            WHERE document_id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Vector not found for document: {document_id}")
                return None
            
            conn.close()
            
            # Convert bytes back to numpy array
            vector_bytes = row[0]
            vector = np.frombuffer(vector_bytes, dtype=np.float32)
            
            logger.info(f"Retrieved vector for document: {document_id}")
            return vector
        except Exception as e:
            logger.error(f"Error retrieving document vector: {e}")
            return None
    
    def search_documents(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for documents similar to the query vector.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            
        Returns:
            List of (document_id, similarity_score) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT document_id, vector
            FROM document_vectors
            ''')
            
            results = []
            for row in cursor.fetchall():
                doc_id = row[0]
                vector_bytes = row[1]
                vector = np.frombuffer(vector_bytes, dtype=np.float32)
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
                results.append((doc_id, float(similarity)))
            
            conn.close()
            
            # Sort by similarity (descending) and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            logger.info(f"Found {len(results[:top_k])} similar documents")
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_related_documents(self, document_id: str, relationship_type: str = None, 
                             min_strength: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get documents related to the given document.
        
        Args:
            document_id: Document ID to find relations for
            relationship_type: Optional filter for relationship type
            min_strength: Minimum relationship strength
            
        Returns:
            List of related document data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
            SELECT r.target_document_id, r.relationship_type, r.strength, r.metadata,
                   d.title, d.document_type
            FROM document_relationships r
            JOIN documents d ON r.target_document_id = d.document_id
            WHERE r.source_document_id = ? AND r.strength >= ?
            '''
            
            params = [document_id, min_strength]
            
            if relationship_type:
                query += " AND r.relationship_type = ?"
                params.append(relationship_type)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'document_id': row[0],
                    'relationship_type': row[1],
                    'strength': row[2],
                    'relationship_metadata': json.loads(row[3]),
                    'title': row[4],
                    'document_type': row[5]
                })
            
            conn.close()
            
            logger.info(f"Found {len(results)} related documents for {document_id}")
            return results
        except Exception as e:
            logger.error(f"Error getting related documents: {e}")
            return []
    
    def prune_memory(self, max_documents: int = 10000, 
                    retention_policy: str = 'least_accessed') -> int:
        """
        Prune memory to stay within limits.
        
        Args:
            max_documents: Maximum number of documents to keep
            retention_policy: Policy for deciding which documents to keep
                              ('least_accessed', 'oldest', 'custom')
            
        Returns:
            Number of documents removed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count documents
            cursor.execute('SELECT COUNT(*) FROM documents')
            count = cursor.fetchone()[0]
            
            if count <= max_documents:
                conn.close()
                logger.info(f"No pruning needed, document count ({count}) is below limit ({max_documents})")
                return 0
            
            # Calculate how many to remove
            to_remove = count - max_documents
            
            # Get IDs to remove based on policy
            if retention_policy == 'least_accessed':
                cursor.execute('''
                SELECT document_id FROM documents
                ORDER BY access_count ASC, last_accessed ASC
                LIMIT ?
                ''', (to_remove,))
            elif retention_policy == 'oldest':
                cursor.execute('''
                SELECT document_id FROM documents
                ORDER BY created_at ASC
                LIMIT ?
                ''', (to_remove,))
            else:
                # Custom policy could be implemented here
                conn.close()
                logger.warning(f"Unknown retention policy: {retention_policy}")
                return 0
            
            doc_ids_to_remove = [row[0] for row in cursor.fetchall()]
            
            # Remove documents and related data
            for doc_id in doc_ids_to_remove:
                cursor.execute('DELETE FROM document_vectors WHERE document_id = ?', (doc_id,))
                cursor.execute('DELETE FROM document_relationships WHERE source_document_id = ? OR target_document_id = ?', 
                              (doc_id, doc_id))
                cursor.execute('DELETE FROM documents WHERE document_id = ?', (doc_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Pruned {len(doc_ids_to_remove)} documents using policy '{retention_policy}'")
            return len(doc_ids_to_remove)
        except Exception as e:
            logger.error(f"Error pruning memory: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary of statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Document count
            cursor.execute('SELECT COUNT(*) FROM documents')
            stats['document_count'] = cursor.fetchone()[0]
            
            # Vector count
            cursor.execute('SELECT COUNT(*) FROM document_vectors')
            stats['vector_count'] = cursor.fetchone()[0]
            
            # Relationship count
            cursor.execute('SELECT COUNT(*) FROM document_relationships')
            stats['relationship_count'] = cursor.fetchone()[0]
            
            # Document types
            cursor.execute('SELECT document_type, COUNT(*) FROM documents GROUP BY document_type')
            stats['document_types'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Relationship types
            cursor.execute('SELECT relationship_type, COUNT(*) FROM document_relationships GROUP BY relationship_type')
            stats['relationship_types'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Most accessed documents
            cursor.execute('''
            SELECT document_id, title, access_count 
            FROM documents 
            ORDER BY access_count DESC 
            LIMIT 10
            ''')
            stats['most_accessed'] = [
                {'document_id': row[0], 'title': row[1], 'access_count': row[2]} 
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            logger.info("Retrieved memory system statistics")
            return stats
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}