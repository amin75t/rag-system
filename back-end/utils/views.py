"""
Views for testing utils functionality.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .api_client import test_api_connection, APIClient
from .date_utils import miladi_to_samci_date, DateConverter
from .alpha_api import get_alpha_api_client, get_embeddings


@swagger_auto_schema(
    method='get',
    operation_description="Test API connection to an external service",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT)
            }
        )
    },
    tags=['Utils']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    """
    Test API connection endpoint.
    Returns data from a test API (jsonplaceholder.typicode.com).
    """
    result = test_api_connection()
    return Response(result)


@swagger_auto_schema(
    method='post',
    operation_description="Convert Miladi (Gregorian) date to Samci (Shamsi) date",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['year', 'month', 'day'],
        properties={
            'year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Gregorian year'),
            'month': openapi.Schema(type=openapi.TYPE_INTEGER, description='Gregorian month (1-12)'),
            'day': openapi.Schema(type=openapi.TYPE_INTEGER, description='Gregorian day'),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'year': openapi.Schema(type=openapi.TYPE_INTEGER),
                'month': openapi.Schema(type=openapi.TYPE_INTEGER),
                'day': openapi.Schema(type=openapi.TYPE_INTEGER),
                'formatted': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    },
    tags=['Utils']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def convert_miladi_to_samci(request):
    """
    Convert Miladi (Gregorian) date to Samci (Shamsi) date.
    
    Request body:
        {
            "year": 2024,
            "month": 1,
            "day": 31
        }
    """
    data = request.data
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    
    if not all([year, month, day]):
        return Response(
            {'error': 'Please provide year, month, and day'},
            status=400
        )
    
    try:
        result = DateConverter.miladi_to_samci(year, month, day)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=500
        )


@swagger_auto_schema(
    method='post',
    operation_description="Convert Samci (Shamsi) date to Miladi (Gregorian) date",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['year', 'month', 'day'],
        properties={
            'year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Shamsi year'),
            'month': openapi.Schema(type=openapi.TYPE_INTEGER, description='Shamsi month (1-12)'),
            'day': openapi.Schema(type=openapi.TYPE_INTEGER, description='Shamsi day'),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'year': openapi.Schema(type=openapi.TYPE_INTEGER),
                'month': openapi.Schema(type=openapi.TYPE_INTEGER),
                'day': openapi.Schema(type=openapi.TYPE_INTEGER),
                'formatted': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    },
    tags=['Utils']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def convert_samci_to_miladi(request):
    """
    Convert Samci (Shamsi) date to Miladi (Gregorian) date.
    
    Request body:
        {
            "year": 1402,
            "month": 11,
            "day": 10
        }
    """
    data = request.data
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    
    if not all([year, month, day]):
        return Response(
            {'error': 'Please provide year, month, and day'},
            status=400
        )
    
    try:
        result = DateConverter.samci_to_miladi(year, month, day)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=500
        )


@swagger_auto_schema(
    method='post',
    operation_description="Send a chat completion request to Alpha API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['messages'],
        properties={
            'messages': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['role', 'content'],
                    properties={
                        'role': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Message role (system, user, assistant)',
                            enum=['system', 'user', 'assistant']
                        ),
                        'content': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Message content'
                        ),
                    }
                )
            ),
            'model': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Model name (optional, uses default if not provided)'
            ),
            'temperature': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Sampling temperature (0.0 - 2.0)'
            ),
            'max_tokens': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Maximum tokens to generate'
            ),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Chat completion response from Alpha API'
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        500: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
    },
    tags=['Alpha API']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def alpha_chat_completion(request):
    """
    Send a chat completion request to Alpha API.
    
    Request body:
        {
            "messages": [
                {"role": "user", "content": "What is the capital of Iran?"}
            ],
            "model": "DeepSeek-V3.1",  // optional
            "temperature": 0.7,  // optional
            "max_tokens": 1000  // optional
        }
    """
    data = request.data
    messages = data.get('messages')
    
    if not messages:
        return Response(
            {'error': 'Please provide messages array'},
            status=400
        )
    
    try:
        # Get Alpha API client singleton
        client = get_alpha_api_client()
        
        # Extract optional parameters
        model = data.get('model')
        kwargs = {}
        
        if 'temperature' in data:
            kwargs['temperature'] = data['temperature']
        if 'max_tokens' in data:
            kwargs['max_tokens'] = data['max_tokens']
        
        # Send chat completion request
        result = client.chat_completion(messages, model, **kwargs)
        return Response(result)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=400
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=500
        )


@swagger_auto_schema(
    method='post',
    operation_description="Send an embeddings request to Alpha API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['input'],
        properties={
            'input': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Text or list of texts to embed'
            ),
            'model': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Model name (optional, uses default if not provided)'
            ),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Embeddings response from Alpha API'
        ),
        400: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        500: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
    },
    tags=['Alpha API']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def alpha_embeddings(request):
    """
    Send an embeddings request to Alpha API.
    
    Request body:
        {
            "input": "What is the capital of Iran?",  // or array of strings
            "model": "baai-bge-m3"  // optional
        }
    """
    data = request.data
    input_data = data.get('input')
    
    if not input_data:
        return Response(
            {'error': 'Please provide input text or array of texts'},
            status=400
        )
    
    try:
        # Get embeddings
        model = data.get('model')
        result = get_embeddings(input_data, model)
        return Response(result)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=400
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=500
        )


@swagger_auto_schema(
    method='post',
    operation_description="RAG Chat - Chat with documents using vector database",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['query'],
        properties={
            'query': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='User query/question'
            ),
            'n_results': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Number of relevant documents to retrieve (default: 5)'
            ),
            'temperature': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Sampling temperature (0.0 - 2.0, default: 0.7)'
            ),
            'max_tokens': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Maximum tokens to generate (default: 1000)'
            ),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'answer': openapi.Schema(type=openapi.TYPE_STRING),
                'sources': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'content': openapi.Schema(type=openapi.TYPE_STRING),
                            'metadata': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'distance': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                )
            }
        ),
        400: openapi.Schema(
            type=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        500: openapi.Schema(
            type=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
    },
    tags=['RAG']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def rag_chat(request):
    """
    RAG Chat - Chat with documents using vector database.
    
    This endpoint:
    1. Embeds the user query using the embeddings API
    2. Searches the vector database for relevant documents
    3. Uses the chat API to generate an answer based on retrieved context
    
    Request body:
        {
            "query": "What is the main topic of the documents?",
            "n_results": 5,  // optional, default: 5
            "temperature": 0.7,  // optional
            "max_tokens": 1000  // optional
        }
    """
    import sys
    from pathlib import Path
    
    # Add project root to path (parent of Ai directory)
    # __file__ = back-end/utils/views.py
    # .parent = back-end/utils/
    # .parent.parent = back-end/
    # .parent.parent.parent = project root (where Ai/ is located)
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # Now we can import from Ai.rag
    from Ai.rag.vector_db import get_vector_db_manager
    
    data = request.data
    query = data.get('query')
    
    if not query:
        return Response(
            {'error': 'Please provide a query'},
            status=400
        )
    
    n_results = data.get('n_results', 5)
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 1000)
    
    try:
        # Step 1: Get embedding for the query using embeddings API
        client = get_alpha_api_client()
        embedding_response = client.embeddings(query)
        embedding_vector = client.extract_embeddings(embedding_response)[0]
        print(f"embad the request embedding_response:{embedding_response}")
        print(f"embad the request embedding_vector:{embedding_vector}")

        # Step 2: Query the vector database for relevant documents
        
        print("=" * 70)
        print("DEBUG: Vector Database Connection Info")
        print("=" * 70)
        print(f"Current working directory: {os.getcwd()}")
        print(f"VECTOR_DB_PATH env var: {os.getenv('VECTOR_DB_PATH', 'NOT SET')}")
        
        # Check both possible database locations
        # Location 1: Ai/db/vector_db (correct location)
        vector_db_path_1 = Path("/mnt/d/projact/rag-new/rag-system/Ai/db/vector_db")
        # Location 2: Ai/rag/Ai/db/vector_db (incorrect nested path from indexing script)
        vector_db_path_2 = Path("Ai/rag/Ai/db/vector_db")
        
        print(f"Checking database location 1: {vector_db_path_1.absolute()}")
        print(f"  Exists: {vector_db_path_1.exists()}")
        if vector_db_path_1.exists():
            print(f"  Contents: {[item.name for item in vector_db_path_1.iterdir()]}")
        
        print(f"\nChecking database location 2: {vector_db_path_2.absolute()}")
        print(f"  Exists: {vector_db_path_2.exists()}")
        if vector_db_path_2.exists():
            print(f"  Contents: {[item.name for item in vector_db_path_2.iterdir()]}")
        
        # Use database that has data (location 2 has indexed documents)
        vector_db_path = vector_db_path_2 if vector_db_path_2.exists() else vector_db_path_1
        
        print(f"\nUsing database path: {vector_db_path.absolute()}")
        
        vector_db = get_vector_db_manager(
                collection_name="documents",
                persist_directory=str(vector_db_path)
        )
        
        print(f"Vector DB persist directory: {vector_db.persist_directory.absolute()}")
        print(f"Vector DB collection name: {vector_db.collection_name}")
        
        # DEBUG: Check how many documents are in the database
        doc_count = vector_db.count()
        print(f"Document count in collection: {doc_count}")
        
        # List all collections in the database
        try:
            all_collections = vector_db.client.list_collections()
            print(f"All collections in database: {[c.name for c in all_collections]}")
        except Exception as e:
            print(f"Error listing collections: {e}")
        
        print("=" * 70)
        
        search_results = vector_db.query(
            query_embeddings=[embedding_vector],
            n_results=n_results
        )
        
        # DEBUG: Log search results
        print(f"DEBUG: Document count in DB: {doc_count}")
        print(f"DEBUG: Search results keys: {search_results.keys()}")
        print(f"DEBUG: Search results: {search_results}")
        
        # Step 3: Build context from retrieved documents
        sources = []
        context_parts = []
        
        if search_results.get('documents') and search_results['documents'][0]:
            for i, doc in enumerate(search_results['documents'][0]):
                metadata = {}
                if search_results.get('metadatas') and search_results['metadatas'][0]:
                    metadata = search_results['metadatas'][0][i] or {}
                
                distance = None
                if search_results.get('distances') and search_results['distances'][0]:
                    distance = search_results['distances'][0][i]
                
                sources.append({
                    'content': doc,
                    'metadata': metadata,
                    'distance': distance
                })
                context_parts.append(doc)
        
        context = "\n\n".join(context_parts)
        
        # DEBUG: Log context
        print(f"DEBUG: Number of retrieved documents: {len(context_parts)}")
        print(f"DEBUG: Context length: {len(context)}")
        print(f"DEBUG: Context preview: {context[:500] if context else 'EMPTY'}")
        
        # Step 4: Generate answer using chat API with context
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer the question. If the answer is not in the context, say "I don't have enough information to answer this question."
Be concise and accurate."""
        
        user_message = f"""Context:
{context}

Question: {query}

Answer:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # DEBUG: Log messages being sent to chat API
        print(f"DEBUG: User message length: {len(user_message)}")
        
        chat_response = client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract answer from chat response
        answer = ""
        if 'choices' in chat_response and len(chat_response['choices']) > 0:
            answer = chat_response['choices'][0].get('message', {}).get('content', '')
        else:
            answer = str(chat_response)
        
        return Response({
            'answer': answer,
            'sources': sources,
            'debug': {
                'document_count': doc_count,
                'retrieved_count': len(context_parts),
                'context_length': len(context)
            }
        })
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=400
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=500
        )


@swagger_auto_schema(
    method='get',
    operation_description="Debug endpoint to check vector database contents",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'sample_documents': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            }
        )
    },
    tags=['RAG']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def rag_debug(request):
    """
    Debug endpoint to check vector database contents.
    
    Returns information about the vector database including:
    - Total document count
    - Sample documents
    """
    import sys
    from pathlib import Path
    
    # Add project root to path (parent of Ai directory)
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    from Ai.rag.vector_db import get_vector_db_manager, inspect_vector_db_directory
    
    try:
        # Check both possible database locations
        vector_db_path_1 = Path("/mnt/d/projact/rag-new/rag-system/Ai/db/vector_db")
        vector_db_path_2 = Path("Ai/rag/Ai/db/vector_db")
        
        # Use database that has data (location 2 has indexed documents)
        vector_db_path = vector_db_path_2 if vector_db_path_2.exists() else vector_db_path_1
        
        # Get vector DB directory inspection
        inspection = inspect_vector_db_directory(str(vector_db_path))
        
        # Get vector DB manager info
        vector_db = get_vector_db_manager(persist_directory=str(vector_db_path))
        count = vector_db.count()
        
        # List all collections
        all_collections = vector_db.client.list_collections()
        collection_info = []
        for coll in all_collections:
            collection_info.append({
                'name': coll.name,
                'count': coll.count()
            })
        
        # Get sample documents
        sample_limit = min(5, count) if count > 0 else 0
        sample_docs = []
        
        if sample_limit > 0:
            results = vector_db.get(limit=sample_limit)
            if results.get('documents'):
                sample_docs = results['documents'][:sample_limit]
        
        return Response({
            'directory_inspection': inspection,
            'current_collection': {
                'name': vector_db.collection_name,
                'count': count
            },
            'all_collections': collection_info,
            'sample_documents': sample_docs
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=500
        )
