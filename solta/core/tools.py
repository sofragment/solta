"""
Base Tool system for Solta framework
"""
from typing import Any, Callable, Dict, Optional
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Base class for all tools that can be used by Solta agents.
    
    Tools provide additional functionality to agents, such as:
    - API interactions
    - Data processing
    - External service integration
    - Custom command handling
    """
    
    def __init__(self, name: Optional[str] = None, description: str = ""):
        self.name = name or self.__class__.__name__
        self.description = description
        self._agent = None
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool's main functionality."""
        pass
    
    def bind_agent(self, agent: 'Agent') -> None:
        """Bind this tool to an agent."""
        self._agent = agent
        
    @property
    def agent(self) -> 'Agent':
        """Get the bound agent."""
        if self._agent is None:
            raise RuntimeError("Tool not bound to any agent")
        return self._agent
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters before execution."""
        return True
    
    async def cleanup(self) -> None:
        """Cleanup any resources used by the tool."""
        pass
