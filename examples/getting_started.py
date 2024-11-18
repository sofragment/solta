"""
Getting started example for Solta framework
"""
from solta.core import Client, Agent, setup_agent
from typing import Dict, Any

# Create the client
client = Client(prefix="router")

@client.agent
class AssistantAgent(Agent):
    """
    A simple assistant agent that will use Ollama for responses.
    """
    def __init__(self):
        super().__init__(name="Assistant", model="llama2")
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is ready to help!")
    
    @setup_agent
    async def on_message(self, message: Dict[str, Any]):
        if "prompt" in message:
            # TODO: This is where we'll integrate with Ollama
            # For now, return a mock response
            return {
                "type": "response",
                "content": f"I received your prompt: {message['prompt']}",
                "model": self.model
            }
        return None

@client.agent
class ContextAgent(Agent):
    """
    An agent that maintains conversation context.
    """
    def __init__(self):
        super().__init__(name="Context")
        self.conversation_history = []
    
    @setup_agent
    async def on_ready(self):
        print(f"{self.name} is tracking context!")
    
    @setup_agent
    async def on_message(self, message: Dict[str, Any]):
        # Store message in history
        self.conversation_history.append(message)
        
        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
        
        return {
            "type": "context",
            "history_length": len(self.conversation_history),
            "last_message": message
        }

def main():
    """
    Example usage of the Solta framework.
    
    To use this example:
    1. Install solta: pip install solta
    2. Run this script: python getting_started.py
    3. The client will start and agents will be initialized
    
    Future integration with Ollama will allow:
    - Direct message processing through Ollama API
    - Model switching and configuration
    - Context-aware responses
    - Tool usage through agents
    """
    try:
        # Start the client
        print("Starting Solta client...")
        client.run()
        
        # Example messages that could be sent:
        """
        # Simple prompt
        message1 = {
            "prompt": "What is artificial intelligence?"
        }
        
        # Prompt with context
        message2 = {
            "prompt": "Can you elaborate on that?",
            "context": True
        }
        
        # Tool usage example
        message3 = {
            "tool": "search",
            "query": "latest AI developments"
        }
        """
        
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
