"""
Hugging Face Models Integration

This module provides functionality for integrating and using Hugging Face models
for various NLP tasks such as embeddings, classification, and question answering.
"""

import os
import logging
import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union
from transformers import (
    AutoTokenizer, 
    AutoModel, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering,
    pipeline
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HuggingFaceIntegration:
    """Class for integrating and using Hugging Face models."""
    
    def __init__(self, cache_dir: str = "./models", device: str = None):
        """
        Initialize Hugging Face models integration.
        
        Args:
            cache_dir: Directory to cache models
            device: Device to run models on ('cpu', 'cuda:0', etc.)
                    If None, will use CUDA if available
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        logger.info(f"Initialized Hugging Face integration with device: {self.device}")
    
    def load_model(self, task: str, model_name: str) -> bool:
        """
        Load a model for a specific task.
        
        Args:
            task: Task name ('embeddings', 'ner', 'classification', 'qa', etc.)
            model_name: Hugging Face model name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading model {model_name} for task: {task}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=self.cache_dir)
            self.tokenizers[task] = tokenizer
            
            # Load model based on task
            if task == 'embeddings':
                model = AutoModel.from_pretrained(model_name, cache_dir=self.cache_dir)
                self.models[task] = model.to(self.device)
            elif task == 'classification':
                model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=self.cache_dir)
                self.models[task] = model.to(self.device)
            elif task == 'ner':
                model = AutoModelForTokenClassification.from_pretrained(model_name, cache_dir=self.cache_dir)
                self.models[task] = model.to(self.device)
            elif task == 'qa':
                model = AutoModelForQuestionAnswering.from_pretrained(model_name, cache_dir=self.cache_dir)
                self.models[task] = model.to(self.device)
            else:
                logger.warning(f"Unknown task: {task}, using pipeline")
                self.pipelines[task] = pipeline(
                    task,
                    model=model_name,
                    device=0 if self.device.startswith('cuda') else -1
                )
                return True
            
            # Create pipeline
            self.pipelines[task] = pipeline(
                task if task != 'embeddings' else 'feature-extraction',
                model=self.models[task],
                tokenizer=self.tokenizers[task],
                device=0 if self.device.startswith('cuda') else -1
            )
            
            logger.info(f"Successfully loaded model for task: {task}")
            return True
        except Exception as e:
            logger.error(f"Error loading model for {task}: {e}")
            return False
    
    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Get embeddings for texts.
        
        Args:
            texts: Text or list of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        if 'embeddings' not in self.models:
            raise ValueError("Embeddings model not loaded. Call load_model('embeddings', model_name) first.")
        
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        # Get embeddings
        tokenizer = self.tokenizers['embeddings']
        model = self.models['embeddings']
        
        embeddings = []
        
        with torch.no_grad():
            for text in texts:
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                outputs = model(**inputs)
                
                # Use mean of last hidden state as embedding
                embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                embeddings.append(embedding[0])
        
        return np.array(embeddings)
    
    def classify_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Classify text using loaded classification model.
        
        Args:
            text: Text to classify
            
        Returns:
            List of classification results with labels and scores
        """
        if 'classification' not in self.pipelines:
            raise ValueError("Classification model not loaded. Call load_model('classification', model_name) first.")
        
        logger.info(f"Classifying text: {text[:50]}...")
        return self.pipelines['classification'](text)
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of extracted entities with type, text, and position
        """
        if 'ner' not in self.pipelines:
            raise ValueError("NER model not loaded. Call load_model('ner', model_name) first.")
        
        logger.info(f"Extracting entities from text: {text[:50]}...")
        return self.pipelines['ner'](text)
    
    def answer_question(self, question: str, context: str) -> Dict[str, Any]:
        """
        Answer a question based on context.
        
        Args:
            question: Question to answer
            context: Context to extract answer from
            
        Returns:
            Answer with score and position
        """
        if 'qa' not in self.pipelines:
            raise ValueError("QA model not loaded. Call load_model('qa', model_name) first.")
        
        logger.info(f"Answering question: {question}")
        return self.pipelines['qa'](question=question, context=context)
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            
        Returns:
            Summarized text
        """
        if 'summarization' not in self.pipelines:
            logger.info("Loading summarization model")
            self.pipelines['summarization'] = pipeline(
                'summarization', 
                device=0 if self.device.startswith('cuda') else -1
            )
        
        logger.info(f"Summarizing text of length {len(text)}")
        result = self.pipelines['summarization'](
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        
        return result[0]['summary_text']
    
    def generate_text(self, prompt: str, max_length: int = 100) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: Text prompt to generate from
            max_length: Maximum length of generated text
            
        Returns:
            Generated text
        """
        if 'text-generation' not in self.pipelines:
            logger.info("Loading text generation model")
            self.pipelines['text-generation'] = pipeline(
                'text-generation', 
                device=0 if self.device.startswith('cuda') else -1
            )
        
        logger.info(f"Generating text from prompt: {prompt[:50]}...")
        result = self.pipelines['text-generation'](
            prompt, 
            max_length=max_length, 
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        
        return result[0]['generated_text']
    
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = "en") -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if None)
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        task_name = f"translation_{source_lang}_to_{target_lang}" if source_lang else f"translation_to_{target_lang}"
        
        if task_name not in self.pipelines:
            logger.info(f"Loading translation model for {task_name}")
            try:
                self.pipelines[task_name] = pipeline(
                    task_name, 
                    device=0 if self.device.startswith('cuda') else -1
                )
            except Exception as e:
                logger.error(f"Error loading translation model: {e}")
                raise ValueError(f"Translation from {source_lang} to {target_lang} not supported")
        
        logger.info(f"Translating text to {target_lang}")
        result = self.pipelines[task_name](text)
        
        if isinstance(result, list):
            return result[0]['translation_text']
        return result['translation_text']
    
    def batch_process(self, task: str, texts: List[str], **kwargs) -> List[Any]:
        """
        Process a batch of texts with the specified task.
        
        Args:
            task: Task to perform
            texts: List of texts to process
            **kwargs: Additional arguments for the task
            
        Returns:
            List of results
        """
        if task not in self.pipelines:
            raise ValueError(f"Task {task} not loaded. Call load_model('{task}', model_name) first.")
        
        logger.info(f"Batch processing {len(texts)} texts with task: {task}")
        return self.pipelines[task](texts, **kwargs)
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get information about available models.
        
        Returns:
            Dictionary of task -> list of model names
        """
        return {
            'embeddings': ['sentence-transformers/all-MiniLM-L6-v2', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'],
            'classification': ['distilbert-base-uncased-finetuned-sst-2-english', 'nlptown/bert-base-multilingual-uncased-sentiment'],
            'ner': ['dbmdz/bert-large-cased-finetuned-conll03-english', 'dslim/bert-base-NER'],
            'qa': ['distilbert-base-cased-distilled-squad', 'deepset/roberta-base-squad2'],
            'summarization': ['facebook/bart-large-cnn', 'google/pegasus-xsum'],
            'translation': ['Helsinki-NLP/opus-mt-en-sv', 'Helsinki-NLP/opus-mt-sv-en']
        }