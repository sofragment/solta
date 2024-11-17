"""
Example tools for the basic Solta agent
"""
from typing import Any, Dict
from solta.core.tools import BaseTool

class SearchTool(BaseTool):
    """
    Example tool that simulates a search functionality.
    
    This demonstrates:
    1. How to create custom tools
    2. Parameter validation
    3. Tool execution logic
    4. Error handling
    """
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Performs searches based on user queries"
        )
        self.search_history = []
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate search parameters."""
        if "query" not in params:
            raise ValueError("Search query is required")
        if not isinstance(params["query"], str):
            raise TypeError("Query must be a string")
        return True
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the search operation."""
        self.validate_params(kwargs)
        query = kwargs["query"]
        
        # Store in history
        self.search_history.append(query)
        
        # This is where you'd implement actual search logic
        # For now, we'll return a mock result
        return {
            "query": query,
            "results": [
                f"Mock result 1 for {query}",
                f"Mock result 2 for {query}",
                f"Mock result 3 for {query}"
            ],
            "metadata": {
                "timestamp": "2024-01-01T00:00:00Z",
                "source": "mock_search"
            }
        }
    
    async def cleanup(self) -> None:
        """Clean up search history."""
        self.search_history.clear()
        await super().cleanup()

class MemoryTool(BaseTool):
    """
    Example tool that provides memory capabilities to the agent.
    
    This demonstrates:
    1. State management in tools
    2. Complex tool functionality
    3. Integration with agent context
    """
    
    def __init__(self):
        super().__init__(
            name="memory",
            description="Manages agent memory and context"
        )
        self.memories = {}
        
    async def execute(self, **kwargs) -> Any:
        """Execute memory operations."""
        operation = kwargs.get("operation", "get")
        key = kwargs.get("key")
        value = kwargs.get("value")
        
        if operation == "store":
            if key is None or value is None:
                raise ValueError("Both key and value required for store operation")
            self.memories[key] = value
            return {"status": "stored", "key": key}
            
        elif operation == "get":
            if key is None:
                raise ValueError("Key required for get operation")
            return {
                "status": "retrieved",
                "key": key,
                "value": self.memories.get(key)
            }
            
        elif operation == "list":
            return {
                "status": "listed",
                "memories": list(self.memories.keys())
            }
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def cleanup(self):
        self.memories.clear()
