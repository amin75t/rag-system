"""
Langfuse Integration Examples for RAG System

This file demonstrates how to integrate Langfuse observability features
into your existing RAG system (chat_manager.py, vector_db.py, document_indexer.py).

Prerequisites:
1. Install langfuse: pip install langfuse
2. Set environment variables:
   - LANGFUSE_PUBLIC_KEY=your_public_key
   - LANGFUSE_SECRET_KEY=your_secret_key
3. Get API keys from https://cloud.langfuse.com
"""

import time
from typing import List, Dict, Any
from langfuse_integration import (
    LangfuseRAGTracker,
    RetrievalStrategy,
    ABTestConfig,
    get_langfuse_tracker
)


# ============================================================================
# EXAMPLE 1: Integration with chat_manager.py
# ============================================================================

class EnterpriseChatSystemWithLangfuse:
    """
    Enhanced EnterpriseChatSystem with Langfuse tracking.
    
    This is how you would modify chat_manager.py to add Langfuse observability.
    """
    
    def __init__(self, *args, **kwargs):
        # Initialize the original chat system
        # from chat_manager import EnterpriseChatSystem
        # self.chat_system = EnterpriseChatSystem(*args, **kwargs)
        
        # Initialize Langfuse tracker
        self.tracker = get_langfuse_tracker()
        
        print("✅ Chat system with Langfuse tracking initialized")
    
    def chat(self, user_query: str, session_id: str = None, user_id: str = None) -> str:
        """
        Chat method with complete Langfuse tracing.
        
        This demonstrates:
        1. Track retrieval quality - which documents were retrieved
        2. Monitor embedding costs and token usage
        3. Debug retrieval failures
        """
        # Use context manager for complete RAG trace
        with self.tracker.create_rag_trace(
            query=user_query,
            session_id=session_id,
            user_id=user_id,
            metadata={"model": "Qwen2.5-7B", "embedding": "baai-bge-m3"}
        ) as trace:
            
            # Step 1: Track Embedding (query embedding)
            start_time = time.time()
            # In real code: query_embedding = self.chat_system.embed_query(user_query)
            embedding_time = (time.time() - start_time) * 1000
            
            # Track embedding usage
            trace.track_embedding(
                texts=[user_query],
                model="baai-bge-m3",
                tokens=len(user_query.split()),  # Approximate token count
                latency_ms=embedding_time,
                metadata={"operation": "query_embedding"}
            )
            
            # Step 2: Track Retrieval (document retrieval)
            start_time = time.time()
            # In real code: retrieved_docs = self.chat_system.retrieve(user_query)
            retrieved_docs = self._mock_retrieve(user_query)
            retrieval_time = (time.time() - start_time) * 1000
            
            # Track retrieval quality
            retrieval_metrics = trace.track_retrieval(
                query=user_query,
                retrieved_docs=retrieved_docs,
                retrieval_time_ms=retrieval_time,
                strategy=RetrievalStrategy.SIMILARITY,
                metadata={"top_k": len(retrieved_docs)}
            )
            
            # Step 3: Debug low relevance
            if retrieval_metrics.avg_similarity_score < 0.5:
                self.tracker.track_low_relevance(
                    query=user_query,
                    retrieved_docs=retrieved_docs,
                    threshold=0.5,
                    session_id=session_id
                )
            
            # Step 4: Track LLM Generation
            start_time = time.time()
            # In real code: response = self.chat_system.generate_response(user_query, retrieved_docs)
            response = self._mock_generate(user_query, retrieved_docs)
            llm_time = (time.time() - start_time) * 1000
            
            # Track LLM usage
            trace.track_llm(
                prompt=user_query,
                response=response,
                model="Qwen2.5-7B",
                input_tokens=len(user_query.split()),
                output_tokens=len(response.split()),
                latency_ms=llm_time,
                metadata={"num_retrieved_docs": len(retrieved_docs)}
            )
            
            return response
    
    def _mock_retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Mock retrieval for demonstration."""
        return [
            {"id": "doc_001", "text": "Sample document content...", "score": 0.85},
            {"id": "doc_002", "text": "Another document...", "score": 0.72},
            {"id": "doc_003", "text": "More content...", "score": 0.65},
        ]
    
    def _mock_generate(self, query: str, docs: List[Dict]) -> str:
        """Mock LLM generation for demonstration."""
        return f"Based on {len(docs)} retrieved documents, here is the answer to: {query}"


# ============================================================================
# EXAMPLE 2: Integration with vector_db.py
# ============================================================================

class VectorDBManagerWithLangfuse:
    """
    Enhanced VectorDBManager with Langfuse tracking.
    
    This demonstrates how to track vector database operations.
    """
    
    def __init__(self, tracker: LangfuseRAGTracker = None):
        # from vector_db import VectorDBManager
        # self.vector_db = VectorDBManager(...)
        
        self.tracker = tracker or get_langfuse_tracker()
        print("✅ Vector DB manager with Langfuse tracking initialized")
    
    def query_with_tracking(
        self,
        query_text: str,
        n_results: int = 5,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Query vector database with Langfuse tracking.
        
        This demonstrates:
        1. Track retrieval quality
        2. Debug retrieval failures
        """
        start_time = time.time()
        
        try:
            # Perform actual query
            # results = self.vector_db.query(query_texts=[query_text], n_results=n_results)
            results = self._mock_vector_query(query_text, n_results)
            
            retrieval_time = (time.time() - start_time) * 1000
            
            # Check if retrieval succeeded
            if not results.get('ids') or len(results['ids'][0]) == 0:
                self.tracker.track_retrieval_failure(
                    query=query_text,
                    failure_reason="no_documents_found",
                    retrieval_strategy=RetrievalStrategy.SIMILARITY,
                    num_docs_attempted=0,
                    session_id=session_id
                )
                return results
            
            # Format retrieved documents for Langfuse
            retrieved_docs = []
            for i, doc_id in enumerate(results['ids'][0]):
                score = results.get('distances', [[0]])[0][i] if results.get('distances') else 0.8
                # Convert distance to similarity (assuming cosine distance)
                similarity = 1 - score if score <= 1 else 1 / (1 + score)
                
                retrieved_docs.append({
                    'id': doc_id,
                    'text': results['documents'][0][i] if results.get('documents') else '',
                    'score': similarity
                })
            
            # Track retrieval quality
            self.tracker.track_retrieval(
                query=query_text,
                retrieved_docs=retrieved_docs,
                retrieval_time_ms=retrieval_time,
                strategy=RetrievalStrategy.SIMILARITY,
                session_id=session_id,
                metadata={"n_results": n_results}
            )
            
            return results
            
        except Exception as e:
            self.tracker.track_retrieval_failure(
                query=query_text,
                failure_reason=f"error: {str(e)}",
                retrieval_strategy=RetrievalStrategy.SIMILARITY,
                num_docs_attempted=0,
                session_id=session_id
            )
            raise
    
    def _mock_vector_query(self, query_text: str, n_results: int) -> Dict[str, Any]:
        """Mock vector query for demonstration."""
        return {
            'ids': [['doc_001', 'doc_002', 'doc_003'][:n_results]],
            'documents': [['Content 1...', 'Content 2...', 'Content 3...'][:n_results]],
            'distances': [[0.15, 0.28, 0.35]][:n_results]
        }


