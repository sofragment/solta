"""
Agent loading and discovery system for Solta framework
"""
import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .agent import Agent

class AgentLoadError(Exception):
    """Raised when an agent cannot be loaded."""
    pass

class AgentReloadError(Exception):
    """Raised when an agent cannot be reloaded."""
    pass

class AgentWatcher(FileSystemEventHandler):
    """Watches for changes in agent files and triggers reloads."""
    
    def __init__(self, loader: 'AgentLoader'):
        self.loader = loader
        self.processing = False
    
    def on_modified(self, event):
        if event.is_directory or self.processing:
            return
            
        if event.src_path.endswith(('.py')):
            self.processing = True
            try:
                self.loader.reload_agent_file(event.src_path)
            finally:
                self.processing = False

class AgentLoader:
    """
    Handles agent discovery, loading, and hot reloading.
    
    This class:
    1. Scans directories for agent files
    2. Loads agents and their dependencies
    3. Manages hot reloading
    4. Tracks agent dependencies
    """
    
    def __init__(self, client):
        self.client = client
        self.loaded_agents: Dict[str, Type[Agent]] = {}
        self.agent_paths: Dict[str, str] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.observer: Optional[Observer] = None
    
    def start_watching(self, directories: List[str]) -> None:
        """Start watching directories for changes."""
        if not self.client.live_reload:
            return
            
        self.observer = Observer()
        handler = AgentWatcher(self)
        
        for directory in directories:
            self.observer.schedule(handler, directory, recursive=True)
        
        self.observer.start()
    
    def stop_watching(self) -> None:
        """Stop watching for changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
    
    def discover_agents(self, directory: str) -> List[str]:
        """
        Discover agent files in a directory.
        
        Args:
            directory: Directory to scan for agents
            
        Returns:
            List of discovered agent file paths
        """
        agent_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise AgentLoadError(f"Directory not found: {directory}")
        
        for item in directory_path.rglob("*"):
            if item.is_file():
                if item.name == "agent.py":
                    agent_files.append(str(item))
                elif item.name == "setup.py":
                    agent_files.append(str(item))
        
        return agent_files
    
    def load_agent_file(self, file_path: str) -> List[Type[Agent]]:
        """
        Load agents from a file.
        
        Args:
            file_path: Path to the agent file
            
        Returns:
            List of loaded agent classes
        """
        try:
            # Import the module
            module_name = f"solta_agent_{Path(file_path).stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise AgentLoadError(f"Could not load spec for {file_path}")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find agent classes
            agents = []
            for item_name, item in inspect.getmembers(module):
                if (inspect.isclass(item) and 
                    issubclass(item, Agent) and 
                    item != Agent):
                    agents.append(item)
                    self.loaded_agents[item_name] = item
                    self.agent_paths[item_name] = file_path
            
            return agents
            
        except Exception as e:
            raise AgentLoadError(f"Error loading {file_path}: {str(e)}")
    
    def reload_agent_file(self, file_path: str) -> None:
        """
        Reload agents from a modified file.
        
        Args:
            file_path: Path to the modified agent file
        """
        if not self.client.live_reload:
            return
            
        try:
            # Find agents that need to be reloaded
            agents_to_reload = [
                name for name, path in self.agent_paths.items()
                if path == file_path
            ]
            
            # Load the updated agents
            updated_agents = self.load_agent_file(file_path)
            
            # Update the client's agents
            for agent_cls in updated_agents:
                self.client.reload_agent(agent_cls)
                
        except Exception as e:
            raise AgentReloadError(f"Error reloading {file_path}: {str(e)}")
    
    def resolve_dependencies(self, agent_cls: Type[Agent]) -> List[str]:
        """
        Resolve dependencies for an agent.
        
        Args:
            agent_cls: Agent class to resolve dependencies for
            
        Returns:
            List of required tool names
        """
        # For now, we'll just look for required tools in the class
        required_tools = getattr(agent_cls, 'required_tools', [])
        return required_tools
