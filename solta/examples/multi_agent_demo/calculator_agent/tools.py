"""
Tools for the Calculator agent
"""
from typing import Dict, Any
from solta.core.tools import BaseTool

class CalculatorTool(BaseTool):
    """
    Tool for performing mathematical calculations.
    
    This tool demonstrates:
    1. Parameter validation
    2. Error handling
    3. Result formatting
    """
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic mathematical calculations"
        )
        self.operations = {
            'add': lambda a, b: a + b,
            'subtract': lambda a, b: a - b,
            'multiply': lambda a, b: a * b,
            'divide': lambda a, b: a / b if b != 0 else float('inf'),
            'power': lambda a, b: a ** b,
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate calculation parameters."""
        if "operation" not in params:
            raise ValueError("Operation is required")
            
        if params["operation"] not in self.operations:
            raise ValueError(f"Unknown operation: {params['operation']}")
            
        if "a" not in params or "b" not in params:
            raise ValueError("Both 'a' and 'b' parameters are required")
            
        if not all(isinstance(params[x], (int, float)) for x in ['a', 'b']):
            raise TypeError("Parameters 'a' and 'b' must be numbers")
            
        return True
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the calculation."""
        self.validate_params(kwargs)
        
        operation = kwargs["operation"]
        a = kwargs["a"]
        b = kwargs["b"]
        
        try:
            result = self.operations[operation](a, b)
            
            return {
                "operation": operation,
                "a": a,
                "b": b,
                "result": result
            }
            
        except ZeroDivisionError:
            raise ValueError("Division by zero")
        except Exception as e:
            raise RuntimeError(f"Calculation error: {str(e)}")
    
    async def cleanup(self) -> None:
        """Clean up tool resources."""
        # Nothing to clean up for this tool
        await super().cleanup()
