"""
Qwen-powered Query Agent - Convert natural language to SQL using Qwen3:14B
"""

from .intelligent_agent import IntelligentQueryAgent
from .schemas import SchemaManager, TestSchema
from .utils.local_llm import LocalLLMFactory, OllamaLLM

__version__ = "1.0.0"
__author__ = "Qwen Query Agent Team"

__all__ = [
    'IntelligentQueryAgent',
    'SchemaManager',
    'TestSchema',
    'LocalLLMFactory',
    'OllamaLLM',
    'cli_main'
]