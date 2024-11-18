"""
Router agent implementation for Solta framework
"""
from typing import Dict, Any, Optional, List
from .agent import Agent
from .decorators import setup_agent

class RouterAgent(Agent):
    """
    Router agent that handles message routing between agents.
    
    This agent:
    1. Receives all incoming messages
    2. Determines appropriate agent(s) to handle each message
    3. Manages message priority and queuing
    4. Handles conversation context
    """
    
    def __init__(self, name: str = "Router", model: str = "llama2"):
        super().__init__(name=name, model=model)
        self.routes: Dict[str, List[Agent]] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
    @setup_agent
    async def on_ready(self) -> None:
        """Called when the router is initialized."""
        print(f"{self.name} is ready and managing agent communications")
        
    def register_route(self, pattern: str, agent: Agent) -> None:
        """Register an agent to handle specific message patterns."""
        if pattern not in self.routes:
            self.routes[pattern] = []
        self.routes[pattern].append(agent)
        
    async def route_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route a message to appropriate agent(s)."""
        # Store in conversation history
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Get all registered agents for broadcasting
        all_agents = set()
        for agents in self.routes.values():
            all_agents.update(agents)
        
        # Send to all agents and collect responses
        responses = []
        for agent in all_agents:
            try:
                response = await agent.on_message(message)
                if response:
                    responses.append(response)
            except Exception as e:
                print(f"Error in agent {agent.name}: {e}")
        
        if responses:
            return {
                "responses": responses,
                "source_count": len(responses)
            }
        return None
    
    @setup_agent
    async def on_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming messages."""
        return await self.route_message(message)
    
    async def cleanup(self) -> None:
        """Cleanup router resources."""
        self.conversation_history.clear()
        self.routes.clear()
        await super().cleanup()
