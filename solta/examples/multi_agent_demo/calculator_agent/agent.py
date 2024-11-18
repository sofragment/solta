"""
Calculator agent implementation
"""
from solta.core import Agent, setup_agent
from .tools import CalculatorTool

class CalculatorAgent(Agent):
    """
    Agent that handles mathematical calculations.
    
    This agent demonstrates:
    1. Tool usage
    2. Message handling
    3. State management
    """
    
    required_tools = ['calculator']
    
    def __init__(self):
        super().__init__(name="Calculator")
        self.register_tool(CalculatorTool())
        self.calculation_history = []
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is ready for calculations!")
    
    @setup_agent
    async def on_message(self, message):
        if "calculate" in message:
            calc = message["calculate"]
            try:
                result = await self.tools["calculator"].execute(**calc)
                
                # Store in history
                self.calculation_history.append({
                    "operation": calc,
                    "result": result["result"]
                })
                
                return {
                    "type": "calculation",
                    "result": result["result"],
                    "history_size": len(self.calculation_history)
                }
            except Exception as e:
                return {
                    "type": "calculation_error",
                    "error": str(e)
                }
        
        return None
    
    async def cleanup(self):
        """Cleanup agent resources."""
        self.calculation_history.clear()
        await super().cleanup()
