"""
Peircean Abduction: Provider Integration

Provider-agnostic LLM integration with prompt-only default mode.
Supports Anthropic, OpenAI, Gemini, and Ollama providers.
"""

from .registry import (
    ProviderRegistry,
    get_provider_client,
    get_provider_registry,
    validate_provider_config,
)

__all__ = [
    "ProviderRegistry",
    "get_provider_registry",
    "get_provider_client",
    "validate_provider_config",
]
