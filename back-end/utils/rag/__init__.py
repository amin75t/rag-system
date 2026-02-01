"""
RAG (Retrieval-Augmented Generation) module for the utils app.

This module provides chat functionality with document context retrieval
using the Alpha API for embeddings and chat completions.
"""

from .chat_manager import ChatManager, HYBRID_SYSTEM_PROMPT

__all__ = ['ChatManager', 'HYBRID_SYSTEM_PROMPT']
