from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Requires phone, password, password_confirm, and optional username.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['phone', 'password', 'password_confirm', 'username']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Requires phone and password.
    """
    phone = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, 
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            user = authenticate(request=self.context.get('request'), username=phone, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include phone and password.')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    class Meta:
        model = User
        fields = ['id', 'phone', 'username', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']
