"""
Base Agent class for Solta framework
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class Agent(ABC):
    """
    Base class for all Solta agents.
    
    This class provides the foundation for creating AI agents that can interact
    with the Ollama API. It handles basic lifecycle management and provides
    hooks for customization.
    """
    
    def __init__(self, name: Optional[str] = None, model: str = "llama2"):
        self.name = name or self.__class__.__name__
        self.model = model
        self.tools = {}
        self.config = {}
        self._is_ready = False
        
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
    async def on_message(self, message: Dict[str, Any]) -> None:
        """Called when the agent receives a message."""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources before shutdown."""
        # Clean up all tools
        for tool in self.tools.values():
            await tool.cleanup()
        # Reset ready state
        self._is_ready = False
    
    def register_tool(self, tool: 'BaseTool') -> None:
        """Register a tool with the agent."""
        tool.bind_agent(self)
        self.tools[tool.name] = tool
    
    def configure(self, **kwargs) -> None:
        """Configure the agent with the provided settings."""
        self.config.update(kwargs)
