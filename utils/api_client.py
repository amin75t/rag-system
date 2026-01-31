"""
API Client utility for making HTTP requests to external APIs.
"""
import requests
from typing import Dict, Any, Optional
from django.conf import settings


class APIClient:
    """
    Generic API client for making HTTP requests to external services.
    """
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict = None, json: Dict = None, 
              headers: Dict = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)
        response = self.session.post(url, data=data, json=json, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: Dict = None, json: Dict = None,
             headers: Dict = None) -> Dict[str, Any]:
        """
        Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)
        response = self.session.put(url, data=data, json=json, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str, params: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        url = self._build_url(endpoint)
        response = self.session.delete(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build the full URL from base URL and endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Full URL
        """
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint


# Example usage for testing
def test_api_connection(url: str = "https://jsonplaceholder.typicode.com/posts/1") -> Dict[str, Any]:
    """
    Test function to verify API connection works.
    
    Args:
        url: Test API URL
        
    Returns:
        Response data
    """
    client = APIClient()
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
