"""
Example implementation of a basic Solta agent
"""
from typing import Dict, Any
from solta import Agent, setup_agent
from .tools import SearchTool

class BasicAgent(Agent):
    """
    A basic example agent that demonstrates core Solta functionality.
    
    This agent shows how to:
    1. Initialize with custom configuration
    2. Use the setup_agent decorator
    3. Handle messages
    4. Integrate tools
    """
    
    def __init__(self, name: str = "BasicAgent", model: str = "llama3:latest"):
        super().__init__(name=name, model=model)
        # Register default tools
        self.register_tool(SearchTool())
        
    @setup_agent
    async def on_ready(self) -> None:
        """Called when the agent is initialized and ready."""
        print(f"{self.name} is ready with model: {self.model}")
        
    @setup_agent
    async def on_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming messages."""
        # Example message handling logic
        if "query" in message:
            response = await self.handle_query(message["query"])
            print(f"Processed query: {response}")
            
    async def handle_query(self, query: str) -> str:
        """Process a query using the Ollama API."""
        # This is where you'd implement the actual Ollama API interaction
        return f"Processed query: {query}"
    
    async def cleanup(self) -> None:
        """Cleanup resources before shutdown."""
        await super().cleanup()
        print(f"{self.name} shutting down...")

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        agent = BasicAgent()
        await agent.initialize()
        
        # Example message
        await agent.on_message({
            "query": "What is the weather like today?"
        })
        
        await agent.cleanup()
    
    asyncio.run(main())
