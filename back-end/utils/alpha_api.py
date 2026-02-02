"""
Alpha API Client - Modular and clean API client for chat completions and embeddings.
"""
import os
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


class AlphaAPIClient:
    """
    Modular API client for Alpha API.
    Handles chat completions and embeddings.
    """
    
    # API Configuration
    BASE_URL = os.getenv('API_BASE_URL', 'https://alphapi.aip.sharif.ir/v1/chat/completions')
    EMBEDDINGS_URL = os.getenv('EMBEDDINGS_URL', 'https://alphapi.aip.sharif.ir/v1/embeddings')
    API_TOKEN = os.getenv('API_TOKEN', '')
    DEFAULT_MODEL = os.getenv('API_MODEL', 'DeepSeek-V3.1')
    DEFAULT_EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'baai-bge-m3')
    
    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None, 
                 model: Optional[str] = None, timeout: int = 60):
        """
        Initialize the Alpha API client.
        
        Args:
            base_url: Custom base URL (optional, defaults to env var)
            api_token: Custom API token (optional, defaults to env var)
            model: Default model name (optional, defaults to env var)
            timeout: Request timeout in seconds (default: 60)
        """
        self.base_url = base_url or self.BASE_URL
        self.api_token = api_token or self.API_TOKEN
        self.default_model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        })
    
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request to the Alpha API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (optional, uses default if not provided)
            **kwargs: Additional parameters like temperature, max_tokens, etc.
            
        Returns:
            Response data as dictionary
            
        Raises:
            ValueError: If API token is not configured
            requests.RequestException: If the API request fails
            
        Example:
            >>> client = AlphaAPIClient()
            >>> messages = [
            ...     {"role": "user", "content": "What is the capital of Iran?"}
            ... ]
            >>> response = client.chat_completion(messages)
        """
        if not self.api_token:
            raise ValueError("API token is not configured. Please set API_TOKEN in .env file.")
        
        # Prepare request payload
        payload = {
            'model': model or self.default_model,
            'messages': messages
        }
        
        # Add optional parameters
        if kwargs:
            payload.update(kwargs)
        
        # Make the API request
        response = self._post(payload)
        return response
    
    def embeddings(self, input_data: Union[str, List[str]], model: Optional[str] = None,
                  **kwargs) -> Dict[str, Any]:
        """
        Send an embeddings request to the Alpha API.
        
        Args:
            input_data: Text or list of texts to embed
            model: Model name (optional, uses default if not provided)
            **kwargs: Additional parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            ValueError: If API token is not configured
            requests.RequestException: If the API request fails
            
        Example:
            >>> client = AlphaAPIClient()
            >>> response = client.embeddings("What is the capital of Iran?")
            >>> # Or with multiple texts
            >>> response = client.embeddings(["text1", "text2"])
        """
        if not self.api_token:
            raise ValueError("API token is not configured. Please set API_TOKEN in .env file.")
        
        # Prepare request payload
        payload = {
            'model': model or self.DEFAULT_EMBEDDING_MODEL,
            'input': input_data
        }
        
        # Add optional parameters
        if kwargs:
            payload.update(kwargs)
        
        # Make the API request to embeddings endpoint
        response = self._post_to_embeddings(payload)
        return response
    
    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make POST request.
        
        Args:
            payload: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_msg = self._extract_error_message(e.response)
            raise requests.RequestException(f"API request failed: {error_msg}") from e
        except requests.Timeout:
            raise requests.RequestException(f"Request timed out after {self.timeout} seconds")
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}") from e
    
    def _post_to_embeddings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to make POST request to embeddings endpoint.
        
        Args:
            payload: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            response = self.session.post(self.EMBEDDINGS_URL, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_msg = self._extract_error_message(e.response)
            raise requests.RequestException(f"Embeddings API request failed: {error_msg}") from e
        except requests.Timeout:
            raise requests.RequestException(f"Request timed out after {self.timeout} seconds")
        except requests.RequestException as e:
            raise requests.RequestException(f"Embeddings API request failed: {str(e)}") from e
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """
        Extract error message from API response.
        
        Args:
            response: HTTP response object
            
        Returns:
            Error message string
        """
        try:
            error_data = response.json()
            return error_data.get('error', {}).get('message', response.text)
        except (ValueError, KeyError):
            return response.text
    
    def set_model(self, model: str) -> None:
        """
        Set the default model for future requests.
        
        Args:
            model: Model name
        """
        self.default_model = model
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set the request timeout.
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
    
    def validate_configuration(self) -> bool:
        """
        Validate that the client is properly configured.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.base_url:
            raise ValueError("Base URL is not configured.")
        if not self.api_token:
            raise ValueError("API token is not configured.")
        if not self.default_model:
            raise ValueError("Model name is not configured.")
        return True


# Convenience function for quick usage
def get_chat_completion(messages: List[Dict[str, str]], model: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
    """
    Convenience function to get a chat completion without instantiating the client.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (optional)
        **kwargs: Additional parameters
        
    Returns:
        Response data as dictionary
        
    Example:
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = get_chat_completion(messages)
    """
    client = AlphaAPIClient()
    return client.chat_completion(messages, model, **kwargs)


# Convenience function for embeddings
def get_embeddings(input_data: Union[str, List[str]], model: Optional[str] = None,
                  **kwargs) -> Dict[str, Any]:
    """
    Convenience function to get embeddings without instantiating client.
    
    Args:
        input_data: Text or list of texts to embed
        model: Model name (optional)
        **kwargs: Additional parameters
        
    Returns:
        Response data as dictionary
        
    Example:
        >>> response = get_embeddings("Hello world!")
        >>> # Or with multiple texts
        >>> response = get_embeddings(["text1", "text2"])
    """
    client = AlphaAPIClient()
    return client.embeddings(input_data, model, **kwargs)


# Singleton instance for global use
_alpha_api_client: Optional[AlphaAPIClient] = None


def get_alpha_api_client() -> AlphaAPIClient:
    """
    Get or create a singleton instance of AlphaAPIClient.
    
    Returns:
        AlphaAPIClient instance
    """
    global _alpha_api_client
    if _alpha_api_client is None:
        _alpha_api_client = AlphaAPIClient()
    return _alpha_api_client
