"""
Decorators for Solta framework
"""
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

def setup_agent(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to mark agent setup methods and commands.
    
    This decorator can be used to:
    1. Mark initialization methods
    2. Define command handlers
    3. Set up event listeners
    
    Example:
        @setup_agent
        async def on_ready(self):
            print("Agent is ready!")
            
        @setup_agent
        async def handle_query(self, query: str):
            return await self.process_query(query)
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # In the future, we'll add proper error handling and logging here
            raise e
    
    # Add metadata to the function for the agent to use
    setattr(wrapper, '_is_agent_method', True)
    setattr(wrapper, '_original_func', func)
    
    return wrapper

def requires_tool(tool_name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to specify that a method requires a specific tool.
    
    Example:
        @requires_tool('search')
        async def search_query(self, query: str):
            return await self.tools['search'].execute(query=query)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            if tool_name not in self.tools:
                raise RuntimeError(f"Required tool '{tool_name}' not found")
            return await func(self, *args, **kwargs)
        
        setattr(wrapper, '_required_tool', tool_name)
        return wrapper
    
    return decorator

def with_context(**context: Any) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to add context to a method.
    
    Example:
        @with_context(temperature=0.7, max_tokens=100)
        async def generate_response(self, prompt: str):
            return await self.generate(prompt)
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(self: Any, *args: P.args, **kwargs: P.kwargs) -> T:
            # Merge context with any existing context
            original_context = getattr(self, 'context', {}).copy()
            self.context = {**original_context, **context}
            try:
                return await func(self, *args, **kwargs)
            finally:
                # Restore original context
                self.context = original_context
        
        return wrapper
    
    return decorator
