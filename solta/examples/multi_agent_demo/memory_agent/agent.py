"""
Memory agent implementation
"""
from typing import Dict, Any, Optional
from solta.core import Agent, setup_agent
from .tools import MemoryStoreTool

class MemoryAgent(Agent):
    """
    Agent that manages persistent memory and context.
    
    This agent demonstrates:
    1. State management
    2. Context tracking
    3. Inter-agent communication
    """
    
    required_tools = ['memory_store']
    
    def __init__(self):
        super().__init__(name="Memory")
        self.register_tool(MemoryStoreTool())
        self.conversation_history = []
        self.max_history = 100
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is ready to manage memory!")
    
    @setup_agent
    async def on_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Store all messages in conversation history
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
        
        # Handle memory operations
        if "memory" in message:
            mem_op = message["memory"]
            operation = mem_op.get("operation")
            
            if operation == "store":
                result = await self.tools["memory_store"].execute(
                    operation="store",
                    key=mem_op.get("key"),
                    value=mem_op.get("value")
                )
                return {
                    "type": "memory_store",
                    "status": "success",
                    "key": mem_op.get("key")
                }
                
            elif operation == "retrieve":
                result = await self.tools["memory_store"].execute(
                    operation="retrieve",
                    key=mem_op.get("key")
                )
                return {
                    "type": "memory_retrieve",
                    "key": mem_op.get("key"),
                    "value": result.get("value")
                }
                
            elif operation == "list":
                result = await self.tools["memory_store"].execute(
                    operation="list"
                )
                return {
                    "type": "memory_list",
                    "keys": result.get("keys", [])
                }
        
        # Provide context for other messages
        return {
            "type": "context",
            "history_size": len(self.conversation_history),
            "last_message": self.conversation_history[-1] if self.conversation_history else None
        }
    
    async def cleanup(self):
        """Cleanup agent resources."""
        self.conversation_history.clear()
        await super().cleanup()
