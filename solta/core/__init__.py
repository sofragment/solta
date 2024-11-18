"""
Core module initialization for Solta framework
"""
from .agent import Agent
from .tools import BaseTool
from .decorators import setup_agent, requires_tool, with_context
from .client import Client
from .router import RouterAgent

__all__ = [
    'Agent',
    'BaseTool',
    'setup_agent',
    'requires_tool',
    'with_context',
    'Client',
    'RouterAgent'
]
