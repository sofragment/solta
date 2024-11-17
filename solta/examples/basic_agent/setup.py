"""
Setup configuration for the basic example agent
"""
from typing import Dict, Any
from .agent import BasicAgent
from .tools import SearchTool, MemoryTool

def create_agent(config: Dict[str, Any] = None) -> BasicAgent:
    """
    Create and configure a BasicAgent instance.
    
    Args:
        config: Optional configuration dictionary with settings
               for the agent and its tools.
    
    Returns:
        Configured BasicAgent instance
    
    Example:
        agent = create_agent({
            "name": "MyAgent",
            "model": "llama2",
            "temperature": 0.7,
            "max_tokens": 100
        })
    """
    # Default configuration
    default_config = {
        "name": "BasicAgent",
        "model": "llama2",
        "temperature": 0.8,
        "max_tokens": 150,
        "tools": ["search", "memory"]
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    
    # Create agent instance
    agent = BasicAgent(
        name=default_config["name"],
        model=default_config["model"]
    )
    
    # Configure agent settings
    agent.configure(
        temperature=default_config["temperature"],
        max_tokens=default_config["max_tokens"]
    )
    
    # Register tools based on configuration
    if "search" in default_config["tools"]:
        agent.register_tool(SearchTool())
    if "memory" in default_config["tools"]:
        agent.register_tool(MemoryTool())
    
    return agent

async def initialize_agent(config: Dict[str, Any] = None) -> BasicAgent:
    """
    Create and initialize a BasicAgent instance.
    
    This is a convenience function that creates the agent
    and calls its initialize method.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Initialized BasicAgent instance
    """
    agent = create_agent(config)
    await agent.initialize()
    return agent

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Create and initialize agent with custom config
        agent = await initialize_agent({
            "name": "CustomAgent",
            "model": "llama3:latest",
            "temperature": 0.7,
            "tools": ["search", "memory"]
        })
        
        # Example usage
        await agent.on_message({
            "query": "Tell me about Python programming"
        })
        
        # Cleanup
        await agent.cleanup()
    
    asyncio.run(main())
