"""
Peircean MCP Module

A Logic Harness for abductive inference.
Model Context Protocol integration for the Peircean abduction server.
"""

from .server import mcp, main as serve, SYSTEM_DIRECTIVE
from .setup import setup_mcp, main as setup

__all__ = [
    "mcp",
    "serve",
    "setup_mcp",
    "setup",
    "SYSTEM_DIRECTIVE",
]
