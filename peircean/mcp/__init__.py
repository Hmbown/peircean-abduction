"""
Peircean MCP Module

A Logic Harness for abductive inference.
Model Context Protocol integration for the Peircean abduction server.
"""

from .server import SYSTEM_DIRECTIVE, mcp
from .server import main as serve
from .setup import main as setup
from .setup import setup_mcp

__all__ = [
    "mcp",
    "serve",
    "setup_mcp",
    "setup",
    "SYSTEM_DIRECTIVE",
]
