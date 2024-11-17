"""
Solta - A framework for building AI agents with Ollama
"""

from .core.agent import Agent
from .core.decorators import setup_agent
from .core.tools import BaseTool

__version__ = "0.0.1"
__all__ = ["Agent", "setup_agent", "BaseTool"]
