"""
Document Embedding Script for RAG system.

This script provides a command-line interface for embedding documents
using the Alpha API from back-end and storing them in the vector database.

Usage:
    python embed_documents.py --file path/to/document.pdf
    python embed_documents.py --directory path/to/docs/
    python embed_documents.py --text "Your text here" --doc_id my_doc
"""
import argparse
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add back-end to path for API imports
BACKEND_PATH = Path(__file__).parent.parent / "back-end"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from .document_indexer import get_document_indexer
from .vector_db import get_vector_db_manager


def embed_file(file_path: str, metadata: dict = None) -> dict:
    """
    Embed a single document file.
    
    Args:
        file_path: Path to the document file
        metadata: Optional metadata dictionary
        
    Returns:
        Indexing result
    """
    logger.info(f"Embedding file: {file_path}")
    
    indexer = get_document_indexer()
    result = indexer.index_file(file_path, metadata=metadata)
    
    logger.info(f"Successfully embedded {result['chunks_indexed']} chunks")
    return result


def embed_directory(
    directory_path: str,
    file_patterns: list = None,
    recursive: bool = True
) -> dict:
    """
    Embed all documents in a directory.
    
    Args:
        directory_path: Path to the directory
        file_patterns: List of file patterns (e.g., ['*.pdf', '*.txt'])
        recursive: Whether to search subdirectories
        
    Returns:
        Indexing result
    """
    logger.info(f"Embedding directory: {directory_path}")
    
    indexer = get_document_indexer()
    result = indexer.index_directory(
        directory_path,
        file_patterns=file_patterns,
        recursive=recursive
    )
    
    logger.info(f"Successfully embedded {result['total_chunks_indexed']} chunks "
                f"from {result['successful_files']} files")
    
    if result['failed_files'] > 0:
        logger.warning(f"Failed to embed {result['failed_files']} files:")
        for failed in result['failed_file_details']:
            logger.warning(f"  - {failed['file']}: {failed['error']}")
    
    return result


def embed_text(text: str, doc_id: str = "manual", metadata: dict = None) -> dict:
    """
    Embed a text string directly.
    
    Args:
        text: Text content to embed
        doc_id: Document ID
        metadata: Optional metadata dictionary
        
    Returns:
        Indexing result
    """
    logger.info(f"Embedding text with ID: {doc_id}")
    
    indexer = get_document_indexer()
    result = indexer.index_text(text, metadata=metadata, doc_id=doc_id)
    
    logger.info(f"Successfully embedded {result['chunks_indexed']} chunks")
    return result


def show_stats():
    """Show vector database statistics."""
    logger.info("Vector Database Statistics:")
    
    vector_db = get_vector_db_manager()
    count = vector_db.count()
    
    logger.info(f"  Total documents: {count}")
    logger.info(f"  Collection: {vector_db.collection_name}")
    logger.info(f"  Persist directory: {vector_db.persist_directory}")


def clear_database():
    """Clear all documents from the vector database."""
    logger.warning("This will clear all documents from the vector database!")
    confirm = input("Are you sure? (yes/no): ")
    
    if confirm.lower() == 'yes':
        indexer = get_document_indexer()
        indexer.clear_index()
        logger.info("Vector database cleared")
    else:
        logger.info("Operation cancelled")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Embed documents for RAG system using Alpha API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Embed a single PDF file
  python embed_documents.py --file document.pdf
  
  # Embed all PDFs in a directory
  python embed_documents.py --directory ./docs --patterns "*.pdf"
  
  # Embed text directly
  python embed_documents.py --text "Your text here" --doc_id my_text
  
  # Show database statistics
  python embed_documents.py --stats
  
  # Clear the database
  python embed_documents.py --clear
        """
    )
    
    # Action arguments (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--file', '-f',
        help='Path to a single document file to embed'
    )
    action_group.add_argument(
        '--directory', '-d',
        help='Path to a directory containing documents to embed'
    )
    action_group.add_argument(
        '--text', '-t',
        help='Text string to embed directly'
    )
    action_group.add_argument(
        '--stats',
        action='store_true',
        help='Show vector database statistics'
    )
    action_group.add_argument(
        '--clear',
        action='store_true',
        help='Clear all documents from vector database'
    )
    
    # Optional arguments
    parser.add_argument(
        '--patterns', '-p',
        nargs='+',
        help='File patterns to include (e.g., "*.pdf *.txt")'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        default=True,
        help='Search directories recursively (default: True)'
    )
    parser.add_argument(
        '--doc-id',
        help='Document ID for text embedding'
    )
    parser.add_argument(
        '--metadata',
        help='JSON string with metadata'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Maximum chunk size in characters (default: 1000)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Chunk overlap in characters (default: 200)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for embedding API calls (default: 10)'
    )
    parser.add_argument(
        '--collection',
        default='documents',
        help='ChromaDB collection name (default: documents)'
    )
    parser.add_argument(
        '--persist-dir',
        default='./vector_db',
        help='Vector database persist directory (default: ./vector_db)'
    )
    
    args = parser.parse_args()
    
    # Parse metadata if provided
    metadata = None
    if args.metadata:
        try:
            import json
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in metadata: {args.metadata}")
            return 1
    
    # Execute action
    try:
        if args.stats:
            show_stats()
        elif args.clear:
            clear_database()
        elif args.file:
            embed_file(args.file, metadata)
        elif args.directory:
            patterns = args.patterns if args.patterns else None
            embed_directory(args.directory, patterns, args.recursive)
        elif args.text:
            doc_id = args.doc_id if args.doc_id else "manual"
            embed_text(args.text, doc_id, metadata)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
