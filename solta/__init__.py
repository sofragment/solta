"""
Solta - A framework for building AI agents with Ollama
"""
from .core import (
    # Base classes
    Agent,
    BaseTool,
    
    # Decorators
    setup_agent,
    requires_tool,
    with_context,
    
    # Client and Router
    Client,
    DefaultRouter,
    
    # AI Providers
    AIProvider,
    OllamaProvider,
    AIProviderFactory,
    default_provider,
)

__version__ = "0.0.4"

__all__ = [
    # Base classes
    'Agent',
    'BaseTool',
    
    # Decorators
    'setup_agent',
    'requires_tool',
    'with_context',
    
    # Client and Router
    'Client',
    'DefaultRouter',
    
    # AI Providers
    'AIProvider',
    'OllamaProvider',
    'AIProviderFactory',
    'default_provider',
    
    # Version
    '__version__',
]
