"""
Client implementation for Solta framework
"""
from typing import Dict, Optional, Type, List, Any
import asyncio
import inspect
from pathlib import Path

from .agent import Agent
from .router import RouterAgent
from .decorators import setup_agent

class Client:
    """
    Main client class for Solta framework.
    
    This class handles:
    1. Agent management and lifecycle
    2. Message routing through RouterAgent
    3. Event handling
    4. Configuration management
    """
    
    def __init__(self, prefix: str = "router", **config):
        self.prefix = prefix
        self.config = config
        self.agents: Dict[str, Agent] = {}
        self._ready = False
        self._router: Optional[RouterAgent] = None
        self._loop = None
        
    def agent(self, cls: Type[Agent]) -> Type[Agent]:
        """Decorator to register an agent class."""
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
        # Initialize agents
        initialized_agents = {}
        for name, agent_cls in self.agents.items():
            try:
                agent = agent_cls()
                await agent.initialize()
                initialized_agents[name] = agent
                
                # Register with router for all message types
                # This ensures the agent receives all messages
                self._router.register_route(name.lower(), agent)
                
            except Exception as e:
                print(f"Failed to initialize agent {name}: {e}")
        
        self.agents = initialized_agents
    
    async def load_agents_from_directory(self, directory: str) -> None:
        """Load agents from a directory."""
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory not found: {directory}")
        
        # Look for agent.py files in subdirectories
        for agent_dir in path.iterdir():
            if agent_dir.is_dir():
                agent_file = agent_dir / "agent.py"
                if agent_file.exists():
                    # TODO: Implement dynamic loading of agent modules
                    pass
    
    async def start(self) -> None:
        """Initialize and start the client."""
        if self._ready:
            return
        
        # Initialize router first
        await self._initialize_router()
        
        # Load all agents
        await self.load_agents()
        
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
