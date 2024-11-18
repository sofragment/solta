"""
Base Agent class for Solta framework
"""
from typing import Optional, Dict, Any, Union, AsyncGenerator
from abc import ABC, abstractmethod
from .ai_providers import AIProvider, default_provider

class Agent(ABC):
    """
    Base class for all Solta agents.
    
    This class provides the foundation for creating AI agents that can interact
    with various AI providers (Ollama, OpenAI, etc.). It handles basic lifecycle
    management and provides hooks for customization.
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        model: str = "llama2",
        ai_provider: Optional[AIProvider] = None,
        **kwargs
    ):
        self.name = name or self.__class__.__name__
        self.model = model
        self.tools = {}
        self.config = kwargs
        self._is_ready = False
        self.ai_provider = ai_provider or default_provider
        
    async def initialize(self) -> None:
        """Initialize the agent and its resources."""
        if not self._is_ready:
            await self.on_ready()
            self._is_ready = True
            
    @abstractmethod
    async def on_ready(self) -> None:
        """Called when the agent is fully initialized."""
        pass
    
    @abstractmethod
    async def on_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Called when the agent receives a message.
        
        Args:
            message: The message to process
            
        Returns:
            Optional response dictionary
        """
        pass
    
    async def generate(
        self,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Generate a response using the configured AI provider.
        
        Args:
            prompt: Input prompt
            stream: Whether to stream the response
            **kwargs: Additional parameters for the AI provider
            
        Returns:
            AI provider response or async generator for streaming
        """
        # Merge instance config with call-specific kwargs
        params = {**self.config, **kwargs}
        params["model"] = kwargs.get("model", self.model)
        
        if stream:
            return self.ai_provider.stream_generate(prompt, **params)
        else:
            return await self.ai_provider.generate(prompt, **params)
    
    async def cleanup(self) -> None:
        """Cleanup resources before shutdown."""
        # Clean up all tools
        for tool in list(self.tools.values()):
            await tool.cleanup()
        
        # Clear tool references
        self.tools.clear()
        
        # Clear any instance-specific data
        self.config.clear()
        
        # Reset ready state
        self._is_ready = False
    
    def register_tool(self, tool: 'BaseTool') -> None:
        """Register a tool with the agent."""
        tool.bind_agent(self)
        self.tools[tool.name] = tool
    
    def configure(self, **kwargs) -> None:
        """Configure the agent with the provided settings."""
        self.config.update(kwargs)
    
    @property
    def is_ready(self) -> bool:
        """Check if the agent is initialized and ready."""
        return self._is_ready
