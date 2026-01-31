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
