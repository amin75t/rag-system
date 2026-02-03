# Langfuse Integration for RAG System

This directory contains a comprehensive Langfuse integration for your RAG system that provides observability, analytics, and debugging capabilities.

## 📋 Table of Contents

1. [What is Langfuse?](#what-is-langfuse)
2. [Features](#features)
3. [Installation](#installation)
4. [Setup](#setup)
5. [Quick Start](#quick-start)
6. [Usage Examples](#usage-examples)
7. [Integration Guide](#integration-guide)
8. [Dashboard Features](#dashboard-features)

---

## What is Langfuse?

**Langfuse** is an open-source LLM engineering platform that provides:
- **Observability** - Track every LLM call, prompt, and response
- **Analytics** - Monitor costs, latency, token usage, and performance
- **Debugging** - Inspect traces to understand model behavior
- **Evaluation** - Run automated tests on LLM outputs
- **Datasets** - Manage test datasets for consistent evaluation

---

## Features

### 1. Track Retrieval Quality
See which documents were retrieved and their impact on responses:
- Track number of documents retrieved
- Monitor similarity scores (avg, min, max)
- Record retrieval time
- Log document IDs and scores

### 2. Monitor Embedding Costs & Token Usage
Track costs for your RAG operations:
- Embedding token counts and costs
- LLM input/output tokens and costs
- Total cost per query
- Cost aggregation over time

### 3. Debug Retrieval Failures
Identify and fix retrieval issues:
- Track when no documents are found
- Monitor low relevance scores
- Log retrieval errors
- Set similarity thresholds

### 4. A/B Testing
Compare different strategies:
- Test different retrieval strategies
- Compare prompt templates
- Measure quality scores
- Determine winning strategies

---

## Installation

```bash
pip install langfuse
```

---

## Setup

### 1. Get Langfuse API Keys

1. Go to [https://cloud.langfuse.com](https://cloud.langfuse.com)
2. Sign up for a free account
3. Create a new project
4. Copy your **Public Key** and **Secret Key**

### 2. Set Environment Variables

Add these to your `.env` file or system environment:

```bash
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud
```

### 3. Verify Installation

```python
from langfuse_integration import get_langfuse_tracker

tracker = get_langfuse_tracker()
print(f"Langfuse enabled: {tracker.enabled}")
```

---

## Quick Start

### Basic Usage

```python
from langfuse_integration import get_langfuse_tracker, RetrievalStrategy

# Get tracker instance
tracker = get_langfuse_tracker()

# Track retrieval
tracker.track_retrieval(
    query="What is the population of Bushehr?",
    retrieved_docs=[
        {"id": "doc_001", "text": "Population data...", "score": 0.85},
        {"id": "doc_002", "text": "More data...", "score": 0.72}
    ],
    retrieval_time_ms=150.5,
    strategy=RetrievalStrategy.SIMILARITY
)
```

### Complete RAG Trace

```python
from langfuse_integration import get_langfuse_tracker

tracker = get_langfuse_tracker()

with tracker.create_rag_trace(query="Your question here") as trace:
    # Track embedding
    trace.track_embedding(
        texts=["Your question"],
        model="baai-bge-m3",
        tokens=10,
        latency_ms=50
    )
    
    # Track retrieval
    trace.track_retrieval(
        query="Your question",
        retrieved_docs=retrieved_docs,
        retrieval_time_ms=100,
        strategy=RetrievalStrategy.SIMILARITY
    )
    
    # Track LLM
    trace.track_llm(
        prompt="Your question",
        response="AI response",
        model="Qwen2.5-7B",
        input_tokens=10,
        output_tokens=100,
        latency_ms=200
    )
```

---

## Usage Examples

Run the example file to see all features in action:

```bash
cd Ai/rag
python langfuse_example.py
```

This will demonstrate:
1. Integration with [`chat_manager.py`](chat_manager.py)
2. Integration with [`vector_db.py`](vector_db.py)
3. Integration with [`document_indexer.py`](document_indexer.py)
4. A/B testing different strategies
5. Cost monitoring
6. Failure debugging

---

## Integration Guide

### Integrating with `chat_manager.py`

Modify your [`EnterpriseChatSystem`](chat_manager.py:216) class:

```python
from langfuse_integration import get_langfuse_tracker, RetrievalStrategy

class EnterpriseChatSystem:
    def __init__(self, *args, **kwargs):
        # Original initialization
        # ...
        
        # Add Langfuse tracker
        self.tracker = get_langfuse_tracker()
    
    def chat(self, user_query: str, session_id: str = None) -> str:
        """Enhanced chat method with Langfuse tracking."""
        with self.tracker.create_rag_trace(
            query=user_query,
            session_id=session_id,
            metadata={"model": "Qwen2.5-7B"}
        ) as trace:
            
            # Track embedding
            query_embedding = self._embed_query(user_query)
            trace.track_embedding(
                texts=[user_query],
                model=self.embedding_model,
                tokens=len(user_query.split()),
                latency_ms=embedding_time
            )
            
            # Track retrieval
            retrieved_docs = self._retrieve_documents(query_embedding)
            trace.track_retrieval(
                query=user_query,
                retrieved_docs=self._format_retrieved_docs(retrieved_docs),
                retrieval_time_ms=retrieval_time,
                strategy=RetrievalStrategy.SIMILARITY
            )
            
            # Track LLM
            response = self.chat_engine.chat(user_query)
            trace.track_llm(
                prompt=user_query,
                response=str(response),
                model=self.llm_model_path,
                input_tokens=self._count_tokens(user_query),
                output_tokens=self._count_tokens(str(response)),
                latency_ms=llm_time
            )
            
            return str(response)
```

### Integrating with `vector_db.py`

Modify your [`VectorDBManager`](vector_db.py:22) class:

```python
from langfuse_integration import get_langfuse_tracker, RetrievalStrategy

class VectorDBManager:
    def __init__(self, *args, **kwargs):
        # Original initialization
        # ...
        
        # Add Langfuse tracker
        self.tracker = get_langfuse_tracker()
    
    def query_with_tracking(
        self,
        query_text: str,
        n_results: int = 5,
        session_id: str = None
    ) -> Dict[str, Any]:
        """Query with Langfuse tracking."""
        start_time = time.time()
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            retrieval_time = (time.time() - start_time) * 1000
            
            # Format for Langfuse
            retrieved_docs = []
            for i, doc_id in enumerate(results['ids'][0]):
                score = 1 - results['distances'][0][i]  # Convert to similarity
                retrieved_docs.append({
                    'id': doc_id,
                    'text': results['documents'][0][i],
                    'score': score
                })
            
            # Track retrieval
            self.tracker.track_retrieval(
                query=query_text,
                retrieved_docs=retrieved_docs,
                retrieval_time_ms=retrieval_time,
                strategy=RetrievalStrategy.SIMILARITY,
                session_id=session_id
            )
            
            return results
            
        except Exception as e:
            # Track failure
            self.tracker.track_retrieval_failure(
                query=query_text,
                failure_reason=str(e),
                retrieval_strategy=RetrievalStrategy.SIMILARITY,
                session_id=session_id
            )
            raise
```

### Integrating with `document_indexer.py`

Modify your [`DocumentIndexer`](document_indexer.py:96) class:

```python
from langfuse_integration import get_langfuse_tracker

class DocumentIndexer:
    def __init__(self, *args, **kwargs):
        # Original initialization
        # ...
        
        # Add Langfuse tracker
        self.tracker = get_langfuse_tracker()
    
    def index_file_with_tracking(
        self,
        file_path: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Index file with Langfuse tracking."""
        trace = self.tracker._langfuse.trace(
            name="document_indexing",
            input={"file_path": file_path},
            metadata=metadata or {}
        )
        
        try:
            # Process file into chunks
            chunks = self.document_processor.process_file(file_path)
            
            # Track each chunk embedding
            for i, chunk in enumerate(chunks):
                embedding = self.api_client.get_embedding(chunk)
                
                self.tracker.track_embedding_usage(
                    texts=[chunk],
                    model=self.embedding_model,
                    tokens=len(chunk.split()),
                    latency_ms=chunk_time,
                    metadata={
                        "file_path": file_path,
                        "chunk_index": i,
                        "chunk_length": len(chunk)
                    }
                )
            
            # Store in vector DB
            self.vector_db.add_documents(chunks)
            
            trace.update(output={"num_chunks": len(chunks), "status": "success"})
            return {"num_chunks": len(chunks)}
            
        except Exception as e:
            trace.update(output={"status": "error", "error": str(e)}, level="ERROR")
            raise
```

---

## Dashboard Features

After integrating Langfuse, visit [https://cloud.langfuse.com](https://cloud.langfuse.com) to see:

### Traces View
- Complete timeline of each RAG operation
- Embedding, retrieval, and LLM steps
- Timing breakdown for each step

### Sessions View
- Group traces by user sessions
- Track conversation history
- Analyze user behavior patterns

### Observability
- Real-time metrics dashboard
- Cost tracking over time
- Token usage statistics
- Latency monitoring

### Evaluation
- Create datasets for testing
- Run automated evaluations
- Compare model versions
- Track quality metrics

### Debugging
- Filter by error status
- View failure reasons
- Inspect low-relevance retrievals
- Analyze retrieval patterns

---

## API Reference

### LangfuseRAGTracker

Main class for tracking RAG operations.

#### Methods

| Method | Description |
|--------|-------------|
| `track_retrieval()` | Track document retrieval quality |
| `track_embedding_usage()` | Track embedding costs and tokens |
| `track_llm_usage()` | Track LLM generation costs and tokens |
| `track_retrieval_failure()` | Track retrieval failures |
| `track_low_relevance()` | Track low relevance scores |
| `create_ab_test()` | Create an A/B test runner |
| `create_rag_trace()` | Create complete RAG trace context |

### RetrievalStrategy

Enum for retrieval strategies:
- `SIMILARITY` - Pure similarity search
- `HYBRID` - Hybrid (keyword + semantic)
- `RERANK` - Retrieval with reranking
- `PARENT_CHILD` - Parent-child retrieval

### CostMetrics

Dataclass for cost tracking:
- `embedding_tokens` - Number of embedding tokens
- `embedding_cost_usd` - Embedding cost in USD
- `llm_input_tokens` - LLM input tokens
- `llm_output_tokens` - LLM output tokens
- `llm_cost_usd` - LLM cost in USD
- `total_cost_usd` - Total cost

---

## Tips & Best Practices

1. **Always use context managers** for complete RAG traces to ensure proper cleanup
2. **Set appropriate similarity thresholds** for your use case (e.g., 0.5-0.7)
3. **Track user sessions** to analyze conversation patterns
4. **Use metadata** to add context (e.g., document type, user segment)
5. **Run A/B tests** before deploying new retrieval strategies
6. **Monitor costs** regularly to optimize performance
7. **Set up alerts** for high failure rates or costs

---

## Troubleshooting

### Langfuse not tracking

```python
# Check if enabled
tracker = get_langfuse_tracker()
print(f"Enabled: {tracker.enabled}")

# Check environment variables
import os
print(f"Public Key: {os.getenv('LANGFUSE_PUBLIC_KEY')}")
print(f"Secret Key: {os.getenv('LANGFUSE_SECRET_KEY')}")
```

### High costs

- Reduce `similarity_top_k` parameter
- Use smaller embedding models
- Cache frequently used embeddings
- Implement query deduplication

### Low retrieval quality

- Adjust similarity threshold
- Try different retrieval strategies
- Improve document chunking
- Add more relevant documents

---

## Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse Python SDK](https://github.com/langfuse/langfuse-python)
- [RAG Best Practices](https://www.llamaindex.ai/blog/)

---

## License

This integration is part of your RAG system project.