# ============================================================================
# EXAMPLE 3: Integration with document_indexer.py
# ============================================================================

class DocumentIndexerWithLangfuse:
    """
    Enhanced DocumentIndexer with Langfuse tracking.
    
    This demonstrates how to track document indexing operations.
    """
    
    def __init__(self, tracker: LangfuseRAGTracker = None):
        # from document_indexer import DocumentIndexer
        # self.indexer = DocumentIndexer(...)
        
        self.tracker = tracker or get_langfuse_tracker()
        print("✅ Document indexer with Langfuse tracking initialized")
    
    def index_file_with_tracking(
        self,
        file_path: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Index a file with Langfuse tracking.
        
        This demonstrates:
        1. Monitor embedding costs for document chunks
        2. Track processing time and performance
        """
        start_time = time.time()
        
        # Create a trace for indexing operation
        trace = self.tracker._langfuse.trace(
            name="document_indexing",
            input={"file_path": file_path},
            metadata=metadata or {}
        )
        
        try:
            # Step 1: Extract and chunk document
            # chunks = self.indexer.document_processor.process_file(file_path)
            chunks = self._mock_chunks(file_path)
            
            # Step 2: Generate embeddings with tracking
            for i, chunk in enumerate(chunks):
                chunk_start = time.time()
                # embedding = self.indexer.api_client.get_embedding(chunk)
                chunk_time = (time.time() - chunk_start) * 1000
                
                # Track each chunk embedding
                self.tracker.track_embedding_usage(
                    texts=[chunk],
                    model="baai-bge-m3",
                    tokens=len(chunk.split()),
                    latency_ms=chunk_time,
                    metadata={
                        "file_path": file_path,
                        "chunk_index": i,
                        "chunk_length": len(chunk)
                    }
                )
            
            # Step 3: Store in vector database
            # result = self.indexer.vector_db.add_documents(...)
            
            total_time = (time.time() - start_time) * 1000
            
            trace.update(
                output={
                    "num_chunks": len(chunks),
                    "processing_time_ms": total_time,
                    "status": "success"
                }
            )
            
            print(f"✅ Indexed {len(chunks)} chunks in {total_time:.2f}ms")
            return {"num_chunks": len(chunks), "status": "success"}
            
        except Exception as e:
            trace.update(
                output={"status": "error", "error": str(e)},
                level="ERROR"
            )
            raise
    
    def _mock_chunks(self, file_path: str) -> List[str]:
        """Mock chunks for demonstration."""
        return ["Chunk 1 content...", "Chunk 2 content...", "Chunk 3 content..."]


# ============================================================================
# EXAMPLE 4: A/B Testing Different Retrieval Strategies
# ============================================================================

def run_ab_test_example():
    """
    Example of A/B testing different retrieval strategies.
    
    This demonstrates how to compare:
    - Similarity search (strategy A)
    - Hybrid search (strategy B)
    """
    
    tracker = get_langfuse_tracker()
    
    # Configure A/B test
    ab_config = ABTestConfig(
        test_name="similarity_vs_hybrid_retrieval",
        strategy_a=RetrievalStrategy.SIMILARITY,
        strategy_b=RetrievalStrategy.HYBRID,
        traffic_split=0.5,
        metadata={"experiment_date": "2025-01-XX"}
    )
    
    ab_test = tracker.create_ab_test(ab_config)
    
    # Define strategy functions
    def similarity_search(query: str) -> Dict[str, Any]:
        """Strategy A: Pure similarity search."""
        # In real code: return vector_db.query(query_texts=[query], n_results=5)
        time.sleep(0.05)  # Simulate processing
        return {"docs": ["sim_doc_1", "sim_doc_2"], "strategy": "similarity"}
    
    def hybrid_search(query: str) -> Dict[str, Any]:
        """Strategy B: Hybrid search (keyword + semantic)."""
        # In real code: return hybrid_search_engine.search(query)
        time.sleep(0.07)  # Simulate processing
        return {"docs": ["hyb_doc_1", "hyb_doc_2"], "strategy": "hybrid"}
    
    # Define evaluation function
    def evaluate_quality(result: Dict[str, Any]) -> float:
        """Evaluate result quality (0.0 to 1.0)."""
        # In real code: Use human evaluation or automated metrics
        import random
        return random.uniform(0.5, 0.95)
    
    # Run multiple experiments
    queries = [
        "What is the population of Bushehr?",
        "How does the RAG system work?",
        "Explain the document indexing process"
    ]
    
    print("\n🧪 Running A/B Test: similarity_vs_hybrid_retrieval")
    print("=" * 60)
    
    for query in queries:
        result = ab_test.run_experiment(
            query=query,
            strategy_a_fn=similarity_search,
            strategy_b_fn=hybrid_search,
            evaluation_fn=evaluate_quality
        )
        print(f"Query: {query[:40]}... | Strategy: {result['strategy_used']} | Quality: {result['quality_score']:.3f}")
    
    # Get results
    results = ab_test.get_results()
    print("\n" + "=" * 60)
    print("📊 A/B Test Results:")
    print(f"  Strategy A ({results['strategy_a']}): {results['samples_a']} samples, avg_quality={results['avg_quality_a']:.3f}")
    print(f"  Strategy B ({results['strategy_b']}): {results['samples_b']} samples, avg_quality={results['avg_quality_b']:.3f}")
    print(f"  🏆 Winner: {results['winner']}")


# ============================================================================
# EXAMPLE 5: Cost Monitoring Dashboard
# ============================================================================

def demonstrate_cost_monitoring():
    """
    Example of monitoring embedding and LLM costs.
    
    This demonstrates:
    1. Track embedding costs per operation
    2. Track LLM costs per generation
    3. Aggregate total costs
    """
    
    tracker = get_langfuse_tracker()
    
    print("\n💰 Cost Monitoring Example")
    print("=" * 60)
    
    # Simulate multiple RAG operations
    queries = [
        "Query 1: Short question",
        "Query 2: Medium length question with more details",
        "Query 3: Very long and complex question that requires extensive processing and retrieval of multiple documents"
    ]
    
    total_cost = 0
    
    for query in queries:
        print(f"\nProcessing: {query[:50]}...")
        
        # Track embedding
        embedding_metrics = tracker.track_embedding_usage(
            texts=[query],
            model="baai-bge-m3",
            tokens=len(query.split()),
            latency_ms=50,
            metadata={"query_length": len(query)}
        )
        
        # Track LLM
        llm_metrics = tracker.track_llm_usage(
            prompt=query,
            response=f"Response to: {query[:30]}...",
            model="Qwen2.5-7B",
            input_tokens=len(query.split()),
            output_tokens=50,
            latency_ms=200,
            metadata={"response_length": 50}
        )
        
        # Calculate total
        operation_cost = tracker.track_total_cost(embedding_metrics, llm_metrics)
        total_cost += operation_cost.total_cost_usd
    
    print("\n" + "=" * 60)
    print(f"💰 Total cost for {len(queries)} queries: ${total_cost:.6f}")
    print(f"   Average cost per query: ${total_cost/len(queries):.6f}")


# ============================================================================
# EXAMPLE 6: Debugging Retrieval Failures
# ============================================================================

def demonstrate_failure_debugging():
    """
    Example of debugging retrieval failures.
    
    This demonstrates:
    1. Track when no documents are found
    2. Track low relevance scores
    3. Track retrieval errors
    """
    
    tracker = get_langfuse_tracker()
    
    print("\n🐛 Retrieval Failure Debugging Example")
    print("=" * 60)
    
    # Scenario 1: No documents found
    print("\nScenario 1: No documents found")
    tracker.track_retrieval_failure(
        query="Query about a topic not in the database",
        failure_reason="no_documents_found",
        retrieval_strategy=RetrievalStrategy.SIMILARITY,
        num_docs_attempted=0,
        similarity_threshold=0.5,
        metadata={"searched_collection": "documents"}
    )
    
    # Scenario 2: Low relevance scores
    print("Scenario 2: Low relevance scores")
    low_relevance_docs = [
        {"id": "doc_001", "text": "Unrelated content...", "score": 0.3},
        {"id": "doc_002", "text": "Also unrelated...", "score": 0.25},
    ]
    tracker.track_low_relevance(
        query="Specific technical question",
        retrieved_docs=low_relevance_docs,
        threshold=0.5
    )
    
    # Scenario 3: Retrieval error
    print("Scenario 3: Retrieval error")
    tracker.track_retrieval_failure(
        query="Query causing error",
        failure_reason="vector_db_timeout",
        retrieval_strategy=RetrievalStrategy.SIMILARITY,
        num_docs_attempted=5,
        metadata={"error_code": "TIMEOUT", "timeout_ms": 30000}
    )
    
    print("\n✅ All failures tracked. Check Langfuse dashboard for details.")


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Langfuse Integration Examples for RAG System")
    print("=" * 70)
    
    # Check if Langfuse is configured
    tracker = get_langfuse_tracker()
    if not tracker.enabled:
        print("\n⚠️  Langfuse is not configured. Tracking will be disabled.")
        print("   Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.")
        print("   Get keys from: https://cloud.langfuse.com\n")
    
    # Run examples
    demonstrate_cost_monitoring()
    demonstrate_failure_debugging()
    run_ab_test_example()
    
    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("   Check your Langfuse dashboard at https://cloud.langfuse.com")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
