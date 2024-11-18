"""
Multi-agent demo showcasing Solta framework features
"""
import asyncio
import time
from solta.core import Client

def main():
    """
    Demonstrates:
    1. Agent discovery and loading
    2. Hot reloading
    3. Inter-agent communication
    4. Tool usage
    """
    
    # Create client with agent discovery and hot reloading
    client = Client(
        prefix="demo_router",
        agent_dirs=[
            "solta/examples/multi_agent_demo/calculator_agent",
            "solta/examples/multi_agent_demo/memory_agent"
        ],
        live_reload=True
    )
    
    try:
        print("Starting Solta multi-agent demo...")
        print("Press Ctrl+C to exit")
        
        # Example messages to demonstrate functionality:
        """
        # Calculator operations
        calc_message = {
            "calculate": {
                "operation": "add",
                "a": 5,
                "b": 3
            }
        }
        
        # Memory operations
        store_message = {
            "memory": {
                "operation": "store",
                "key": "last_calculation",
                "value": 8
            }
        }
        
        retrieve_message = {
            "memory": {
                "operation": "retrieve",
                "key": "last_calculation"
            }
        }
        
        # List stored memories
        list_message = {
            "memory": {
                "operation": "list"
            }
        }
        """
        
        # Run the client
        client.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        client.cleanup()

def test_hot_reload():
    """
    Test hot reloading functionality.
    
    This function demonstrates how agents can be modified
    while the client is running.
    """
    client = Client(
        prefix="test_router",
        agent_dirs=[
            "solta/examples/multi_agent_demo/calculator_agent",
            "solta/examples/multi_agent_demo/memory_agent"
        ],
        live_reload=True
    )
    
    async def run_test():
        # Start client
        await client.start()
        
        # Test calculator
        calc_result = await client.process_message({
            "calculate": {
                "operation": "add",
                "a": 5,
                "b": 3
            }
        })
        print("Calculator result:", calc_result)
        
        # Test memory
        await client.process_message({
            "memory": {
                "operation": "store",
                "key": "test",
                "value": "hello"
            }
        })
        
        memory_result = await client.process_message({
            "memory": {
                "operation": "retrieve",
                "key": "test"
            }
        })
        print("Memory result:", memory_result)
        
        # Wait for potential file changes
        await asyncio.sleep(5)
        
        await client._cleanup_async()
    
    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        print("\nTest interrupted...")

if __name__ == "__main__":
    main()
    
    # Uncomment to test hot reloading:
    # test_hot_reload()
