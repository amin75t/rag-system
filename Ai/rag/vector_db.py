"""
Vector Database Manager using ChromaDB.

This module provides a wrapper around ChromaDB for storing
and retrieving document embeddings.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class VectorDBManager:
    """
    Vector Database Manager using ChromaDB.
    
    This class manages document embeddings storage and retrieval
    using ChromaDB as the vector database backend.
    """
    
    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str = "./vector_db",
        embedding_function=None
    ):
        """
        Initialize the Vector DB Manager.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector database
            embedding_function: Custom embedding function (optional)
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.embedding_function = embedding_function
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"VectorDBManager initialized with collection '{collection_name}'")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection '{self.collection_name}'")
            return collection
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG system"}
            )
            logger.info(f"Created new collection '{self.collection_name}'")
            return collection
    
    def add_documents(
        self,
        documents: List[str],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of document texts
            ids: List of unique document IDs
            embeddings: Pre-computed embeddings (optional)
            metadatas: List of metadata dictionaries (optional)
        """
        if len(documents) != len(ids):
            raise ValueError("Number of documents must match number of IDs")
        
        if metadatas and len(metadatas) != len(documents):
            raise ValueError("Number of metadatas must match number of documents")
        
        # Add documents to collection
        self.collection.add(
            documents=documents,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to vector database")
    
    def query(
        self,
        query_embeddings: Optional[List[List[float]]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector database for similar documents.
        
        Args:
            query_embeddings: Query embeddings (optional)
            query_texts: Query texts (optional, will be embedded if provided)
            n_results: Number of results to return
            where: Filter on metadata
            where_document: Filter on document content
            
        Returns:
            Dictionary with query results
        """
        results = self.collection.query(
            query_embeddings=query_embeddings,
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        logger.info(f"Query returned {len(results.get('ids', [[]])[0])} results")
        return results
    
    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get documents from the vector database.
        
        Args:
            ids: List of document IDs to retrieve
            where: Filter on metadata
            limit: Maximum number of results
            
        Returns:
            Dictionary with documents
        """
        results = self.collection.get(
            ids=ids,
            where=where,
            limit=limit
        )
        
        return results
    
    def update(
        self,
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[str]] = None
    ) -> None:
        """
        Update documents in the vector database.
        
        Args:
            ids: List of document IDs to update
            embeddings: New embeddings
            metadatas: New metadata
            documents: New document texts
        """
        self.collection.update(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        logger.info(f"Updated {len(ids)} documents in vector database")
    
    def delete(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Delete documents from the vector database.
        
        Args:
            ids: List of document IDs to delete
            where: Filter on metadata
            where_document: Filter on document content
        """
        self.collection.delete(
            ids=ids,
            where=where,
            where_document=where_document
        )
        
        logger.info("Deleted documents from vector database")
    
    def count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Document embeddings for RAG system"}
        )
        
        logger.info(f"Cleared collection '{self.collection_name}'")
    
    def reset_database(self) -> None:
        """Reset the entire vector database."""
        self.client.reset()
        self.collection = self._get_or_create_collection()
        
        logger.info("Reset vector database")


# Singleton instance
_vector_db_manager: Optional[VectorDBManager] = None


def get_vector_db_manager(**kwargs) -> VectorDBManager:
    """
    Get or create a singleton instance of VectorDBManager.
    
    Returns:
        VectorDBManager instance
    """
    global _vector_db_manager
    if _vector_db_manager is None:
        _vector_db_manager = VectorDBManager(**kwargs)
    return _vector_db_manager
