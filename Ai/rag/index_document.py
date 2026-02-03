"""
Script to index a document into the vector database with detailed logging.

This script demonstrates the complete flow:
1. Document processing (extract text, chunking)
2. Embedding generation via API
3. Storage in ChromaDB

Usage:
    cd Ai/rag
    python index_document.py
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from Ai.rag.document_indexer import DocumentIndexer
from Ai.rag.vector_db import get_vector_db_manager, inspect_vector_db_directory


def main():
    """Main function to index a document."""
    
    print("=" * 70)
    print("DOCUMENT INDEXING WITH DETAILED LOGGING")
    print("=" * 70)
    
    # Step 1: Check vector database before indexing
    print("\n" + "=" * 70)
    print("STEP 1: CHECKING VECTOR DATABASE BEFORE INDEXING")
    print("=" * 70)
    
    vector_db_path = "/mnt/d/projact/rag-new/rag-system/Ai/db/vector_db"
    inspection = inspect_vector_db_directory(vector_db_path)
    
    print(f"Vector DB path: {inspection['path']}")
    print(f"Path exists: {inspection['exists']}")
    print(f"Is directory: {inspection['is_directory']}")
    print(f"Contents: {len(inspection['contents'])} items")
    
    for item in inspection['contents']:
        print(f"  - {item['name']} (dir={item['is_dir']}, size={item['size']})")
    
    if inspection['chroma_collections']:
        print(f"\nChromaDB collections found: {len(inspection['chroma_collections'])}")
        for coll in inspection['chroma_collections']:
            print(f"  - UUID: {coll['uuid']}")
            print(f"    Files: {coll['files']}")
    
    # Check current document count
    vector_db = get_vector_db_manager(
        collection_name="documents",
        persist_directory=vector_db_path
    )
    
    doc_count_before = vector_db.count()
    print(f"\nCurrent document count in 'documents' collection: {doc_count_before}")
    
    # List all collections
    all_collections = vector_db.client.list_collections()
    print(f"All collections in database: {[c.name for c in all_collections]}")
    
    # Step 2: Initialize document indexer
    print("\n" + "=" * 70)
    print("STEP 2: INITIALIZING DOCUMENT INDEXER")
    print("=" * 70)
    
    indexer = DocumentIndexer(
        vector_db=vector_db,
        chunk_size=1000,
        chunk_overlap=200,
        batch_size=10,
        processing_batch_size=100
    )
    
    # Step 3: Index document
    print("\n" + "=" * 70)
    print("STEP 3: INDEXING DOCUMENT")
    print("=" * 70)
    
    # Use the Persian document in the rag directory
    doc_path = "report.docx"
    
    if not Path(doc_path).exists():
        print(f"ERROR: Document not found at: {doc_path}")
        print("Please ensure the document exists.")
        return
    
    print(f"Document path: {doc_path}")
    print(f"Document exists: {Path(doc_path).exists()}")
    print(f"Document size: {Path(doc_path).stat().st_size / 1024:.2f} KB")
    
    # Index the document
    result = indexer.index_file(
        file_path=doc_path,
        metadata={
            "source": "سند راهنمای رصدپذیری v1.1.docx",
            "indexed_at": "2025-01-XX",
            "language": "persian"
        }
    )
    
    # Step 4: Check vector database after indexing
    print("\n" + "=" * 70)
    print("STEP 4: CHECKING VECTOR DATABASE AFTER INDEXING")
    print("=" * 70)
    
    doc_count_after = vector_db.count()
    print(f"Document count in 'documents' collection: {doc_count_after}")
    print(f"Documents added: {doc_count_after - doc_count_before}")
    
    # Get sample documents from the database
    if doc_count_after > 0:
        print(f"\nGetting sample documents from database...")
        sample_results = vector_db.get(limit=3)
        
        if sample_results.get('documents'):
            print(f"Sample documents retrieved: {len(sample_results['documents'])}")
            for i, doc in enumerate(sample_results['documents']):
                print(f"\n  Document {i+1}:")
                print(f"    ID: {sample_results['ids'][i]}")
                print(f"    Content preview: {doc[:100]}...")
                if sample_results.get('metadatas'):
                    print(f"    Metadata: {sample_results['metadatas'][i]}")
    
    # Step 5: Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Document indexed: {doc_path}")
    print(f"Chunks indexed: {result.get('chunks_indexed', 0)}")
    print(f"Documents before: {doc_count_before}")
    print(f"Documents after: {doc_count_after}")
    print(f"Documents added: {doc_count_after - doc_count_before}")
    print(f"Status: {'SUCCESS' if doc_count_after > doc_count_before else 'FAILED'}")
    print("=" * 70)
    
    # Step 6: Test retrieval
    if doc_count_after > 0:
        print("\n" + "=" * 70)
        print("STEP 6: TESTING RETRIEVAL")
        print("=" * 70)
        
        test_query = "رصدپذیری چیست؟"  # What is observability?
        print(f"Test query: {test_query}")
        
        # Get embedding for test query
        from Ai.rag.document_indexer import get_alpha_api_client
        api_client = get_alpha_api_client()
        
        print("Getting embedding for test query...")
        embedding_response = api_client.embeddings(test_query)
        embedding_vector = api_client.extract_embeddings(embedding_response)[0]
        print(f"Embedding dimension: {len(embedding_vector)}")
        
        # Query the database
        print("Querying vector database...")
        search_results = vector_db.query(
            query_embeddings=[embedding_vector],
            n_results=3
        )
        
        print(f"Results found: {len(search_results.get('ids', [[]])[0])}")
        
        if search_results.get('documents') and search_results['documents'][0]:
            for i, doc in enumerate(search_results['documents'][0]):
                distance = search_results['distances'][0][i]
                similarity = 1 - distance  # Convert to similarity
                print(f"\n  Result {i+1}:")
                print(f"    Distance: {distance:.4f}")
                print(f"    Similarity: {similarity:.4f}")
                print(f"    Content: {doc[:150]}...")
        else:
            print("No results found!")
    
    print("\n" + "=" * 70)
    print("INDEXING COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
