"""
Serializers for RAG chat endpoints.

This module defines Django REST Framework serializers for
handling chat requests and responses.
"""
from rest_framework import serializers
from typing import List, Dict, Any


class DocumentSerializer(serializers.Serializer):
    """Serializer for document input."""
    id = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=True)
    metadata = serializers.DictField(required=False, default=dict)


class AddDocumentsSerializer(serializers.Serializer):
    """Serializer for adding documents to the knowledge base."""
    documents = DocumentSerializer(many=True, required=True)


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request."""
    query = serializers.CharField(required=True, max_length=5000)
    include_history = serializers.BooleanField(default=True)
    use_rag = serializers.BooleanField(default=True)
    similarity_top_k = serializers.IntegerField(default=7, min_value=1, max_value=20)
    temperature = serializers.FloatField(default=0.3, min_value=0.0, max_value=2.0)
    max_tokens = serializers.IntegerField(default=2048, min_value=100, max_value=8192)


class SourceSerializer(serializers.Serializer):
    """Serializer for document source information."""
    id = serializers.CharField()
    similarity = serializers.FloatField()
    metadata = serializers.DictField(default=dict)


class UsageSerializer(serializers.Serializer):
    """Serializer for token usage information."""
    prompt_tokens = serializers.IntegerField(required=False, allow_null=True)
    completion_tokens = serializers.IntegerField(required=False, allow_null=True)
    total_tokens = serializers.IntegerField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    response = serializers.CharField()
    context = serializers.CharField(required=False, allow_null=True)
    sources = SourceSerializer(many=True, default=list)
    model = serializers.CharField(required=False, allow_blank=True)
    usage = UsageSerializer(required=False, allow_null=True)


class HistoryItemSerializer(serializers.Serializer):
    """Serializer for conversation history item."""
    role = serializers.ChoiceField(choices=['user', 'assistant', 'system'])
    content = serializers.CharField()


class ChatHistorySerializer(serializers.Serializer):
    """Serializer for conversation history response."""
    history = HistoryItemSerializer(many=True)


class SystemPromptSerializer(serializers.Serializer):
    """Serializer for updating system prompt."""
    system_prompt = serializers.CharField(required=True, max_length=10000)
