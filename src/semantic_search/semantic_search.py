"""
Semantic Search and Analysis Module

This module provides advanced semantic search capabilities:
1. Semantic search using word embeddings and NLP
2. Context-aware relevance ranking
3. Entity recognition for companies, people, amounts, and dates
4. Thematic grouping of documents

Dependencies:
- nltk
- scikit-learn
- numpy
- spacy (with Swedish language model)
"""

import os
import re
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SemanticSearch:
    """Class for semantic search and analysis of documents."""
    
    def __init__(self, data_dir: str, language: str = "swedish"):
        """
        Initialize the Semantic Search.
        
        Args:
            data_dir (str): Directory containing indexed data
            language (str): Language for NLP processing ("swedish" or "english")
        """
        self.data_dir = data_dir
        self.language = language
        self.documents = {}
        self.metadata = {}
        self.vectorizer = None
        self.document_vectors = None
        self.kmeans = None
        self.clusters = None
        self.entities = {
            'companies': set(),
            'people': set(),
            'amounts': set(),
            'dates': set()
        }
        
        # Initialize NLP components
        self._initialize_nlp()
        
        # Load documents and metadata
        self._load_documents()
    
    def _initialize_nlp(self) -> None:
        """Initialize NLP components."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer")
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK stopwords")
            nltk.download('stopwords')
        
        # Set up stemmer and stopwords for the specified language
        if self.language == "swedish":
            self.stemmer = SnowballStemmer("swedish")
            try:
                self.stop_words = set(stopwords.words('swedish'))
            except:
                logger.warning("Swedish stopwords not available, using English")
                self.stop_words = set(stopwords.words('english'))
                # Add some common Swedish stopwords manually
                self.stop_words.update(['och', 'att', 'det', 'som', 'en', 'är', 'på', 'för', 'med', 'av'])
        else:
            self.stemmer = SnowballStemmer("english")
            self.stop_words = set(stopwords.words('english'))
        
        # Add domain-specific stopwords
        domain_stopwords = ['ab', 'inc', 'ltd', 'kb', 'hb', 'aktiebolag', 'handelsbolag', 'kommanditbolag']
        self.stop_words.update(domain_stopwords)
        
        # Try to load spaCy for entity recognition
        try:
            import spacy
            if self.language == "swedish":
                try:
                    self.nlp = spacy.load("sv_core_news_sm")
                    logger.info("Loaded Swedish spaCy model")
                except:
                    logger.warning("Swedish spaCy model not available, using English")
                    self.nlp = spacy.load("en_core_web_sm")
            else:
                self.nlp = spacy.load("en_core_web_sm")
            self.use_spacy = True
        except:
            logger.warning("spaCy not available, using regex-based entity recognition")
            self.use_spacy = False
    
    def _load_documents(self) -> None:
        """Load documents and metadata from data directory."""
        if not os.path.exists(self.data_dir):
            logger.error(f"Data directory not found: {self.data_dir}")
            return
        
        # Load metadata if available
        metadata_file = os.path.join(self.data_dir, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.metadata)} documents")
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
        
        # Load text files
        text_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
        logger.info(f"Found {len(text_files)} text files")
        
        for text_file in text_files:
            try:
                file_path = os.path.join(self.data_dir, text_file)
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                
                # Store document content
                self.documents[text_file] = content
                
                # Extract entities if not using spaCy
                if not self.use_spacy:
                    self._extract_entities_regex(text_file, content)
            except Exception as e:
                logger.error(f"Error loading {text_file}: {e}")
        
        logger.info(f"Loaded {len(self.documents)} documents")
        
        # Create document vectors
        self._create_document_vectors()
        
        # Perform clustering
        self._cluster_documents()
        
        # Extract entities using spaCy if available
        if self.use_spacy:
            self._extract_entities_spacy()
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for analysis.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(token) for token in tokens if token.isalpha() and token not in self.stop_words]
        
        # Join tokens back into text
        return ' '.join(tokens)
    
    def _create_document_vectors(self) -> None:
        """Create TF-IDF vectors for documents."""
        if not self.documents:
            logger.warning("No documents to vectorize")
            return
        
        # Preprocess documents
        preprocessed_docs = {doc_id: self._preprocess_text(content) for doc_id, content in self.documents.items()}
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Create document vectors
        try:
            doc_ids = list(preprocessed_docs.keys())
            doc_contents = [preprocessed_docs[doc_id] for doc_id in doc_ids]
            
            # Fit and transform
            self.document_vectors = self.vectorizer.fit_transform(doc_contents)
            
            logger.info(f"Created {self.document_vectors.shape[1]}-dimensional vectors for {len(doc_ids)} documents")
        except Exception as e:
            logger.error(f"Error creating document vectors: {e}")
    
    def _cluster_documents(self, n_clusters: int = 5) -> None:
        """
        Cluster documents using K-means.
        
        Args:
            n_clusters (int): Number of clusters
        """
        if self.document_vectors is None:
            logger.warning("No document vectors available for clustering")
            return
        
        try:
            # Determine optimal number of clusters (between 2 and 10)
            max_clusters = min(10, len(self.documents))
            if max_clusters < 2:
                logger.warning("Not enough documents for clustering")
                return
            
            # Use fixed number of clusters for simplicity
            n_clusters = min(n_clusters, max_clusters)
            
            # Perform K-means clustering
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.clusters = self.kmeans.fit_predict(self.document_vectors)
            
            # Create mapping from document ID to cluster
            doc_ids = list(self.documents.keys())
            self.doc_clusters = {doc_ids[i]: int(self.clusters[i]) for i in range(len(doc_ids))}
            
            # Create mapping from cluster to document IDs
            self.cluster_docs = {}
            for i, cluster in enumerate(self.clusters):
                cluster = int(cluster)
                if cluster not in self.cluster_docs:
                    self.cluster_docs[cluster] = []
                self.cluster_docs[cluster].append(doc_ids[i])
            
            logger.info(f"Clustered documents into {n_clusters} groups")
            
            # Extract cluster keywords
            self._extract_cluster_keywords()
        except Exception as e:
            logger.error(f"Error clustering documents: {e}")
    
    def _extract_cluster_keywords(self, top_n: int = 5) -> None:
        """
        Extract keywords for each cluster.
        
        Args:
            top_n (int): Number of top keywords to extract
        """
        if self.kmeans is None or self.vectorizer is None:
            return
        
        try:
            # Get cluster centers
            cluster_centers = self.kmeans.cluster_centers_
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Extract top keywords for each cluster
            self.cluster_keywords = {}
            for i, center in enumerate(cluster_centers):
                # Get indices of top features
                top_indices = center.argsort()[-top_n:][::-1]
                
                # Get corresponding feature names
                keywords = [feature_names[idx] for idx in top_indices]
                
                self.cluster_keywords[i] = keywords
            
            logger.info(f"Extracted {top_n} keywords for each cluster")
        except Exception as e:
            logger.error(f"Error extracting cluster keywords: {e}")
    
    def _extract_entities_spacy(self) -> None:
        """Extract entities using spaCy."""
        if not self.use_spacy:
            return
        
        try:
            for doc_id, content in self.documents.items():
                # Process with spaCy
                doc = self.nlp(content[:10000])  # Limit to first 10000 chars for performance
                
                # Extract entities
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "ORGANIZATION"]:
                        self.entities['companies'].add(ent.text.strip())
                    elif ent.label_ in ["PERSON"]:
                        self.entities['people'].add(ent.text.strip())
                    elif ent.label_ in ["MONEY", "CARDINAL"]:
                        # Clean up amount
                        amount = re.sub(r'[^\d.,]', '', ent.text)
                        if amount:
                            self.entities['amounts'].add(amount)
                    elif ent.label_ in ["DATE", "TIME"]:
                        self.entities['dates'].add(ent.text.strip())
            
            logger.info(f"Extracted entities: {len(self.entities['companies'])} companies, "
                       f"{len(self.entities['people'])} people, "
                       f"{len(self.entities['amounts'])} amounts, "
                       f"{len(self.entities['dates'])} dates")
        except Exception as e:
            logger.error(f"Error extracting entities with spaCy: {e}")
    
    def _extract_entities_regex(self, doc_id: str, content: str) -> None:
        """
        Extract entities using regex patterns.
        
        Args:
            doc_id (str): Document ID
            content (str): Document content
        """
        # Extract companies (look for AB, KB, HB, Inc, Ltd, etc.)
        company_pattern = r'([A-Za-zåäöÅÄÖ0-9\s]{2,}(?:AB|HB|KB|Inc|Ltd|Aktiebolag|Handelsbolag|Kommanditbolag))'
        companies = re.findall(company_pattern, content)
        for company in companies:
            self.entities['companies'].add(company.strip())
        
        # Extract amounts (look for currency patterns)
        amount_pattern = r'(\d{1,3}(?:[ \.,]\d{3})*(?:[\.,]\d{2})?)\s*(?:kr|sek|:-)'
        amounts = re.findall(amount_pattern, content.lower())
        for amount in amounts:
            # Clean up amount
            amount = re.sub(r'[^\d.,]', '', amount)
            if amount:
                self.entities['amounts'].add(amount)
        
        # Extract dates
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # ISO format
            r'(\d{1,2}/\d{1,2}/\d{4})',  # DD/MM/YYYY
            r'(\d{1,2}\.\d{1,2}\.\d{4})'  # DD.MM.YYYY
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, content)
            for date in dates:
                self.entities['dates'].add(date)
    
    def search(self, query: str, fuzzy: bool = True, semantic: bool = True,
              metadata_filter: Optional[Dict[str, Any]] = None,
              top_n: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for documents matching the query.
        
        Args:
            query (str): Search query
            fuzzy (bool): Whether to use fuzzy matching
            semantic (bool): Whether to use semantic search
            metadata_filter (Dict[str, Any]): Filters to apply on metadata
            top_n (int): Number of top results to return
            
        Returns:
            List[Tuple[str, float, Dict[str, Any]]]: List of matching documents with relevance scores and metadata
        """
        if not self.documents:
            logger.warning("No documents to search")
            return []
        
        # Apply metadata filters if specified
        doc_ids = list(self.documents.keys())
        if metadata_filter and self.metadata:
            filtered_ids = []
            for doc_id in doc_ids:
                if doc_id in self.metadata:
                    doc_metadata = self.metadata[doc_id]
                    include = True
                    for key, value in metadata_filter.items():
                        if key not in doc_metadata or doc_metadata[key] != value:
                            include = False
                            break
                    if include:
                        filtered_ids.append(doc_id)
            doc_ids = filtered_ids
        
        if not doc_ids:
            logger.warning("No documents match the metadata filter")
            return []
        
        # Perform exact search
        exact_matches = []
        for doc_id in doc_ids:
            content = self.documents[doc_id].lower()
            if query.lower() in content:
                # Count occurrences for relevance
                count = content.count(query.lower())
                score = 1.0 + (count * 0.01)
                metadata = self.metadata.get(doc_id, {})
                exact_matches.append((doc_id, score, metadata))
        
        # Perform fuzzy search if enabled and no exact matches found
        fuzzy_matches = []
        if fuzzy and not exact_matches:
            from difflib import SequenceMatcher
            
            for doc_id in doc_ids:
                content = self.documents[doc_id].lower()
                words = content.split()
                
                # Calculate best match for each word
                best_match = 0
                for word in words:
                    similarity = SequenceMatcher(None, query.lower(), word).ratio()
                    if similarity > best_match:
                        best_match = similarity
                
                # If match is good enough, add to results
                if best_match > 0.8:
                    metadata = self.metadata.get(doc_id, {})
                    fuzzy_matches.append((doc_id, best_match, metadata))
        
        # Perform semantic search if enabled
        semantic_matches = []
        if semantic and self.vectorizer is not None and self.document_vectors is not None:
            try:
                # Preprocess query
                query_preprocessed = self._preprocess_text(query)
                
                # Transform query to vector
                query_vector = self.vectorizer.transform([query_preprocessed])
                
                # Calculate similarity with document vectors
                similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
                
                # Get document IDs and scores
                all_doc_ids = list(self.documents.keys())
                for i, score in enumerate(similarities):
                    doc_id = all_doc_ids[i]
                    if doc_id in doc_ids and score > 0.1:  # Only include if passes metadata filter
                        metadata = self.metadata.get(doc_id, {})
                        semantic_matches.append((doc_id, float(score), metadata))
            except Exception as e:
                logger.error(f"Error in semantic search: {e}")
        
        # Combine results
        all_matches = exact_matches + fuzzy_matches + semantic_matches
        
        # Remove duplicates (keep highest score)
        unique_matches = {}
        for doc_id, score, metadata in all_matches:
            if doc_id not in unique_matches or score > unique_matches[doc_id][0]:
                unique_matches[doc_id] = (score, metadata)
        
        # Convert back to list and sort by score
        results = [(doc_id, score, metadata) for doc_id, (score, metadata) in unique_matches.items()]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_n]
    
    def get_document_clusters(self) -> Dict[int, List[str]]:
        """
        Get document clusters.
        
        Returns:
            Dict[int, List[str]]: Mapping from cluster ID to list of document IDs
        """
        return self.cluster_docs if hasattr(self, 'cluster_docs') else {}
    
    def get_cluster_keywords(self) -> Dict[int, List[str]]:
        """
        Get cluster keywords.
        
        Returns:
            Dict[int, List[str]]: Mapping from cluster ID to list of keywords
        """
        return self.cluster_keywords if hasattr(self, 'cluster_keywords') else {}
    
    def get_entities(self) -> Dict[str, Set[str]]:
        """
        Get extracted entities.
        
        Returns:
            Dict[str, Set[str]]: Mapping from entity type to set of entities
        """
        return self.entities
    
    def get_related_terms(self, term: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get terms related to the input term based on co-occurrence.
        
        Args:
            term (str): Input term
            top_n (int): Number of top related terms to return
            
        Returns:
            List[Tuple[str, float]]: List of related terms with similarity scores
        """
        if not self.documents or not self.vectorizer:
            return []
        
        try:
            # Get term index in the vocabulary
            term = self.stemmer.stem(term.lower())
            vocabulary = self.vectorizer.get_feature_names_out()
            
            if term not in vocabulary:
                # Find closest term in vocabulary
                from difflib import SequenceMatcher
                best_match = None
                best_score = 0
                
                for word in vocabulary:
                    score = SequenceMatcher(None, term, word).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = word
                
                if best_score > 0.8:
                    term = best_match
                else:
                    return []
            
            # Get term index
            term_idx = list(vocabulary).index(term)
            
            # Get co-occurrence scores
            term_vector = self.document_vectors[:, term_idx].toarray().flatten()
            
            # Calculate similarity with other terms
            related_terms = []
            for i, word in enumerate(vocabulary):
                if i != term_idx:
                    word_vector = self.document_vectors[:, i].toarray().flatten()
                    similarity = np.dot(term_vector, word_vector) / (np.linalg.norm(term_vector) * np.linalg.norm(word_vector) + 1e-8)
                    if similarity > 0:
                        related_terms.append((word, float(similarity)))
            
            # Sort by similarity
            related_terms.sort(key=lambda x: x[1], reverse=True)
            
            return related_terms[:top_n]
        except Exception as e:
            logger.error(f"Error getting related terms: {e}")
            return []
    
    def analyze_trends(self, field: str = 'total_amount', 
                      group_by: str = 'date',
                      document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze trends in metadata.
        
        Args:
            field (str): Field to analyze
            group_by (str): Field to group by
            document_type (str): Type of documents to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        if not self.metadata:
            logger.warning("No metadata available for trend analysis")
            return {}
        
        try:
            # Filter by document type if specified
            filtered_metadata = {}
            for doc_id, metadata in self.metadata.items():
                if document_type is None or metadata.get('document_type') == document_type:
                    filtered_metadata[doc_id] = metadata
            
            if not filtered_metadata:
                logger.warning(f"No documents match the filter: document_type={document_type}")
                return {}
            
            # Check if fields exist in metadata
            if not any(field in metadata for metadata in filtered_metadata.values()):
                logger.warning(f"Field '{field}' not found in metadata")
                return {}
            
            if not any(group_by in metadata for metadata in filtered_metadata.values()):
                logger.warning(f"Field '{group_by}' not found in metadata")
                return {}
            
            # Group data
            grouped_data = {}
            for doc_id, metadata in filtered_metadata.items():
                if field in metadata and group_by in metadata:
                    group_value = metadata[group_by]
                    field_value = metadata[field]
                    
                    # Convert to appropriate type
                    if isinstance(field_value, str) and field_value.replace('.', '').isdigit():
                        field_value = float(field_value)
                    
                    if group_value not in grouped_data:
                        grouped_data[group_value] = []
                    
                    grouped_data[group_value].append(field_value)
            
            # Calculate statistics for each group
            results = {}
            for group_value, values in grouped_data.items():
                if all(isinstance(v, (int, float)) for v in values):
                    results[group_value] = {
                        'count': len(values),
                        'sum': sum(values),
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }
                else:
                    # For non-numeric values, count occurrences
                    counter = Counter(values)
                    results[group_value] = {
                        'count': len(values),
                        'most_common': counter.most_common(3)
                    }
            
            return results
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python semantic_search.py <data_dir>")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    search = SemanticSearch(data_dir)
    
    # Test search
    query = "faktura"
    results = search.search(query, semantic=True)
    
    print(f"Search results for '{query}':")
    for doc_id, score, metadata in results:
        print(f"  {doc_id} (score: {score:.2f})")
        if metadata:
            print(f"    {metadata}")
    
    # Test clustering
    clusters = search.get_document_clusters()
    keywords = search.get_cluster_keywords()
    
    print("\nDocument clusters:")
    for cluster_id, doc_ids in clusters.items():
        print(f"  Cluster {cluster_id} ({len(doc_ids)} documents):")
        if cluster_id in keywords:
            print(f"    Keywords: {', '.join(keywords[cluster_id])}")
        print(f"    Documents: {', '.join(doc_ids[:5])}{'...' if len(doc_ids) > 5 else ''}")
    
    # Test entity extraction
    entities = search.get_entities()
    
    print("\nExtracted entities:")
    for entity_type, entity_set in entities.items():
        print(f"  {entity_type.capitalize()}: {len(entity_set)}")
        if entity_set:
            print(f"    Examples: {', '.join(list(entity_set)[:5])}")
    
    # Test related terms
    related = search.get_related_terms("faktura")
    
    print("\nTerms related to 'faktura':")
    for term, score in related:
        print(f"  {term} (similarity: {score:.2f})")
    
    # Test trend analysis
    trends = search.analyze_trends(field='total_amount', group_by='date')
    
    print("\nTrend analysis:")
    for group, stats in trends.items():
        print(f"  {group}:")
        for stat, value in stats.items():
            print(f"    {stat}: {value}")