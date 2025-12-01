"""
Peircean Abduction: Configuration Management

Provider-agnostic configuration system with environment variable hierarchy:
CLI args > Environment variables > .env file > Defaults

Supports:
- Multiple LLM providers (Anthropic, OpenAI, Gemini, Ollama)
- Feature toggles for Council of Critics and interactive mode
- Rich configuration validation
- Environment file loading with python-dotenv
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils.env import load_env_file


class Provider(str, Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PeirceanConfig(BaseSettings):
    """
    Main configuration class for Peircean Abduction.

    Environment variables take precedence over .env file values.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PEIRCEAN_",
        extra="ignore",
        case_sensitive=False,
    )

    # Core Provider Configuration
    provider: Provider = Field(
        default=Provider.ANTHROPIC,
        description="LLM provider to use for abductive reasoning"
    )

    model: Optional[str] = Field(
        default=None,
        description="Model name to use (if None, uses provider default)"
    )

    api_key: Optional[str] = Field(
        default=None,
        description="API key for the provider (if None, attempts to detect from provider-specific env vars)"
    )

    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for provider API (useful for custom endpoints or Ollama)"
    )

    # Feature Toggles
    enable_council: bool = Field(
        default=True,
        description="Enable Council of Critics evaluation by default"
    )

    interactive_mode: bool = Field(
        default=False,
        description="Enable interactive mode with real-time LLM calls (default: prompt-only mode like Hegelion)"
    )

    # Performance and Behavior
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for API calls"
    )

    timeout_seconds: int = Field(
        default=60,
        description="Timeout for API calls in seconds"
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for creative reasoning"
    )

    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to generate (None for provider default)"
    )

    # Default Abduction Settings
    default_domain: str = Field(
        default="general",
        description="Default domain for abductive analysis"
    )

    default_num_hypotheses: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Default number of hypotheses to generate"
    )

    # Logging and Debugging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level for debugging"
    )

    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode with verbose output"
    )

    # MCP Configuration
    mcp_server_port: Optional[int] = Field(
        default=None,
        description="Port for MCP server (None for automatic)"
    )

    mcp_server_host: str = Field(
        default="localhost",
        description="Host for MCP server"
    )

    @validator("model", pre=True, always=True)
    def set_default_model(cls, v: Optional[str], values: dict[str, Any]) -> str:
        """Set default model based on provider if not specified."""
        if v is not None:
            return v

        provider = values.get("provider", Provider.ANTHROPIC)
        default_models = {
            Provider.ANTHROPIC: "claude-3-sonnet-20241022",
            Provider.OPENAI: "gpt-4",
            Provider.GEMINI: "gemini-pro",
            Provider.OLLAMA: "llama2",
        }
        return default_models.get(provider, "claude-3-sonnet-20241022")

    @validator("api_key", pre=True, always=True)
    def detect_api_key(cls, v: Optional[str], values: dict[str, Any]) -> Optional[str]:
        """Detect API key from provider-specific environment variables if not set."""
        if v is not None:
            return v

        provider = values.get("provider", Provider.ANTHROPIC)
        env_key_mapping = {
            Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
            Provider.OPENAI: "OPENAI_API_KEY",
            Provider.GEMINI: "GEMINI_API_KEY",
            Provider.OLLAMA: None,  # Ollama typically doesn't need API key
        }

        env_key = env_key_mapping.get(provider)
        if env_key:
            return os.getenv(env_key)

        return None

    @validator("base_url", pre=True, always=True)
    def set_default_base_url(cls, v: Optional[str], values: dict[str, Any]) -> Optional[str]:
        """Set default base URL for certain providers."""
        if v is not None:
            return v

        provider = values.get("provider")
        if provider == Provider.OLLAMA:
            # Try to detect Ollama host from common environment variables
            return (
                os.getenv("OLLAMA_HOST") or
                os.getenv("OLLAMA_BASE_URL") or
                "http://localhost:11434"
            )

        return None

    def get_provider_config(self) -> dict[str, Any]:
        """Get provider-specific configuration dictionary."""
        base_config: dict[str, Any] = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout_seconds,
            "max_retries": self.max_retries,
        }

        # Add provider-specific configuration
        if self.provider == Provider.ANTHROPIC:
            base_config.update({
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            })
        elif self.provider == Provider.OPENAI:
            base_config.update({
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            })
        elif self.provider == Provider.GEMINI:
            base_config.update({
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            })
        elif self.provider == Provider.OLLAMA:
            base_config.update({
                "model": self.model,
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            })

        return base_config

    def validate_config(self) -> list[str]:
        """Validate the configuration and return a list of issues."""
        issues = []

        # Check if provider requires API key
        if self.provider != Provider.OLLAMA and not self.api_key:
            issues.append(
                f"API key required for {self.provider.value}. "
                f"Set PEIRCEAN_API_KEY or {self.provider.value.upper()}_API_KEY"
            )

        # Check model validity for provider
        provider_models = {
            Provider.ANTHROPIC: [
                "claude-3-sonnet-20241022", "claude-3-haiku-20241022",
                "claude-3-opus-20241022"
            ],
            Provider.OPENAI: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            Provider.GEMINI: ["gemini-pro", "gemini-pro-vision"],
            Provider.OLLAMA: None,  # Ollama models are dynamic
        }

        if self.provider in provider_models and provider_models[self.provider]:
            valid_models = provider_models[self.provider]
            if valid_models and self.model not in valid_models:
                issues.append(
                    f"Unknown model '{self.model}' for {self.provider.value}. "
                    f"Known models: {', '.join(valid_models)}"
                )

        # Check Ollama connectivity
        if self.provider == Provider.OLLAMA and self.base_url:
            try:
                import httpx
                with httpx.Client(timeout=5) as client:
                    response = client.get(f"{self.base_url}/api/tags")
                    if response.status_code != 200:
                        issues.append(f"Cannot reach Ollama at {self.base_url}")
            except Exception:
                issues.append(f"Failed to connect to Ollama at {self.base_url}")

        return issues

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for display."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "base_url": self.base_url,
            "enable_council": self.enable_council,
            "interactive_mode": self.interactive_mode,
            "timeout_seconds": self.timeout_seconds,
            "temperature": self.temperature,
            "debug_mode": self.debug_mode,
        }

    def to_env_file_content(self) -> str:
        """Generate .env file content from current configuration."""
        lines = ["# Peircean Abduction Configuration", ""]

        # Provider configuration
        lines.extend([
            f"PEIRCEAN_PROVIDER={self.provider.value}",
            f"PEIRCEAN_MODEL={self.model}",
        ])

        if self.api_key:
            lines.append(f"PEIRCEAN_API_KEY={self.api_key}")

        if self.base_url:
            lines.append(f"PEIRCEAN_BASE_URL={self.base_url}")

        lines.extend([
            "",
            "# Feature Toggles",
            f"PEIRCEAN_ENABLE_COUNCIL={'true' if self.enable_council else 'false'}",
            f"PEIRCEAN_INTERACTIVE_MODE={'true' if self.interactive_mode else 'false'}",
            "",
            "# Performance",
            f"PEIRCEAN_MAX_RETRIES={self.max_retries}",
            f"PEIRCEAN_TIMEOUT_SECONDS={self.timeout_seconds}",
            f"PEIRCEAN_TEMPERATURE={self.temperature}",
            "",
            "# Debugging",
            f"PEIRCEAN_LOG_LEVEL={self.log_level.value}",
            f"PEIRCEAN_DEBUG_MODE={'true' if self.debug_mode else 'false'}",
        ])

        return "\n".join(lines)


# Global configuration instance
_config: Optional[PeirceanConfig] = None


def get_config() -> PeirceanConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Load .env file if it exists
        load_env_file()
        _config = PeirceanConfig()
    return _config


def set_config(config: PeirceanConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reload_config() -> PeirceanConfig:
    """Reload configuration from environment variables."""
    global _config
    load_env_file()
    _config = PeirceanConfig()
    return _config


# Convenience functions for common configuration access
def get_provider() -> Provider:
    """Get the current provider."""
    return get_config().provider


def get_model() -> Optional[str]:
    """Get the current model."""
    return get_config().model


def get_api_key() -> Optional[str]:
    """Get the current API key."""
    return get_config().api_key


def is_council_enabled() -> bool:
    """Check if Council of Critics is enabled."""
    return get_config().enable_council


def is_interactive_mode() -> bool:
    """Check if interactive mode is enabled."""
    return get_config().interactive_mode


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_config().debug_mode


__all__ = [
    "Provider",
    "LogLevel",
    "PeirceanConfig",
    "get_config",
    "set_config",
    "reload_config",
    "get_provider",
    "get_model",
    "get_api_key",
    "is_council_enabled",
    "is_interactive_mode",
    "is_debug_mode",
]