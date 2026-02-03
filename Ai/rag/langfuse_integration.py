"""
Langfuse Integration for RAG System

This module provides comprehensive Langfuse observability features for the RAG system:

1. Track retrieval quality - see which documents were retrieved and their impact
2. Monitor embedding costs and token usage
3. Debug retrieval failures when relevant documents aren't found
4. A/B test different retrieval strategies or prompt templates

Installation:
    pip install langfuse

Setup:
    1. Get API keys from https://cloud.langfuse.com
    2. Set environment variables:
       - LANGFUSE_PUBLIC_KEY
       - LANGFUSE_SECRET_KEY
       - LANGFUSE_HOST (optional, defaults to https://cloud.langfuse.com)
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RetrievalStrategy(Enum):
    """Enumeration of different retrieval strategies for A/B testing."""
    SIMILARITY = "similarity"
    HYBRID = "hybrid"
    RERANK = "rerank"
    PARENT_CHILD = "parent_child"


@dataclass
class RetrievalMetrics:
    """Metrics for tracking retrieval quality."""
    num_documents_retrieved: int
    retrieval_time_ms: float
    avg_similarity_score: float
    min_similarity_score: float
    max_similarity_score: float
    document_ids: List[str] = field(default_factory=list)
    document_scores: List[float] = field(default_factory=list)


@dataclass
class CostMetrics:
    """Metrics for tracking embedding and LLM costs."""
    embedding_tokens: int = 0
    embedding_cost_usd: float = 0.0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    llm_cost_usd: float = 0.0
    total_cost_usd: float = 0.0

    # Cost per token (adjust based on your model pricing)
    EMBEDDING_COST_PER_1K_TOKENS = 0.0001  # Example: BGE-M3
    LLM_INPUT_COST_PER_1K_TOKENS = 0.0001  # Example: Local model
    LLM_OUTPUT_COST_PER_1K_TOKENS = 0.0002  # Example: Local model


@dataclass
class ABTestConfig:
    """Configuration for A/B testing."""
    test_name: str
    strategy_a: RetrievalStrategy
    strategy_b: RetrievalStrategy
    traffic_split: float = 0.5  # 50/50 split by default
    metadata: Dict[str, Any] = field(default_factory=dict)


class LangfuseRAGTracker:
    """
    Main class for tracking RAG operations with Langfuse.
    
    This class provides:
    1. Retrieval quality tracking
    2. Cost and token monitoring
    3. Retrieval failure debugging
    4. A/B testing capabilities
    """
    
    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: str = "https://cloud.langfuse.com",
        enabled: bool = True
    ):
        """
        Initialize the Langfuse RAG Tracker.
        
        Args:
            public_key: Langfuse public key (or from LANGFUSE_PUBLIC_KEY env var)
            secret_key: Langfuse secret key (or from LANGFUSE_SECRET_KEY env var)
            host: Langfuse host URL
            enabled: Whether tracking is enabled
        """
        self.enabled = enabled
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = host
        
        # Lazy import of langfuse (only if enabled)
        self._langfuse = None
        self._initialized = False
        
        if self.enabled:
            self._initialize_langfuse()
    
    def _initialize_langfuse(self):
        """Initialize Langfuse client."""
        try:
            from langfuse import Langfuse
            
            if not self.public_key or not self.secret_key:
                logger.warning(
                    "Langfuse keys not found. Tracking will be disabled. "
                    "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
                )
                self.enabled = False
                return
            
            self._langfuse = Langfuse(
                public_key=self.public_key,
                secret_key=self.secret_key,
                host=self.host
            )
            self._initialized = True
            logger.info("✅ Langfuse initialized successfully")
            
        except ImportError:
            logger.warning(
                "langfuse package not installed. Install with: pip install langfuse. "
                "Tracking will be disabled."
            )
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Langfuse: {e}")
            self.enabled = False
    
    # ==================== FEATURE 1: Track Retrieval Quality ====================
    
    def track_retrieval(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        retrieval_time_ms: float,
        strategy: RetrievalStrategy = RetrievalStrategy.SIMILARITY,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RetrievalMetrics:
        """
        Track retrieval quality - see which documents were retrieved and their impact.
        
        Args:
            query: The user query
            retrieved_docs: List of retrieved documents with 'id', 'text', 'score' keys
            retrieval_time_ms: Time taken for retrieval in milliseconds
            strategy: Retrieval strategy used
            session_id: Optional session ID for grouping traces
            user_id: Optional user ID
            metadata: Additional metadata to attach
            
        Returns:
            RetrievalMetrics object with calculated metrics
        """
        if not self.enabled or not self._initialized:
            logger.debug("Langfuse tracking disabled, skipping retrieval tracking")
            return self._calculate_retrieval_metrics(retrieved_docs, retrieval_time_ms)
        
        start_time = time.time()
        
        # Calculate metrics
        metrics = self._calculate_retrieval_metrics(retrieved_docs, retrieval_time_ms)
        
        # Create Langfuse span for retrieval
        span = self._langfuse.span(
            name="rag_retrieval",
            input={"query": query, "strategy": strategy.value},
            output={
                "num_documents": metrics.num_documents_retrieved,
                "document_ids": metrics.document_ids,
                "document_scores": metrics.document_scores
            },
            metadata=metadata or {},
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        # Set metrics on the span
        span.update(
            usage={
                "retrieval_time_ms": retrieval_time_ms,
                "avg_similarity_score": metrics.avg_similarity_score,
                "min_similarity_score": metrics.min_similarity_score,
                "max_similarity_score": metrics.max_similarity_score
            }
        )
        
        # Add document-level observations
        for i, doc in enumerate(retrieved_docs):
            self._langfuse.score(
                name=f"retrieved_doc_{i}_relevance",
                value=doc.get('score', 0.0),
                comment=f"Document ID: {doc.get('id', 'unknown')}",
                observation_id=span.id
            )
        
        logger.info(
            f"📊 Tracked retrieval: {metrics.num_documents_retrieved} docs, "
            f"avg_score={metrics.avg_similarity_score:.3f}, "
            f"time={retrieval_time_ms:.2f}ms"
        )
        
        return metrics
    
    def _calculate_retrieval_metrics(
        self,
        retrieved_docs: List[Dict[str, Any]],
        retrieval_time_ms: float
    ) -> RetrievalMetrics:
        """Calculate retrieval metrics from retrieved documents."""
        scores = [doc.get('score', 0.0) for doc in retrieved_docs]
        doc_ids = [doc.get('id', f"doc_{i}") for i, doc in enumerate(retrieved_docs)]
        
        return RetrievalMetrics(
            num_documents_retrieved=len(retrieved_docs),
            retrieval_time_ms=retrieval_time_ms,
            avg_similarity_score=sum(scores) / len(scores) if scores else 0.0,
            min_similarity_score=min(scores) if scores else 0.0,
            max_similarity_score=max(scores) if scores else 0.0,
            document_ids=doc_ids,
            document_scores=scores
        )
    
    # ==================== FEATURE 2: Monitor Embedding Costs ====================
    
    def track_embedding_usage(
        self,
        texts: List[str],
        model: str,
        tokens: int,
        latency_ms: float,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CostMetrics:
        """
        Track embedding usage and costs.
        
        Args:
            texts: List of texts that were embedded
            model: Model name used for embeddings
            tokens: Number of tokens processed
            latency_ms: Latency in milliseconds
            session_id: Optional session ID
            metadata: Additional metadata
            
        Returns:
            CostMetrics with calculated costs
        """
        if not self.enabled or not self._initialized:
            return CostMetrics(embedding_tokens=tokens)
        
        cost_usd = (tokens / 1000) * CostMetrics.EMBEDDING_COST_PER_1K_TOKENS
        
        span = self._langfuse.span(
            name="rag_embedding",
            input={
                "num_texts": len(texts),
                "model": model,
                "total_chars": sum(len(text) for text in texts)
            },
            metadata=metadata or {},
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        span.update(
            usage={
                "tokens": tokens,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd
            }
        )
        
        logger.info(
            f"💰 Tracked embedding: {tokens} tokens, "
            f"cost=${cost_usd:.6f}, "
            f"latency={latency_ms:.2f}ms"
        )
        
        return CostMetrics(embedding_tokens=tokens, embedding_cost_usd=cost_usd)
    
    def track_llm_usage(
        self,
        prompt: str,
        response: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CostMetrics:
        """
        Track LLM usage and costs.
        
        Args:
            prompt: The prompt sent to LLM
            response: The response from LLM
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: Latency in milliseconds
            session_id: Optional session ID
            metadata: Additional metadata
            
        Returns:
            CostMetrics with calculated costs
        """
        if not self.enabled or not self._initialized:
            return CostMetrics(
                llm_input_tokens=input_tokens,
                llm_output_tokens=output_tokens
            )
        
        input_cost = (input_tokens / 1000) * CostMetrics.LLM_INPUT_COST_PER_1K_TOKENS
        output_cost = (output_tokens / 1000) * CostMetrics.LLM_OUTPUT_COST_PER_1K_TOKENS
        total_cost = input_cost + output_cost
        
        generation = self._langfuse.generation(
            name="rag_llm_generation",
            input=prompt,
            output=response,
            model=model,
            metadata=metadata or {},
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        generation.update(
            usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost_usd": input_cost,
                "output_cost_usd": output_cost,
                "total_cost_usd": total_cost,
                "latency_ms": latency_ms
            }
        )
        
        logger.info(
            f"💰 Tracked LLM: {input_tokens} in, {output_tokens} out, "
            f"cost=${total_cost:.6f}, "
            f"latency={latency_ms:.2f}ms"
        )
        
        return CostMetrics(
            llm_input_tokens=input_tokens,
            llm_output_tokens=output_tokens,
            llm_cost_usd=total_cost
        )
    
    def track_total_cost(self, embedding_metrics: CostMetrics, llm_metrics: CostMetrics) -> CostMetrics:
        """Calculate and track total cost for a RAG operation."""
        total = CostMetrics(
            embedding_tokens=embedding_metrics.embedding_tokens,
            embedding_cost_usd=embedding_metrics.embedding_cost_usd,
            llm_input_tokens=llm_metrics.llm_input_tokens,
            llm_output_tokens=llm_metrics.llm_output_tokens,
            llm_cost_usd=llm_metrics.llm_cost_usd,
            total_cost_usd=embedding_metrics.embedding_cost_usd + llm_metrics.llm_cost_usd
        )
        
        logger.info(
            f"💰 Total cost: ${total.total_cost_usd:.6f} "
            f"(embeddings: ${total.embedding_cost_usd:.6f}, "
            f"LLM: ${total.llm_cost_usd:.6f})"
        )
        
        return total
    
    # ==================== FEATURE 3: Debug Retrieval Failures ====================
    
    def track_retrieval_failure(
        self,
        query: str,
        failure_reason: str,
        retrieval_strategy: RetrievalStrategy,
        num_docs_attempted: int = 0,
        similarity_threshold: Optional[float] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track retrieval failures for debugging.
        
        Args:
            query: The query that failed
            failure_reason: Reason for failure (e.g., "no_docs_above_threshold")
            retrieval_strategy: Strategy used
            num_docs_attempted: Number of documents attempted
            similarity_threshold: Threshold used for filtering
            session_id: Optional session ID
            metadata: Additional metadata
        """
        if not self.enabled or not self._initialized:
            logger.warning(f"❌ Retrieval failure: {failure_reason}")
            return
        
        span = self._langfuse.span(
            name="rag_retrieval_failure",
            input={"query": query},
            output={
                "failure_reason": failure_reason,
                "strategy": retrieval_strategy.value,
                "num_docs_attempted": num_docs_attempted,
                "similarity_threshold": similarity_threshold
            },
            metadata=metadata or {},
            level="ERROR",
            status_message=failure_reason
        )
        
        logger.error(
            f"❌ Tracked retrieval failure: {failure_reason} "
            f"(query: '{query[:50]}...', strategy: {retrieval_strategy.value})"
        )
    
    def track_low_relevance(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        threshold: float,
        session_id: Optional[str] = None
    ):
        """
        Track when retrieved documents have low relevance scores.
        
        This helps identify queries that need better retrieval strategies.
        """
        low_relevance_docs = [
            doc for doc in retrieved_docs 
            if doc.get('score', 0.0) < threshold
        ]
        
        if low_relevance_docs:
            self.track_retrieval_failure(
                query=query,
                failure_reason="low_relevance_scores",
                retrieval_strategy=RetrievalStrategy.SIMILARITY,
                num_docs_attempted=len(retrieved_docs),
                similarity_threshold=threshold,
                session_id=session_id,
                metadata={
                    "num_low_relevance": len(low_relevance_docs),
                    "low_scores": [d.get('score') for d in low_relevance_docs]
                }
            )
    
    # ==================== FEATURE 4: A/B Testing ====================
    
    class ABTestRunner:
        """Runner for A/B testing different retrieval strategies."""
        
        def __init__(self, tracker: 'LangfuseRAGTracker', config: ABTestConfig):
            self.tracker = tracker
            self.config = config
            self._results_a = []
            self._results_b = []
        
        def run_experiment(
            self,
            query: str,
            strategy_a_fn: callable,
            strategy_b_fn: callable,
            evaluation_fn: callable
        ) -> Dict[str, Any]:
            """
            Run an A/B test experiment.
            
            Args:
                query: The query to test
                strategy_a_fn: Function that implements strategy A
                strategy_b_fn: Function that implements strategy B
                evaluation_fn: Function that evaluates the result quality
                
            Returns:
                Dictionary with experiment results
            """
            import random
            
            # Randomly assign strategy based on traffic split
            use_strategy_a = random.random() < self.config.traffic_split
            
            if use_strategy_a:
                strategy = self.config.strategy_a
                result = strategy_a_fn(query)
                self._results_a.append(result)
            else:
                strategy = self.config.strategy_b
                result = strategy_b_fn(query)
                self._results_b.append(result)
            
            # Evaluate result quality
            quality_score = evaluation_fn(result)
            
            # Track the experiment
            if self.tracker.enabled and self.tracker._initialized:
                self.tracker._langfuse.event(
                    name="ab_test_assignment",
                    input={"query": query},
                    output={
                        "test_name": self.config.test_name,
                        "strategy_used": strategy.value,
                        "quality_score": quality_score
                    },
                    metadata={
                        "strategy_a": self.config.strategy_a.value,
                        "strategy_b": self.config.strategy_b.value,
                        "traffic_split": self.config.traffic_split
                    }
                )
            
            logger.info(
                f"🧪 A/B Test: {self.config.test_name} - "
                f"Used {strategy.value}, Quality: {quality_score:.3f}"
            )
            
            return {
                "strategy_used": strategy.value,
                "result": result,
                "quality_score": quality_score
            }
        
        def get_results(self) -> Dict[str, Any]:
            """Get aggregated A/B test results."""
            avg_quality_a = sum(r.get('quality_score', 0) for r in self._results_a) / len(self._results_a) if self._results_a else 0
            avg_quality_b = sum(r.get('quality_score', 0) for r in self._results_b) / len(self._results_b) if self._results_b else 0
            
            return {
                "test_name": self.config.test_name,
                "strategy_a": self.config.strategy_a.value,
                "strategy_b": self.config.strategy_b.value,
                "samples_a": len(self._results_a),
                "samples_b": len(self._results_b),
                "avg_quality_a": avg_quality_a,
                "avg_quality_b": avg_quality_b,
                "winner": self.config.strategy_a.value if avg_quality_a > avg_quality_b else self.config.strategy_b.value
            }
    
    def create_ab_test(self, config: ABTestConfig) -> ABTestRunner:
        """Create an A/B test runner."""
        return self.ABTestRunner(self, config)
    
    # ==================== Complete RAG Trace ====================
    
    def create_rag_trace(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create a complete RAG trace that includes all operations.
        
        Returns a context manager that tracks the entire RAG pipeline.
        """
        if not self.enabled or not self._initialized:
            return _DummyRAGTrace()
        
        return _RAGTraceContext(
            tracker=self,
            query=query,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata
        )


class _RAGTraceContext:
    """Context manager for complete RAG trace tracking."""
    
    def __init__(
        self,
        tracker: LangfuseRAGTracker,
        query: str,
        session_id: Optional[str],
        user_id: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ):
        self.tracker = tracker
        self.query = query
        self.session_id = session_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self._trace = None
        self._start_time = None
        self._embedding_metrics = None
        self._retrieval_metrics = None
        self._llm_metrics = None
    
    def __enter__(self):
        self._start_time = time.time()
        self._trace = self.tracker._langfuse.trace(
            name="rag_query",
            input={"query": self.query},
            user_id=self.user_id,
            session_id=self.session_id,
            metadata=self.metadata
        )
        return self
    
    def track_embedding(self, **kwargs):
        """Track embedding operation."""
        self._embedding_metrics = self.tracker.track_embedding_usage(**kwargs)
        return self._embedding_metrics
    
    def track_retrieval(self, **kwargs):
        """Track retrieval operation."""
        self._retrieval_metrics = self.tracker.track_retrieval(**kwargs)
        return self._retrieval_metrics
    
    def track_llm(self, **kwargs):
        """Track LLM generation."""
        self._llm_metrics = self.tracker.track_llm_usage(**kwargs)
        return self._llm_metrics
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        total_time_ms = (end_time - self._start_time) * 1000
        
        # Calculate total cost
        total_cost = self.tracker.track_total_cost(
            self._embedding_metrics or CostMetrics(),
            self._llm_metrics or CostMetrics()
        )
        
        # Update trace with final output
        self._trace.update(
            output={
                "total_time_ms": total_time_ms,
                "total_cost_usd": total_cost.total_cost_usd,
                "num_documents_retrieved": self._retrieval_metrics.num_documents_retrieved if self._retrieval_metrics else 0
            },
            usage={
                "total_time_ms": total_time_ms,
                "total_cost_usd": total_cost.total_cost_usd
            }
        )
        
        logger.info(f"✅ RAG trace completed in {total_time_ms:.2f}ms")


class _DummyRAGTrace:
    """Dummy trace for when Langfuse is disabled."""
    
    def __enter__(self):
        return self
    
    def track_embedding(self, **kwargs):
        return CostMetrics()
    
    def track_retrieval(self, **kwargs):
        return RetrievalMetrics(0, 0, 0, 0, 0)
    
    def track_llm(self, **kwargs):
        return CostMetrics()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# ==================== Singleton Instance ====================

_tracker_instance: Optional[LangfuseRAGTracker] = None


def get_langfuse_tracker() -> LangfuseRAGTracker:
    """Get the singleton Langfuse tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = LangfuseRAGTracker()
    return _tracker_instance
