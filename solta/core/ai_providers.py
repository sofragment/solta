"""
AI provider integrations for Solta framework
"""
from typing import Dict, Any, Optional, List, Union
import json
import aiohttp
from abc import ABC, abstractmethod

class AIProvider(ABC):
    """
    Base class for AI providers.
    
    This class defines the interface for AI providers and ensures
    compatibility with different services like Ollama, OpenAI, etc.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        model: str,
        **kwargs
    ):
        """Stream a response from the AI model."""
        pass

class OllamaProvider(AIProvider):
    """
    Ollama API integration with OpenAI-compatible interface.
    
    This provider allows using Ollama models with an interface
    similar to OpenAI's, making it easy to switch between providers.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    async def _post(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a POST request to the Ollama API."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{endpoint}",
                json=data
            ) as response:
                return await response.json()
    
    async def generate(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: The input prompt
            model: Model name (e.g., "llama2")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters
            
        Returns:
            OpenAI-compatible response format
        """
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "options": kwargs
        }
        
        if max_tokens:
            data["options"]["num_predict"] = max_tokens
            
        response = await self._post("api/generate", data)
        
        # Convert to OpenAI-compatible format
        return {
            "id": "ollama",
            "object": "text_completion",
            "created": None,  # Ollama doesn't provide timestamp
            "model": model,
            "choices": [{
                "text": response.get("response", ""),
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0),
                "total_tokens": (
                    response.get("prompt_eval_count", 0) +
                    response.get("eval_count", 0)
                )
            }
        }
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Stream a response from Ollama.
        
        Args:
            prompt: The input prompt
            model: Model name (e.g., "llama2")
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters
            
        Yields:
            OpenAI-compatible streaming response format
        """
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": True,
            "options": kwargs
        }
        
        if max_tokens:
            data["options"]["num_predict"] = max_tokens
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=data
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            yield {
                                "id": "ollama",
                                "object": "text_completion",
                                "created": None,
                                "model": model,
                                "choices": [{
                                    "text": chunk.get("response", ""),
                                    "index": 0,
                                    "logprobs": None,
                                    "finish_reason": None
                                }]
                            }
                        except json.JSONDecodeError:
                            continue

class AIProviderFactory:
    """
    Factory for creating AI provider instances.
    
    This factory makes it easy to switch between different AI providers
    while maintaining a consistent interface.
    """
    
    @staticmethod
    def create(
        provider: str = "ollama",
        **kwargs
    ) -> AIProvider:
        """
        Create an AI provider instance.
        
        Args:
            provider: Provider name ("ollama", "openai", etc.)
            **kwargs: Provider-specific configuration
            
        Returns:
            AIProvider instance
        """
        if provider == "ollama":
            return OllamaProvider(**kwargs)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")

# Default provider instance
default_provider = AIProviderFactory.create("ollama")
