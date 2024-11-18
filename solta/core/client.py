"""
Client implementation for Solta framework
"""
from typing import Dict, Optional, Type, List, Any, Union
import asyncio
import inspect
from pathlib import Path

from .agent import Agent
from .router import RouterAgent
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
        client = Client(
            prefix="router",
            agent_dirs=["my_agents"],
            live_reload=True
        )
    """
    
    def __init__(
        self,
        prefix: str = "router",
        agent_dirs: Optional[List[str]] = None,
        live_reload: bool = False,
        **config
    ):
        self.prefix = prefix
        self.config = config
        self.agent_dirs = agent_dirs or []
        self.live_reload = live_reload
        self.agents: Dict[str, Agent] = {}
        self._ready = False
        self._router: Optional[RouterAgent] = None
        self._loop = None
        self._loader = AgentLoader(self)
        
    def agent(self, cls: Type[Agent]) -> Type[Agent]:
        """
        Decorator to register an agent class.
        
        Example:
            @client.agent
            class MyAgent(Agent):
                pass
        """
        if not inspect.isclass(cls) or not issubclass(cls, Agent):
            raise TypeError("Decorator must be applied to an Agent class")
        
        # Store the agent class for later instantiation
        self.agents[cls.__name__] = cls
        return cls
    
    async def _initialize_router(self) -> None:
        """Initialize the router agent."""
        self._router = RouterAgent(name=self.prefix)
        await self._router.initialize()
    
    async def load_agents(self) -> None:
        """Load all registered agents."""
        # Initialize agents from decorator registration
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
        Reload an agent instance.
        
        Args:
            agent_cls: Updated agent class to reload
        """
        if not self.live_reload:
            return
            
        name = agent_cls.__name__
        old_agent = self.agents.get(name)
        
        if old_agent:
            # Cleanup old agent
            await old_agent.cleanup()
            
            try:
                # Initialize new agent
                new_agent = agent_cls()
                await new_agent.initialize()
                
                # Update registrations
                self.agents[name] = new_agent
                self._router.register_route(name.lower(), new_agent)
                
                print(f"Successfully reloaded agent: {name}")
                
            except Exception as e:
                print(f"Failed to reload agent {name}: {e}")
                # Restore old agent if reload fails
                self.agents[name] = old_agent
    
    async def start(self) -> None:
        """Initialize and start the client."""
        if self._ready:
            return
        
        # Initialize router first
        await self._initialize_router()
        
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
        
        # Clean up router first
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
