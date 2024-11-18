"""
Core module initialization for Solta framework
"""
from .agent import Agent
from .tools import BaseTool
from .decorators import setup_agent, requires_tool, with_context
from .client import Client
from .default_router import DefaultRouter  # Updated import
from .ai_providers import (
    AIProvider,
    OllamaProvider,
    AIProviderFactory,
    default_provider
)

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
]
