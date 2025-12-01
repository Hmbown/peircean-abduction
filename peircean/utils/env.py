"""
Peircean Abduction: Environment Loading Utilities

Robust environment variable handling with .env file support,
provider-specific configuration detection, and fallback logic.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def find_env_file(start_path: Path | None = None) -> Path | None:
    """
    Find .env file by searching up from the given path.

    Args:
        start_path: Path to start searching from (defaults to current working directory)

    Returns:
        Path to .env file if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search up the directory tree
    while True:
        env_file = current / ".env"
        if env_file.exists() and env_file.is_file():
            return env_file

        # Check for project-specific env files
        for variant in [".env.local", ".env.development", ".env.production"]:
            variant_file = current / variant
            if variant_file.exists() and variant_file.is_file():
                return variant_file

        # Move up to parent directory
        parent = current.parent
        if parent == current:  # Reached root directory
            break
        current = parent

    return None


def load_env_file(env_file_path: Path | None = None) -> bool:
    """
    Load environment variables from .env file.

    Args:
        env_file_path: Path to .env file (if None, will search for one)

    Returns:
        True if .env file was loaded successfully, False otherwise
    """
    if not DOTENV_AVAILABLE:
        # python-dotenv not available, skip .env loading
        return False

    if env_file_path is None:
        env_file_path = find_env_file()

    if env_file_path is None or not env_file_path.exists():
        return False

    try:
        # Load the .env file
        result = load_dotenv(env_file_path, override=False)
        return result
    except Exception:
        # Failed to load .env file, continue without it
        return False


def get_env_var(
    key: str, default: Any | None = None, cast_type: type | None = None, required: bool = False
) -> Any:
    """
    Get environment variable with optional type casting and validation.

    Args:
        key: Environment variable name
        default: Default value if not found
        cast_type: Type to cast the value to (str, int, float, bool)
        required: If True, raise ValueError if not found

    Returns:
        Environment variable value (cast to specified type if provided)

    Raises:
        ValueError: If required=True and variable not found
    """
    value = os.getenv(key)

    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' not found")
        return default

    if cast_type is not None:
        try:
            if cast_type is bool:
                # Handle boolean conversion
                if value.lower() in ("true", "1", "yes", "on"):
                    return True
                elif value.lower() in ("false", "0", "no", "off"):
                    return False
                else:
                    return bool(value)
            elif cast_type is int:
                return int(value)
            elif cast_type is float:
                return float(value)
            else:
                return cast_type(value)
        except (ValueError, TypeError) as e:
            if required:
                raise ValueError(
                    f"Environment variable '{key}' must be convertible to {cast_type.__name__}: {e}"
                ) from e
            return default

    return value


def get_provider_specific_config(provider: str) -> dict[str, Any]:
    """
    Get provider-specific configuration from environment variables.

    Args:
        provider: Provider name (anthropic, openai, gemini, ollama)

    Returns:
        Dictionary of provider-specific configuration
    """
    provider_upper = provider.upper()

    config = {}

    # API key
    api_key_var = f"{provider_upper}_API_KEY"
    config["api_key"] = get_env_var(api_key_var)

    # Base URL
    base_url_var = f"{provider_upper}_BASE_URL"
    config["base_url"] = get_env_var(base_url_var)

    # Provider-specific settings
    if provider == "anthropic":
        config["max_tokens"] = get_env_var("ANTHROPIC_MAX_TOKENS", cast_type=int)
        config["timeout"] = get_env_var("ANTHROPIC_TIMEOUT", cast_type=int, default=60)
    elif provider == "openai":
        config["organization"] = get_env_var("OPENAI_ORGANIZATION")
        config["max_tokens"] = get_env_var("OPENAI_MAX_TOKENS", cast_type=int)
        config["timeout"] = get_env_var("OPENAI_TIMEOUT", cast_type=int, default=60)
    elif provider == "gemini":
        config["max_tokens"] = get_env_var("GEMINI_MAX_TOKENS", cast_type=int)
        config["timeout"] = get_env_var("GEMINI_TIMEOUT", cast_type=int, default=60)
    elif provider == "ollama":
        # Ollama-specific configuration
        config["host"] = get_env_var("OLLAMA_HOST", default="localhost:11434")
        config["base_url"] = get_env_var("OLLAMA_HOST", default="http://localhost:11434")
        config["timeout"] = get_env_var("OLLAMA_TIMEOUT", cast_type=int, default=120)
        config["num_predict"] = get_env_var("OLLAMA_NUM_PREDICT", cast_type=int)

    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def validate_environment() -> dict[str, Any]:
    """
    Validate the current environment configuration.

    Returns:
        Dictionary with validation results
    """
    results: dict[str, Any] = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "loaded_env_file": None,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment_variables": {},
    }

    # Check if .env file was loaded
    env_file = find_env_file()
    if env_file:
        results["loaded_env_file"] = str(env_file)

    # Check python-dotenv availability
    if not DOTENV_AVAILABLE:
        results["warnings"].append("python-dotenv not available - .env file support disabled")

    # Check for common environment variables
    common_vars = [
        "PEIRCEAN_PROVIDER",
        "PEIRCEAN_MODEL",
        "PEIRCEAN_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ]

    for var in common_vars:
        value = os.getenv(var)
        if value:
            # Mask API keys in output
            if "API_KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            results["environment_variables"][var] = display_value

    # Check for at least one API key
    api_keys = [v for v in common_vars if "API_KEY" in v and os.getenv(v)]
    if not api_keys:
        results["issues"].append("No API keys found in environment variables")
        results["valid"] = False

    return results


def create_example_env_file() -> str:
    """
    Create example .env file content.

    Returns:
        String with example .env file content
    """
    content = """# Peircean Abduction Configuration
# Copy this file to .env and fill in your API keys

# Provider Selection (anthropic, openai, gemini, ollama)
PEIRCEAN_PROVIDER=anthropic

# Model Configuration
PEIRCEAN_MODEL=claude-3-sonnet-20241022
PEIRCEAN_TEMPERATURE=0.7
PEIRCEAN_TIMEOUT_SECONDS=60
PEIRCEAN_MAX_RETRIES=3

# Feature Toggles
PEIRCEAN_ENABLE_COUNCIL=true
PEIRCEAN_INTERACTIVE_MODE=false
PEIRCEAN_DEBUG_MODE=false

# Logging
PEIRCEAN_LOG_LEVEL=info

# API Keys (choose one or more)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama Configuration (if using Ollama)
OLLAMA_HOST=http://localhost:11434
PEIRCEAN_BASE_URL=http://localhost:11434

# MCP Server Configuration
PEIRCEAN_MCP_SERVER_HOST=localhost
# PEIRCEAN_MCP_SERVER_PORT=8080

# Default Abduction Settings
PEIRCEAN_DEFAULT_DOMAIN=general
PEIRCEAN_DEFAULT_NUM_HYPOTHESES=5
"""
    return content


def detect_provider_from_env() -> str | None:
    """
    Automatically detect provider from available API keys.

    Returns:
        Provider name if detected, None otherwise
    """
    # Check for API keys in order of preference
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GEMINI_API_KEY"):
        return "gemini"
    elif os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL"):
        return "ollama"

    return None


__all__ = [
    "find_env_file",
    "load_env_file",
    "get_env_var",
    "get_provider_specific_config",
    "validate_environment",
    "create_example_env_file",
    "detect_provider_from_env",
]
