"""
Document Indexer for RAG system.

This module provides functionality to index documents by:
1. Extracting text from files
2. Chunking text into manageable pieces
3. Generating embeddings using Alpha API (from back-end)
4. Storing in vector database

Enhanced with:
- Detailed logging for each processing step
- Memory management (4GB RAM limit)
- Streaming processing for large documents
"""
import sys
import os
import logging
import gc
import psutil
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add back-end to path for API imports
BACKEND_PATH = Path(__file__).parent.parent.parent / "back-end"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from utils.alpha_api import AlphaAPIClient, get_alpha_api_client
from .vector_db import VectorDBManager, get_vector_db_manager
from .document_processor import DocumentProcessor, get_document_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Memory limit: 4GB in bytes
MAX_MEMORY_BYTES = 4 * 1024 * 1024 * 1024  # 4GB


# ==================== Memory Management Functions ====================

def get_memory_usage() -> int:
    """Get current memory usage in bytes."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def log_memory_usage(step_name: str):
    """Log current memory usage with step name."""
    mem_bytes = get_memory_usage()
    mem_mb = mem_bytes / (1024 * 1024)
    mem_gb = mem_bytes / (1024 * 1024 * 1024)
    logger.info(f"[MEMORY] {step_name}: {mem_mb:.2f} MB ({mem_gb:.3f} GB)")
    return mem_bytes


def check_memory_limit(step_name: str) -> bool:
    """
    Check if memory usage is within the 4GB limit.
    
    Returns:
        True if within limit, False if approaching limit
    """
    current_mem = get_memory_usage()
    usage_percent = (current_mem / MAX_MEMORY_BYTES) * 100
    
    logger.info(f"[MEMORY CHECK] {step_name}: {usage_percent:.2f}% of 4GB limit")
    
    if usage_percent > 90:
        logger.warning(f"[MEMORY WARNING] Approaching 4GB limit! Current: {usage_percent:.2f}%")
        return False
    elif usage_percent > 75:
        logger.warning(f"[MEMORY ALERT] Memory usage high: {usage_percent:.2f}%")
        return True
    else:
        return True


def force_garbage_collection(step_name: str):
    """Force garbage collection and log memory before/after."""
    logger.info(f"[GC] Starting garbage collection at step: {step_name}")
    mem_before = get_memory_usage()
    
    gc.collect()
    
    mem_after = get_memory_usage()
    mem_freed = (mem_before - mem_after) / (1024 * 1024)
    logger.info(f"[GC] Freed {mem_freed:.2f} MB ({mem_before/(1024*1024):.2f}MB -> {mem_after/(1024*1024):.2f}MB)")


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
        batch_size: int = 10,
        processing_batch_size: int = 100
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
            processing_batch_size: Number of chunks to process in memory at once (for RAM efficiency)
        """
        self.vector_db = vector_db or get_vector_db_manager()
        self.document_processor = document_processor or get_document_processor()
        self.api_client = api_client or get_alpha_api_client()
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size
        self.processing_batch_size = processing_batch_size
        
        logger.info("=" * 60)
        logger.info("[INIT] Initializing DocumentIndexer")
        
        log_memory_usage("Before initialization")
        
        logger.info(f"[INIT] Chunk size: {chunk_size}, Overlap: {chunk_overlap}")
        logger.info(f"[INIT] Batch size: {batch_size}, Processing batch size: {processing_batch_size}")
        logger.info(f"[INIT] Embedding model: {embedding_model or 'default'}")
        
        log_memory_usage("After initialization")
        
        logger.info("=" * 60)
    
    def index_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        save_chunks_to_disk: bool = True,
        chunks_output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Index a single document file with detailed logging.
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata to include
            
        Returns:
            Dictionary with indexing results
        """
        logger.info("=" * 60)
        logger.info(f"[INDEX FILE] Starting file indexing")
        logger.info(f"File: {file_path}")
        
        log_memory_usage("Start of index_file")
        
        start_time = time.time()
        
        # Process file into chunks (with streaming to disk)
        chunks = self.document_processor.process_file(
            file_path,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            metadata=metadata,
            save_chunks_to_disk=save_chunks_to_disk
        )
        
        # Generate embeddings and store in vector DB
        result = self._index_chunks(chunks)
        
        indexing_time = time.time() - start_time
        logger.info(f"[INDEX FILE] File indexing completed in {indexing_time:.2f} seconds")
        logger.info(f"[INDEX FILE] Total chunks indexed: {result.get('chunks_indexed', 0)}")
        
        log_memory_usage("End of index_file")
        
        logger.info("=" * 60)
        
        return result
    
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
        Index chunks in memory-efficient batches to prevent OOM errors.
        
        Processes chunks in smaller batches to maintain constant memory usage:
        - Generates embeddings for each batch via API
        - Immediately inserts batch into ChromaDB
        - Clears batch variables and forces garbage collection
        - Continues processing even if individual batches fail
        
        Args:
            chunks: List of chunk dictionaries with 'content', 'id', and 'metadata' keys
            
        Returns:
            Dictionary with indexing results including success rate and failed batches
        """
        if not chunks:
            return {
                'chunks_indexed': 0,
                'total_chunks': 0,
                'failed_batches': 0,
                'success_rate': 1.0
            }
        
        total_chunks = len(chunks)
        indexed_chunks = 0
        failed_batches = []
        
        logger.info(f"[EMBEDDING] Processing batch size: {self.processing_batch_size}")
        logger.info(f"[EMBEDDING] API batch size: {self.batch_size}")
        logger.info(f"[EMBEDDING] Estimated batches: {(total_chunks + self.processing_batch_size - 1) // self.processing_batch_size}")
        
        start_time = time.time()
        
        # Process chunks in batches to maintain constant memory usage
        for batch_start in range(0, total_chunks, self.processing_batch_size):
            batch_end = min(batch_start + self.processing_batch_size, total_chunks)
            batch_chunks = chunks[batch_start:batch_end]
            batch_number = batch_start // self.processing_batch_size + 1
            
            logger.info(f"[EMBEDDING] === Batch {batch_number}/{(total_chunks + self.processing_batch_size - 1) // self.processing_batch_size} ===")
            logger.info(f"[EMBEDDING] Processing chunks {batch_start}-{batch_end-1} ({len(batch_chunks)} chunks)")
            
            log_memory_usage(f"Before batch {batch_number}")
            
            # Check memory before processing batch
            if not check_memory_limit(f"Before batch {batch_number}"):
                logger.warning(f"[EMBEDDING] Memory high before batch {batch_number}, forcing GC")
                force_garbage_collection(f"Pre-batch {batch_number}")
            
            try:
                # Extract batch data
                batch_texts = [chunk['content'] for chunk in batch_chunks]
                batch_ids = [chunk['id'] for chunk in batch_chunks]
                batch_metadatas = [chunk['metadata'] for chunk in batch_chunks]
                
                logger.info(f"[EMBEDDING] Extracted batch data: {len(batch_texts)} texts, {len(batch_ids)} IDs, {len(batch_metadatas)} metadatas")
                
                # Generate embeddings for this batch only
                batch_embeddings = []
                api_batches = (len(batch_texts) + self.batch_size - 1) // self.batch_size
                logger.info(f"[EMBEDDING] Will make {api_batches} API calls for this batch")
                
                for i in range(0, len(batch_texts), self.batch_size):
                    api_batch_texts = batch_texts[i:i + self.batch_size]
                    api_batch_num = i // self.batch_size + 1
                    
                    logger.info(f"[EMBEDDING] API call {api_batch_num}/{api_batches}: processing {len(api_batch_texts)} texts")
                    
                    try:
                        response = self.api_client.embeddings(
                            input_data=api_batch_texts,
                            model=self.embedding_model
                        )
                        api_batch_embeddings = [item['embedding'] for item in response.get('data', [])]
                        batch_embeddings.extend(api_batch_embeddings)
                        logger.info(f"[EMBEDDING] API call {api_batch_num} successful: received {len(api_batch_embeddings)} embeddings")
                    except Exception as e:
                        logger.error(f"[EMBEDDING] Error generating embeddings for API batch {i}: {e}")
                        raise
                
                # Immediately insert this batch into ChromaDB
                logger.info(f"[EMBEDDING] Inserting {len(batch_texts)} chunks into vector database")
                self.vector_db.collection.add(
                    documents=batch_texts,
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                
                indexed_chunks += len(batch_chunks)
                progress = (indexed_chunks / total_chunks) * 100
                logger.info(f"[EMBEDDING] Successfully indexed batch {batch_number}: {len(batch_chunks)} chunks (total: {indexed_chunks}/{total_chunks}, {progress:.1f}%)")
                
                # Clear batch variables to free memory
                del batch_texts, batch_ids, batch_metadatas, batch_embeddings, batch_chunks
                
                # Force garbage collection to free memory immediately
                force_garbage_collection(f"Post-batch {batch_number}")
                
                log_memory_usage(f"After batch {batch_number}")
                
            except Exception as e:
                error_msg = f"Failed to process batch {batch_number} (chunks {batch_start}-{batch_end-1}): {e}"
                logger.error(f"[EMBEDDING ERROR] {error_msg}")
                failed_batches.append({
                    'batch_number': batch_number,
                    'batch_start': batch_start,
                    'batch_end': batch_end,
                    'error': str(e)
                })
                
                # Continue with next batch instead of failing completely
                logger.warning(f"[EMBEDDING] Continuing to next batch despite error")
                continue
        
        indexing_time = time.time() - start_time
        
        logger.info(f"[EMBEDDING] === Embedding and indexing completed ===")
        logger.info(f"[EMBEDDING] Total time: {indexing_time:.2f} seconds")
        logger.info(f"[EMBEDDING] Indexed: {indexed_chunks}/{total_chunks} chunks successfully")
        logger.info(f"[EMBEDDING] Success rate: {(indexed_chunks / total_chunks * 100):.1f}%")
        logger.info(f"[EMBEDDING] Processing rate: {indexed_chunks / indexing_time:.0f} chunks/sec")
        
        if failed_batches:
            logger.warning(f"[EMBEDDING] Failed batches: {len(failed_batches)}")
            for batch in failed_batches:
                logger.warning(f"[EMBEDDING]   Batch {batch['batch_number']} (chunks {batch['batch_start']}-{batch['batch_end']-1}): {batch['error']}")
        
        log_memory_usage("End of _index_chunks")
        
        # Final GC check
        if not check_memory_limit("End of _index_chunks"):
            force_garbage_collection("Final cleanup after _index_chunks")
        
        logger.info("=" * 60)
        
        return {
            'chunks_indexed': indexed_chunks,
            'total_chunks': total_chunks,
            'failed_batches': len(failed_batches),
            'success_rate': indexed_chunks / total_chunks if total_chunks > 0 else 0
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
