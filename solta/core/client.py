"""
Client implementation for Solta framework
"""
from typing import Dict, Optional, Type, List, Any, Union
import asyncio
import inspect
from pathlib import Path
import importlib.util

from .agent import Agent
from .default_router import DefaultRouter  # Fixed import
from .loader import AgentLoader
from .decorators import setup_agent

class Client:
    """
    Main client class for Solta framework.
    
    This class handles:
    1. Agent management and lifecycle
    2. Message routing through RouterAgent
    3. Event handling
    4. Configuration management
    
    Example:
        # Using default router
        client = Client(
            router="default",
            agent_dirs=["my_agents"],
            live_reload=True
        )
        
        # Using custom router
        client = Client(
            router="path/to/custom_router.py",
            agent_dirs=["my_agents"]
        )
    """
    
    def __init__(
        self,
        router: str = "default",
        agent_dirs: Optional[List[str]] = None,
        live_reload: bool = False,
        **config
    ):
        self.config = config
        self.agent_dirs = agent_dirs or []
        self.live_reload = live_reload
        self.agents: Dict[str, Agent] = {}
        self._ready = False
        self._router: Optional[Agent] = None
        self._loop = None
        self._loader = AgentLoader(self)
        
        # Initialize router
        self._init_router(router)
        
    def _init_router(self, router: str) -> None:
        """
        Initialize the router based on configuration.
        
        Args:
            router: Either "default" or path to custom router implementation
        """
        if router == "default":
            self._router = DefaultRouter()
        else:
            # Load custom router from file
            try:
                router_path = Path(router)
                if not router_path.exists():
                    raise ValueError(f"Router file not found: {router}")
                
                # Import the router module
                spec = importlib.util.spec_from_file_location(
                    "custom_router",
                    router_path
                )
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load router from {router}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find router class
                router_class = None
                for item_name, item in inspect.getmembers(module):
                    if (inspect.isclass(item) and 
                        issubclass(item, Agent) and 
                        item != Agent):
                        router_class = item
                        break
                
                if router_class is None:
                    raise ValueError(f"No router class found in {router}")
                
                self._router = router_class()
                
            except Exception as e:
                raise RuntimeError(f"Error loading custom router: {str(e)}")
    
    def agent(self, cls: Type[Agent]) -> Type[Agent]:
        """Decorator to register an agent class."""
        if not inspect.isclass(cls) or not issubclass(cls, Agent):
            raise TypeError("Decorator must be applied to an Agent class")
        
        # Store the agent class for later instantiation
        self.agents[cls.__name__] = cls
        return cls
    
    async def load_agents(self) -> None:
        """Load all registered agents."""
        # Initialize agents
        initialized_agents = {}
        for name, agent_cls in self.agents.items():
            try:
                agent = agent_cls()
                await agent.initialize()
                initialized_agents[name] = agent
                
                # Register with router
                self._router.register_route(name.lower(), agent)
                
            except Exception as e:
                print(f"Failed to initialize agent {name}: {e}")
        
        self.agents = initialized_agents
    
    async def discover_and_load_agents(self) -> None:
        """Discover and load agents from configured directories."""
        for directory in self.agent_dirs:
            try:
                # Discover agent files
                agent_files = self._loader.discover_agents(directory)
                
                # Load each discovered agent
                for file_path in agent_files:
                    agent_classes = self._loader.load_agent_file(file_path)
                    
                    # Initialize and register each agent
                    for agent_cls in agent_classes:
                        try:
                            # Check dependencies
                            required_tools = self._loader.resolve_dependencies(agent_cls)
                            
                            # Initialize agent
                            agent = agent_cls()
                            await agent.initialize()
                            
                            # Register with client and router
                            self.agents[agent_cls.__name__] = agent
                            self._router.register_route(agent_cls.__name__.lower(), agent)
                            
                        except Exception as e:
                            print(f"Failed to initialize agent {agent_cls.__name__}: {e}")
                
            except Exception as e:
                print(f"Error loading agents from directory {directory}: {e}")
    
    async def reload_agent(self, agent_cls: Type[Agent]) -> None:
        """
        Reload an agent with an updated class.
        
        Args:
            agent_cls: Updated agent class
        """
        if not self.live_reload:
            return
            
        try:
            # Clean up old agent if it exists
            old_agent = self.agents.get(agent_cls.__name__)
            if old_agent:
                await old_agent.cleanup()
            
            # Initialize new agent
            new_agent = agent_cls()
            await new_agent.initialize()
            
            # Update client and router
            self.agents[agent_cls.__name__] = new_agent
            self._router.register_route(agent_cls.__name__.lower(), new_agent)
            
            print(f"Reloaded agent: {agent_cls.__name__}")
            
        except Exception as e:
            print(f"Failed to reload agent {agent_cls.__name__}: {e}")
    
    async def start(self) -> None:
        """Initialize and start the client."""
        if self._ready:
            return
        
        # Initialize router
        await self._router.initialize()
        
        # Load decorator-registered agents
        await self.load_agents()
        
        # Discover and load agents from directories
        if self.agent_dirs:
            await self.discover_and_load_agents()
            
            # Start watching for changes if live reload is enabled
            if self.live_reload:
                self._loader.start_watching(self.agent_dirs)
        
        self._ready = True
        print(f"Client ready with {len(self.agents)} agents")
    
    def run(self) -> None:
        """Run the client (blocking)."""
        try:
            self._loop = asyncio.get_event_loop()
            self._loop.run_until_complete(self.start())
            self._loop.run_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
    
    async def _cleanup_async(self) -> None:
        """Async cleanup implementation."""
        # Stop file watching if enabled
        self._loader.stop_watching()
        
        # Clean up router
        if self._router is not None:
            await self._router.cleanup()
            self._router = None
        
        # Clean up agents
        for agent in list(self.agents.values()):
            await agent.cleanup()
        
        # Clear agent references
        self.agents.clear()
        
        self._ready = False
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if self._loop is not None and self._loop.is_running():
            # Create a new event loop for cleanup if the current one is running
            cleanup_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cleanup_loop)
            try:
                cleanup_loop.run_until_complete(self._cleanup_async())
            finally:
                cleanup_loop.close()
        elif self._loop is not None:
            # Use existing loop if it's not running
            self._loop.run_until_complete(self._cleanup_async())
        
        # Reset loop
        if self._loop is not None:
            try:
                self._loop.close()
            except:
                pass
            self._loop = None
    
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message through the router."""
        if not self._ready:
            raise RuntimeError("Client not ready. Call run() first.")
        
        if self._router is None:
            raise RuntimeError("Router not initialized")
        
        return await self._router.route_message(message)
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to be processed (non-blocking)."""
        if self._loop is None:
            raise RuntimeError("Client not running")
            
        asyncio.run_coroutine_threadsafe(
            self.process_message(message),
            self._loop
        )
