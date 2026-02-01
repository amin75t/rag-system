"""
Chat Manager for RAG system using Alpha API.

This module provides a chat system that combines document context retrieval
with the Alpha API's chat completion and embedding capabilities.
"""
import logging
from typing import List, Dict, Any, Optional
from ..alpha_api import AlphaAPIClient, get_alpha_api_client

logger = logging.getLogger(__name__)


# =====================================================================
# SYSTEM PROMPT: THE ELOQUENT EXPERT (استاد سخنور و دانا)
# =====================================================================
HYBRID_SYSTEM_PROMPT = (
    "You are a highly intelligent, eloquent, and comprehensive AI consultant named 'Dastyar'.\n"
    "Your goal is to provide extensive, well-structured, and professional responses in Persian.\n"
    "\n"
    "### CORE INSTRUCTIONS:\n"
    "1. **Seamless Knowledge Integration (Hybrid RAG):**\n"
    "   - You have access to a specific set of documents (Context).\n"
    "   - Use the Context as your PRIMARY source for facts, numbers, and specific entities.\n"
    "   - **CRITICAL:** IF the answer is NOT in the Context, you MUST use your own vast general knowledge to answer.\n"
    "   - **NEVER** state 'I could not find this in the documents' or 'The text does not mention this'.\n"
    "   - Blend the document information and your general knowledge so seamlessly that the user cannot tell the difference.\n"
    "\n"
    "2. **Elaboration & Eloquence (Sokhanvari):**\n"
    "   - **Never give one-line answers.** Always expand on the topic.\n"
    "   - Explain the 'Why' and 'How', not just the 'What'.\n"
    "   - Use a professional, academic, yet engaging tone.\n"
    "   - Structure your answer with a proper **Introduction**, detailed **Body Paragraphs**, and a **Conclusion**.\n"
    "   - Use bullet points for clarity, but surround them with descriptive text.\n"
    "\n"
    "3. **Handling Missing Data:**\n"
    "   - If asked about specific statistics (e.g., 'Population of Bushehr in 1402') and it's NOT in the docs:\n"
    "     - Provide the latest general estimate you know from your training data.\n"
    "     - Do not fabricate specific numbers if you don't know them, but discuss the importance of that metric conceptually.\n"
    "\n"
    "4. **Language:**\n"
    "   - Always respond in fluent, formal Persian (Farsi).\n"
)


