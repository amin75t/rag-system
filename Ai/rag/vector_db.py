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

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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
        persist_directory: str = None,
        embedding_function=None
    ):
        """
        Initialize the Vector DB Manager.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector database (optional, uses env var if not provided)
            embedding_function: Custom embedding function (optional)
        """
        self.collection_name = collection_name
        # Use environment variable if persist_directory not provided
        if persist_directory is None:
            persist_directory = os.getenv('VECTOR_DB_PATH', './vector_db')
        self.persist_directory = Path(persist_directory)
        self.embedding_function = embedding_function
        
        # DEBUG: Log initialization details
        logger.info("=" * 70)
        logger.info("VectorDBManager Initialization")
        logger.info("=" * 70)
        logger.info(f"Collection name: {collection_name}")
        logger.info(f"Persist directory (raw): {persist_directory}")
        logger.info(f"Persist directory (absolute): {self.persist_directory.absolute()}")
        logger.info(f"Current working directory: {Path.cwd().absolute()}")
        logger.info(f"VECTOR_DB_PATH env var: {os.getenv('VECTOR_DB_PATH', 'NOT SET')}")
        
        # Check if directory exists and what's in it
        if self.persist_directory.exists():
            logger.info(f"Persist directory EXISTS")
            logger.info(f"Contents of persist directory:")
            for item in self.persist_directory.iterdir():
                logger.info(f"  - {item.name} (dir={item.is_dir()})")
        else:
            logger.info(f"Persist directory DOES NOT EXIST - will be created")
        
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
        
        # DEBUG: List all collections before accessing
        try:
            all_collections = self.client.list_collections()
            logger.info(f"Existing collections in database: {[c.name for c in all_collections]}")
        except Exception as e:
            logger.warning(f"Could not list collections: {e}")
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        logger.info(f"VectorDBManager initialized with collection '{collection_name}'")
        logger.info("=" * 70)
    
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


def inspect_vector_db_directory(directory_path: str) -> Dict[str, Any]:
    """
    Inspect a vector database directory to understand its structure.
    
    This helps debug issues with ChromaDB database locations.
    
    Args:
        directory_path: Path to inspect
        
    Returns:
        Dictionary with inspection results
    """
    import glob
    path = Path(directory_path)
    
    result = {
        "path": str(path.absolute()),
        "exists": path.exists(),
        "is_directory": path.is_dir(),
        "contents": [],
        "chroma_collections": [],
        "potential_chroma_dirs": []
    }
    
    if not path.exists():
        return result
    
    # List all contents
    for item in path.iterdir():
        item_info = {
            "name": item.name,
            "is_dir": item.is_dir(),
            "size": item.stat().st_size if item.is_file() else None
        }
        result["contents"].append(item_info)
        
        # Check for ChromaDB collection directories (UUID pattern)
        if item.is_dir() and len(item.name) == 36:  # UUID length
            result["potential_chroma_dirs"].append(item.name)
            
            # Check for ChromaDB files
            chroma_files = ["chroma.sqlite3", "data_level0.bin", "header.bin", "length.bin", "link_lists.bin"]
            found_files = []
            for cf in chroma_files:
                if (item / cf).exists():
                    found_files.append(cf)
            
            if found_files:
                result["chroma_collections"].append({
                    "uuid": item.name,
                    "files": found_files
                })
    
    return result


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
