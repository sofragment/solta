"""
Tools for the Memory agent
"""
from typing import Dict, Any, Optional, List
from solta.core.tools import BaseTool

class MemoryStoreTool(BaseTool):
    """
    Tool for managing persistent memory storage.
    
    This tool demonstrates:
    1. State persistence
    2. Data validation
    3. Error handling
    """
    
    def __init__(self):
        super().__init__(
            name="memory_store",
            description="Manages persistent memory storage"
        )
        self.storage: Dict[str, Any] = {}
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate memory operation parameters."""
        operation = params.get("operation")
        if not operation:
            raise ValueError("Operation is required")
            
        if operation not in ["store", "retrieve", "list"]:
            raise ValueError(f"Unknown operation: {operation}")
            
        if operation in ["store", "retrieve"]:
            if "key" not in params:
                raise ValueError("Key is required for store/retrieve operations")
                
        if operation == "store" and "value" not in params:
            raise ValueError("Value is required for store operation")
            
        return True
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute memory operations."""
        self.validate_params(kwargs)
        
        operation = kwargs["operation"]
        
        try:
            if operation == "store":
                key = kwargs["key"]
                value = kwargs["value"]
                self.storage[key] = value
                return {
                    "operation": "store",
                    "status": "success",
                    "key": key
                }
                
            elif operation == "retrieve":
                key = kwargs["key"]
                if key not in self.storage:
                    return {
                        "operation": "retrieve",
                        "status": "not_found",
                        "key": key,
                        "value": None
                    }
                return {
                    "operation": "retrieve",
                    "status": "success",
                    "key": key,
                    "value": self.storage[key]
                }
                
            elif operation == "list":
                return {
                    "operation": "list",
                    "status": "success",
                    "keys": list(self.storage.keys())
                }
                
        except Exception as e:
            raise RuntimeError(f"Memory operation error: {str(e)}")
    
    async def cleanup(self) -> None:
        """Clean up tool resources."""
        self.storage.clear()
        await super().cleanup()
    
    def get_storage_size(self) -> int:
        """Get the current size of the storage."""
        return len(self.storage)
    
    def has_key(self, key: str) -> bool:
        """Check if a key exists in storage."""
        return key in self.storage
