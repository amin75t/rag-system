"""
Local LLM interface specifically for Qwen3:14b
"""
from typing import Optional, Generator
from abc import ABC, abstractmethod
import requests
from typing import Generator

class BaseLLM(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, system_prompt: str = None, **kwargs) -> Generator[str, None, None]:
        """Stream response from LLM"""
        pass


class OllamaLLM(BaseLLM):
    """Correct Ollama implementation for Qwen3:14b"""

    def __init__(
        self,
        model: str = "qwen3:14b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 300,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

        # healthcheck
        self.available = self._healthcheck()

    def _healthcheck(self) -> bool:
        try:
            r = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            r.raise_for_status()

            models = [m["name"] for m in r.json().get("models", [])]
            return self.model in models

        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.available:
            return self._fallback_generate(prompt, system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.1),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("max_tokens", 1500),
            },
        }

        r = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()

        return r.json()["message"]["content"]

    def stream_generate(
        self,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> Generator[str, None, None]:

        if not self.available:
            yield self._fallback_generate(prompt, system_prompt)
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        with requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=self.timeout,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                data = line.decode("utf-8")
                if data.startswith("data:"):
                    chunk = data.removeprefix("data:").strip()
                    if chunk and chunk != "[DONE]":
                        yield chunk

    def _fallback_generate(self, prompt: str, system_prompt: str = None) -> str:
        return "[Ollama not available]"
    
    def test_connection(self) -> bool:
        """Test if Ollama is connected and model is available"""
        return self.available


class LocalLLMFactory:
    """Factory for creating local LLM instances for Qwen3:14b"""
    
    @staticmethod
    def create_llm(llm_type: str = "ollama", **kwargs) -> BaseLLM:
        """
        Create LLM instance based on type with Qwen3:14b as default
        
        Args:
            llm_type: Type of LLM (ollama, vllm, litellm)
            **kwargs: Additional arguments for the LLM
            
        Returns:
            BaseLLM instance
        """
        if llm_type == "ollama":
            return OllamaLLM(
                model=kwargs.get("model", "qwen3:14b"),
                base_url=kwargs.get("base_url", "http://localhost:11434")
            )
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
    
    @staticmethod
    def detect_available_llm() -> Optional[BaseLLM]:
        """Try to detect and create an available LLM, preferring Qwen3:14b"""
        llm_priority = ["ollama", "vllm", "litellm"]
        
        for llm_type in llm_priority:
            try:
                llm = LocalLLMFactory.create_llm(llm_type)
                
                # Test connection
                if llm_type == "ollama" and hasattr(llm, 'test_connection'):
                    if llm.test_connection():
                        print(f"✓ Detected Ollama with Qwen3:14b")
                        return llm
                else:
                    # For other types, try a simple generation
                    test_response = llm.generate("test", max_tokens=5)
                    if "not available" not in test_response.lower():
                        print(f"✓ Detected {llm_type}")
                        return llm
                        
            except Exception as e:
                print(f"  {llm_type} not available: {e}")
                continue
        
        print("✗ No local LLM detected. Using rule-based fallback.")
        return None
    
    @staticmethod
    def get_available_models() -> dict:
        """Get available Qwen3 models for each LLM type"""
        return {
            "ollama": [
                "qwen3:14b",
                "qwen3:14b-instruct",
                "qwen3:7b",
                "qwen3:7b-instruct"
            ],
            "vllm": [
                "Qwen/Qwen3-14B",
                "Qwen/Qwen3-14B-Instruct",
                "Qwen/Qwen3-7B",
                "Qwen/Qwen3-7B-Instruct"
            ],
            "litellm": [
                "ollama/qwen3:14b",
                "ollama/qwen3:14b-instruct",
                "ollama/qwen3:7b",
                "ollama/qwen3:7b-instruct"
            ]
        }