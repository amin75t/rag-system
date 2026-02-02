from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import SignUpSerializer, LoginSerializer, UserSerializer
from .models import User


@swagger_auto_schema(
    method='post',
    operation_description="Register a new user with phone and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password', 'password_confirm'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='User phone number (unique)'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username (optional)'),
        }
    ),
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'user': openapi.Schema(type=openapi.TYPE_OBJECT)
            }
        ),
        400: "Bad Request"
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({
        'message': 'User created successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_description="Login with phone and password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone', 'password'],
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='User phone number'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'user': openapi.Schema(type=openapi.TYPE_OBJECT)
            }
        ),
        400: "Bad Request",
        401: "Unauthorized"
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    login(request, user)
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Logout the current user",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get current user profile",
    responses={
        200: UserSerializer,
        401: "Unauthorized"
    },
    tags=['User']
)
@swagger_auto_schema(
    method='put',
    operation_description="Update current user profile",
    request_body=UserSerializer,
    responses={
        200: UserSerializer,
        401: "Unauthorized"
    },
    tags=['User']
)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
