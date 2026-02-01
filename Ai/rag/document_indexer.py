"""
Document Indexer for RAG system.

This module provides functionality to index documents by:
1. Extracting text from files
2. Chunking text into manageable pieces
3. Generating embeddings using Alpha API (from back-end)
4. Storing in vector database
"""
import sys
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add back-end to path for API imports
BACKEND_PATH = Path(__file__).parent.parent.parent / "back-end"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from utils.alpha_api import AlphaAPIClient, get_alpha_api_client
from .vector_db import VectorDBManager, get_vector_db_manager
from .document_processor import DocumentProcessor, get_document_processor

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """
    Document Indexer for RAG system.
    
    This class handles the complete document indexing pipeline:
    - Text extraction from files
    - Text chunking
    - Embedding generation via Alpha API (from back-end)
    - Storage in vector database
    """
    
    def __init__(
        self,
        vector_db: Optional[VectorDBManager] = None,
        document_processor: Optional[DocumentProcessor] = None,
        api_client: Optional[AlphaAPIClient] = None,
        embedding_model: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        batch_size: int = 10
    ):
        """
        Initialize the Document Indexer.
        
        Args:
            vector_db: VectorDBManager instance (uses singleton if not provided)
            document_processor: DocumentProcessor instance (uses singleton if not provided)
            api_client: AlphaAPIClient instance (uses singleton if not provided)
            embedding_model: Model name for embeddings
            chunk_size: Maximum size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            batch_size: Number of embeddings to generate in one API call
        """
        self.vector_db = vector_db or get_vector_db_manager()
        self.document_processor = document_processor or get_document_processor()
        self.api_client = api_client or get_alpha_api_client()
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        
        logger.info("DocumentIndexer initialized")
    
    def index_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index a single document file.
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata to include
            
        Returns:
            Dictionary with indexing results
        """
        # Process file into chunks
        chunks = self.document_processor.process_file(
            file_path,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            metadata=metadata
        )
        
        # Generate embeddings and store in vector DB
        return self._index_chunks(chunks)
    
    def index_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: str = "manual_entry"
    ) -> Dict[str, Any]:
        """
        Index a text string directly.
        
        Args:
            text: Text content to index
            metadata: Additional metadata to include
            doc_id: Document ID for this text
            
        Returns:
            Dictionary with indexing results
        """
        # Chunk text
        chunks_text = self.document_processor.chunk_text(
            text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        # Create chunk documents
        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                'chunk_id': i,
                'chunk_index': i,
                'total_chunks': len(chunks_text),
                'doc_id': doc_id
            })
            
            chunks.append({
                'content': chunk_text,
                'metadata': chunk_metadata,
                'id': f"{doc_id}_chunk_{i}"
            })
        
        # Generate embeddings and store in vector DB
        return self._index_chunks(chunks)
    
    def index_directory(
        self,
        directory_path: str,
        file_patterns: Optional[List[str]] = None,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Index all documents in a directory.
        
        Args:
            directory_path: Path to the directory
            file_patterns: List of file patterns to include (e.g., ['*.pdf', '*.txt'])
            recursive: Whether to search subdirectories
            
        Returns:
            Dictionary with indexing results
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all matching files
        if file_patterns:
            files = []
            for pattern in file_patterns:
                if recursive:
                    files.extend(directory.rglob(pattern))
                else:
                    files.extend(directory.glob(pattern))
        else:
            files = list(directory.rglob('*')) if recursive else list(directory.glob('*'))
        
        # Filter to only supported file types
        supported_extensions = set(self.document_processor.supported_extensions.keys())
        files = [f for f in files if f.suffix.lower() in supported_extensions]
        
        logger.info(f"Found {len(files)} files to index in {directory_path}")
        
        # Index each file
        total_chunks = 0
        failed_files = []
        
        for file_path in files:
            try:
                result = self.index_file(str(file_path))
                total_chunks += result['chunks_indexed']
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                failed_files.append({
                    'file': str(file_path),
                    'error': str(e)
                })
        
        return {
            'total_files': len(files),
            'successful_files': len(files) - len(failed_files),
            'failed_files': len(failed_files),
            'total_chunks_indexed': total_chunks,
            'failed_file_details': failed_files
        }
    
    def _index_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index a list of chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with indexing results
        """
        if not chunks:
            return {
                'chunks_indexed': 0,
                'total_chunks': 0
            }
        
        # Extract content and metadata
        texts = [chunk['content'] for chunk in chunks]
        ids = [chunk['id'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings in batches using Alpha API
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            try:
                response = self.api_client.embeddings(
                    input_data=batch_texts,
                    model=self.embedding_model
                )
                batch_embeddings = [item['embedding'] for item in response.get('data', [])]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                raise
        
        # Store in vector database
        self.vector_db.add_documents(
            documents=texts,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        logger.info(f"Indexed {len(chunks)} chunks in vector database")
        
        return {
            'chunks_indexed': len(chunks),
            'total_chunks': len(chunks)
        }
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the vector database.
        
        Args:
            doc_id: Document ID to delete (can be a pattern)
        """
        # Delete all chunks matching the document ID
        self.vector_db.delete(where={'doc_id': doc_id})
        logger.info(f"Deleted document {doc_id} from vector database")
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the vector database.
        
        Returns:
            Number of documents
        """
        return self.vector_db.count()
    
    def clear_index(self) -> None:
        """Clear all documents from the vector database."""
        self.vector_db.clear_collection()
        logger.info("Cleared all documents from vector database")


# Singleton instance
_document_indexer: Optional[DocumentIndexer] = None


def get_document_indexer(**kwargs) -> DocumentIndexer:
    """
    Get or create a singleton instance of DocumentIndexer.
    
    Returns:
        DocumentIndexer instance
    """
    global _document_indexer
    if _document_indexer is None:
        _document_indexer = DocumentIndexer(**kwargs)
    return _document_indexer
