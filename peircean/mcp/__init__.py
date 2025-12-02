"""
Peircean MCP Module

A Logic Harness for abductive inference.
Model Context Protocol integration for the Peircean abduction server.
"""

from .errors import (
    ErrorCode,
    format_error_response,
    format_json_parse_error,
    format_validation_error,
)
from .inputs import (
    AbduceSingleShotInput,
    CriticEvaluateInput,
    Domain,
    EvaluateViaIBEInput,
    GenerateHypothesesInput,
    ObserveAnomalyInput,
    ResponseFormat,
)
from .server import CHARACTER_LIMIT, SYSTEM_DIRECTIVE, mcp
from .server import main as serve
from .setup import main as setup
from .setup import setup_mcp

__all__ = [
    # Server
    "mcp",
    "serve",
    "setup_mcp",
    "setup",
    "SYSTEM_DIRECTIVE",
    "CHARACTER_LIMIT",
    # Input models
    "Domain",
    "ResponseFormat",
    "ObserveAnomalyInput",
    "GenerateHypothesesInput",
    "EvaluateViaIBEInput",
    "AbduceSingleShotInput",
    "CriticEvaluateInput",
    # Error handling
    "ErrorCode",
    "format_error_response",
    "format_validation_error",
    "format_json_parse_error",
]
