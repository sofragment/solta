"""
Example demonstrating the Solta client system with multiple agents
"""
from solta.core import Client, Agent, setup_agent
from solta.core.tools import BaseTool

# Create the client
client = Client(prefix="router")

# Define a custom tool
class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs basic calculations"
        )
    
    async def execute(self, **kwargs):
        operation = kwargs.get("operation")
        a = kwargs.get("a", 0)
        b = kwargs.get("b", 0)
        
        if operation == "add":
            return {"result": a + b}
        elif operation == "multiply":
            return {"result": a * b}
        else:
            raise ValueError(f"Unknown operation: {operation}")

# Define agents using the client decorator
@client.agent
class MathAgent(Agent):
    def __init__(self):
        super().__init__(name="MathAgent")
        self.register_tool(CalculatorTool())
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is ready for calculations!")
    
    @setup_agent
    async def on_message(self, message):
        if "calculate" in message:
            calc = message["calculate"]
            if calc["operation"] == "add":
                result = await self.tools["calculator"].execute(
                    operation="add",
                    a=calc["a"],
                    b=calc["b"]
                )
                return {
                    "type": "calculation",
                    "result": result["result"]
                }
        return None

@client.agent
class MemoryAgent(Agent):
    def __init__(self):
        super().__init__(name="MemoryAgent")
        self.memories = {}
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is ready to store memories!")
    
    @setup_agent
    async def on_message(self, message):
        if "store" in message:
            key = message["store"]["key"]
            value = message["store"]["value"]
            self.memories[key] = value
            return {
                "type": "memory",
                "status": "stored",
                "key": key
            }
        elif "recall" in message:
            key = message["recall"]["key"]
            value = self.memories.get(key)
            return {
                "type": "memory",
                "status": "recalled",
                "key": key,
                "value": value
            }
        return None

# Example usage
if __name__ == "__main__":
    # Run the client
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    # Example messages (these would normally be sent while the client is running):
    """
    # Calculate something
    message1 = {
        "calculate": {
            "operation": "add",
            "a": 5,
            "b": 3
        }
    }
    
    # Store a memory
    message2 = {
        "store": {
            "key": "favorite_number",
            "value": 42
        }
    }
    
    # Recall a memory
    message3 = {
        "recall": {
            "key": "favorite_number"
        }
    }
    """