class ChatManager:
    """
    Chat Manager for RAG system using Alpha API.
    
    This class manages chat sessions with document context retrieval,
    using Alpha API for both embeddings (for similarity search) and
    chat completions.
    """
    
    def __init__(
        self,
        api_client: Optional[AlphaAPIClient] = None,
        chat_model: Optional[str] = None,
        embedding_model: Optional[str] = None,
        similarity_top_k: int = 7,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        """
        Initialize the Chat Manager.
        
        Args:
            api_client: AlphaAPIClient instance (uses singleton if not provided)
            chat_model: Model name for chat completions
            embedding_model: Model name for embeddings
            similarity_top_k: Number of similar documents to retrieve
            temperature: Temperature for chat generation
            max_tokens: Maximum tokens in response
        """
        self.api_client = api_client or get_alpha_api_client()
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.similarity_top_k = similarity_top_k
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Store conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Document storage (in-memory for now, can be replaced with vector DB)
        self.documents: List[Dict[str, Any]] = []
        
        logger.info("ChatManager initialized successfully")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of documents with 'id', 'content', and optional 'metadata'
        """
        for doc in documents:
            if 'id' not in doc:
                doc['id'] = str(len(self.documents))
            if 'content' not in doc:
                raise ValueError(f"Document must have 'content' field: {doc}")
            self.documents.append(doc)
        
        logger.info(f"Added {len(documents)} documents to knowledge base")
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using Alpha API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.api_client.embeddings(
                input_data=texts,
                model=self.embedding_model
            )
            embeddings = [item['embedding'] for item in response.get('data', [])]
            return embeddings
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise
    
    def _retrieve_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on query using similarity search.
        
        Args:
            query: User query string
            
        Returns:
            List of relevant documents with similarity scores
        """
        if not self.documents:
            return []
        
        # Get embedding for query
        query_embedding = self._get_embeddings([query])[0]
        
        # Get embeddings for all documents
        doc_texts = [doc['content'] for doc in self.documents]
        doc_embeddings = self._get_embeddings(doc_texts)
        
        # Calculate cosine similarity
        import numpy as np
        
        similarities = []
        for doc, doc_emb in zip(self.documents, doc_embeddings):
            query_vec = np.array(query_embedding)
            doc_vec = np.array(doc_emb)
            
            # Cosine similarity
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
            )
            similarities.append({
                'document': doc,
                'similarity': float(similarity)
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:self.similarity_top_k]
    
    def _format_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            relevant_docs: List of documents with similarity scores
            
        Returns:
            Formatted context string
        """
        if not relevant_docs:
            return "No relevant documents found in the knowledge base."
        
        context_parts = []
        for i, item in enumerate(relevant_docs, 1):
            doc = item['document']
            context_parts.append(
                f"[Document {i}] (Similarity: {item['similarity']:.3f})\n"
                f"{doc['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_messages(
        self,
        user_query: str,
        context: str,
        include_history: bool = True
    ) -> List[Dict[str, str]]:
        """
        Build message list for chat completion.
        
        Args:
            user_query: User's query
            context: Retrieved document context
            include_history: Whether to include conversation history
            
        Returns:
            List of message dictionaries
        """
        messages = [
            {
                "role": "system",
                "content": HYBRID_SYSTEM_PROMPT
            }
        ]
        
        # Add context to the first user message
        context_template = (
            "Below is some context information from the uploaded documents:\n"
            "---------------------\n"
            "{context}\n"
            "---------------------\n"
            "Using the context above as a reference (if relevant), AND your own extensive knowledge, "
            "provide a detailed, comprehensive, and eloquent answer to the following query.\n"
            "Do NOT limit yourself to the context if it is insufficient. Expand on the topic.\n"
        )
        
        first_message = context_template.format(context=context)
        first_message += f"\n\nQuery: {user_query}"
        
        messages.append({
            "role": "user",
            "content": first_message
        })
        
        return messages
    
    def chat(
        self,
        user_query: str,
        include_history: bool = True,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            user_query: User's query string
            include_history: Whether to include conversation history
            use_rag: Whether to use RAG (document retrieval)
            
        Returns:
            Dictionary with 'response', 'context', and 'sources'
        """
        try:
            # Retrieve relevant documents if RAG is enabled
            context = ""
            sources = []
            
            if use_rag and self.documents:
                relevant_docs = self._retrieve_relevant_documents(user_query)
                context = self._format_context(relevant_docs)
                sources = [
                    {
                        'id': item['document'].get('id'),
                        'similarity': item['similarity'],
                        'metadata': item['document'].get('metadata', {})
                    }
                    for item in relevant_docs
                ]
            
            # Build messages
            messages = self._build_messages(user_query, context, include_history)
            
            # Get chat completion from Alpha API
            response = self.api_client.chat_completion(
                messages=messages,
                model=self.chat_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response text
            response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Limit history size
            max_history = 10
            if len(self.conversation_history) > max_history * 2:
                self.conversation_history = self.conversation_history[-max_history * 2:]
            
            return {
                'response': response_text,
                'context': context if use_rag else None,
                'sources': sources if use_rag else [],
                'model': response.get('model', self.chat_model),
                'usage': response.get('usage', {})
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, system_prompt: str) -> None:
        """
        Set a custom system prompt.
        
        Args:
            system_prompt: New system prompt string
        """
        global HYBRID_SYSTEM_PROMPT
        HYBRID_SYSTEM_PROMPT = system_prompt
        logger.info("System prompt updated")


# Singleton instance
_chat_manager: Optional[ChatManager] = None


def get_chat_manager(**kwargs) -> ChatManager:
    """
    Get or create a singleton instance of ChatManager.
    
    Returns:
        ChatManager instance
    """
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = ChatManager(**kwargs)
    return _chat_manager
