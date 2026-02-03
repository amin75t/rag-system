"""
Custom authentication that reads token from HttpOnly cookie.
"""
from rest_framework.authentication import TokenAuthentication
from django.conf import settings


class TokenAuthenticationFromCookie(TokenAuthentication):
    """
    Custom token authentication that reads the token from an HttpOnly cookie.
    Falls back to the default header-based authentication if cookie is not found.
    """
    def authenticate(self, request):
        # Try to get token from HttpOnly cookie
        token = request.COOKIES.get('auth_token')
        
        if token:
            # Authenticate using the token from cookie
            return self.authenticate_credentials(token)
        
        # Fallback to default header-based authentication
        return super().authenticate(request)
