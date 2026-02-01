"""
Views for RAG chat endpoints.

This module provides Django REST Framework views for
handling chat requests and document management.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .chat_manager import get_chat_manager
from .serializers import (
    AddDocumentsSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatHistorySerializer,
    SystemPromptSerializer,
)

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """
    API endpoint for chat interactions with RAG system.
    
    POST /api/rag/chat/
    """
    
    @swagger_auto_schema(
        operation_description="Send a chat message to the RAG system",
        request_body=ChatRequestSerializer,
        responses={
            200: ChatResponseSerializer,
            400: "Bad Request",
            500: "Internal Server Error"
        },
        tags=['RAG Chat']
    )
    def post(self, request):
        """
        Process a chat request.
        
        Request body:
        {
            "query": "User question",
            "include_history": true,
            "use_rag": true,
            "similarity_top_k": 7,
            "temperature": 0.3,
            "max_tokens": 2048
        }
        """
        try:
            # Validate request
            serializer = ChatRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data = serializer.validated_data
            
            # Get chat manager
            chat_manager = get_chat_manager()
            
            # Process chat
            result = chat_manager.chat(
                user_query=data['query'],
                include_history=data['include_history'],
                use_rag=data['use_rag']
            )
            
            # Serialize response
            response_serializer = ChatResponseSerializer(result)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in chat view: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddDocumentsView(APIView):
    """
    API endpoint for adding documents to the knowledge base.
    
    POST /api/rag/documents/
    """
    
    @swagger_auto_schema(
        operation_description="Add documents to the RAG knowledge base",
        request_body=AddDocumentsSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'document_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        },
        tags=['RAG Chat']
    )
    def post(self, request):
        """
        Add documents to the knowledge base.
        
        Request body:
        {
            "documents": [
                {
                    "id": "doc1",
                    "content": "Document content",
                    "metadata": {"key": "value"}
                }
            ]
        }
        """
        try:
            # Validate request
            serializer = AddDocumentsSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data = serializer.validated_data
            documents = data['documents']
            
            # Get chat manager and add documents
            chat_manager = get_chat_manager()
            chat_manager.add_documents(documents)
            
            return Response(
                {
                    'message': f'Successfully added {len(documents)} documents',
                    'document_count': len(documents)
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    """
    API endpoint for retrieving conversation history.
    
    GET /api/rag/history/
    DELETE /api/rag/history/
    """
    
    @swagger_auto_schema(
        operation_description="Get conversation history",
        responses={
            200: ChatHistorySerializer,
            500: "Internal Server Error"
        },
        tags=['RAG Chat']
    )
    def get(self, request):
        """
        Retrieve conversation history.
        """
        try:
            chat_manager = get_chat_manager()
            history = chat_manager.get_history()
            
            serializer = ChatHistorySerializer({'history': history})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Clear conversation history",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            500: "Internal Server Error"
        },
        tags=['RAG Chat']
    )
    def delete(self, request):
        """
        Clear conversation history.
        """
        try:
            chat_manager = get_chat_manager()
            chat_manager.clear_history()
            
            return Response(
                {'message': 'Conversation history cleared'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemPromptView(APIView):
    """
    API endpoint for updating the system prompt.
    
    PUT /api/rag/system-prompt/
    """
    
    @swagger_auto_schema(
        operation_description="Update the system prompt",
        request_body=SystemPromptSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        },
        tags=['RAG Chat']
    )
    def put(self, request):
        """
        Update the system prompt.
        
        Request body:
        {
            "system_prompt": "New system prompt text"
        }
        """
        try:
            # Validate request
            serializer = SystemPromptSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data = serializer.validated_data
            system_prompt = data['system_prompt']
            
            # Update system prompt
            chat_manager = get_chat_manager()
            chat_manager.set_system_prompt(system_prompt)
            
            return Response(
                {'message': 'System prompt updated successfully'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error updating system prompt: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    API endpoint for health check.
    
    GET /api/rag/health/
    """
    
    @swagger_auto_schema(
        operation_description="Check RAG system health",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'documents_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'history_length': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        },
        tags=['RAG Chat']
    )
    def get(self, request):
        """
        Check system health status.
        """
        try:
            chat_manager = get_chat_manager()
            
            return Response(
                {
                    'status': 'healthy',
                    'documents_count': len(chat_manager.documents),
                    'history_length': len(chat_manager.conversation_history)
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return Response(
                {
                    'status': 'unhealthy',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
