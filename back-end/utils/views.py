"""
Views for testing utils functionality.
"""
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
                oneOf=[
                    openapi.Schema(type=openapi.TYPE_STRING, description='Text to embed'),
                    openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description='List of texts to embed'
                    )
                ],
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
