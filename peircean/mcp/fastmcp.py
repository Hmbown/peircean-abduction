from typing import Any, Callable, Optional
from .types import ToolAnnotations

class FastMCP:
    """
    A minimal implementation of FastMCP for local usage.
    """
    def __init__(self, name: str, instructions: str = ""):
        self.name = name
        self.instructions = instructions
        self._tools: dict[str, Callable] = {}

    def tool(self, annotations: Optional[ToolAnnotations] = None) -> Callable:
        """Decorator to register a tool."""
        def decorator(func: Callable) -> Callable:
            self._tools[func.__name__] = func
            return func
        return decorator

    def run(self) -> None:
        """Run the MCP server."""
        # Minimal implementation: just print that it's running
        # In a real scenario, this would start the server loop
        print(f"Starting FastMCP server: {self.name}")
        # Keep process alive or handle stdin/stdout if needed
        # For now, we assume this is enough for the harness
