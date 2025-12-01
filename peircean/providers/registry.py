"""
Peircean Abduction: Provider Registry

Provider registry for managing different LLM providers with prompt-only
default behavior and optional interactive mode.

Design principles:
- Default to prompt generation (no API calls required)
- Optional interactive mode with real LLM integration
- Provider-agnostic interface with fallback capabilities
- Graceful handling of missing dependencies or API keys
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderCapabilities:
    """Capabilities and features supported by a provider."""

    supports_streaming: bool = True
    supports_functions: bool = True
    supports_system_messages: bool = True
    max_tokens: int | None = None
    default_model: str | None = None


@dataclass
class ProviderInfo:
    """Information about a provider."""

    name: str
    display_name: str
    description: str
    capabilities: ProviderCapabilities
    dependency_name: str | None = None
    env_api_key: str | None = None
    examples: list[str] | None = None

    def __post_init__(self) -> None:
        if self.examples is None:
            self.examples = []


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.client = None
        self._initialized = False

    @abstractmethod
    def get_info(self) -> ProviderInfo:
        """Get provider information."""
        pass

    @abstractmethod
    def _create_client(self) -> Any:
        """Create the provider-specific client."""
        pass

    def initialize(self) -> bool:
        """
        Initialize the provider client.

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        try:
            self.client = self._create_client()
            self._initialized = True
            return True
        except Exception:
            self._initialized = False
            return False

    def is_available(self) -> bool:
        """Check if provider is available for use."""
        if not self._initialized:
            return self.initialize()
        return self._initialized

    @abstractmethod
    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: dict[str, Any] | None = None,
        use_council: bool = True,
    ) -> str:
        """
        Generate abductive reasoning prompt (always available).

        This method should work without API calls - it just formats
        the prompt for the user to copy to any LLM.

        Returns:
            Formatted prompt string
        """
        pass

    def generate_completion(self, prompt: str, **kwargs: Any) -> str | None:
        """
        Generate completion using the provider (requires API integration).

        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the provider

        Returns:
            Generated completion text, or None if unavailable
        """
        if not self.is_available():
            return None

        try:
            assert self.client is not None
            return self._generate_completion_impl(prompt, **kwargs)
        except Exception:
            return None

    def _generate_completion_impl(self, prompt: str, **kwargs: Any) -> str:
        """Implementation-specific completion generation."""
        raise NotImplementedError("Direct completion not implemented for this provider")

    def validate_config(self) -> list[str]:
        """
        Validate provider configuration.

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        info = self.get_info()
        if info.env_api_key and not self.config.get("api_key"):
            issues.append(f"API key required. Set {info.env_api_key} environment variable.")

        return issues


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider."""

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="anthropic",
            display_name="Anthropic Claude",
            description="Advanced reasoning and analysis with Claude models",
            capabilities=ProviderCapabilities(
                supports_streaming=True,
                supports_functions=True,
                supports_system_messages=True,
                max_tokens=4096,
                default_model="claude-3-sonnet-20241022",
            ),
            dependency_name="anthropic",
            env_api_key="ANTHROPIC_API_KEY",
            examples=["claude-3-sonnet-20241022", "claude-3-haiku-20241022"],
        )

    def _create_client(self) -> Any:
        try:
            from anthropic import Anthropic

            return Anthropic(
                api_key=self.config["api_key"],
                base_url=self.config.get("base_url"),
                timeout=self.config.get("timeout", 60),
            )
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            ) from None

    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: dict[str, Any] | None = None,
        use_council: bool = True,
    ) -> str:
        """Generate abductive reasoning prompt for Claude."""
        # Import the existing prompt generation logic
        from ..core import abduction_prompt

        return abduction_prompt(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
        )

    def _generate_completion_impl(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion using Claude."""
        assert self.client is not None
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.config.get("model", "claude-3-sonnet-20241022"),
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
            messages=messages,
        )

        return str(response.content[0].text)


class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider."""

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openai",
            display_name="OpenAI GPT",
            description="Versatile language understanding and generation",
            capabilities=ProviderCapabilities(
                supports_streaming=True,
                supports_functions=True,
                supports_system_messages=True,
                max_tokens=4096,
                default_model="gpt-4",
            ),
            dependency_name="openai",
            env_api_key="OPENAI_API_KEY",
            examples=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        )

    def _create_client(self) -> Any:
        try:
            from openai import OpenAI

            return OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config.get("base_url"),
                timeout=self.config.get("timeout", 60),
                organization=self.config.get("organization"),
            )
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            ) from None

    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: dict[str, Any] | None = None,
        use_council: bool = True,
    ) -> str:
        """Generate abductive reasoning prompt for GPT."""
        from ..core import abduction_prompt

        return abduction_prompt(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
        )

    def _generate_completion_impl(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion using GPT."""
        assert self.client is not None
        response = self.client.chat.completions.create(
            model=self.config.get("model", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=kwargs.get("temperature", 0.7),
        )

        return str(response.choices[0].message.content)


class GeminiProvider(BaseProvider):
    """Google Gemini provider."""

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="gemini",
            display_name="Google Gemini",
            description="Multimodal AI with strong reasoning capabilities",
            capabilities=ProviderCapabilities(
                supports_streaming=True,
                supports_functions=True,
                supports_system_messages=False,
                max_tokens=2048,
                default_model="gemini-pro",
            ),
            dependency_name="google-generativeai",
            env_api_key="GEMINI_API_KEY",
            examples=["gemini-pro", "gemini-pro-vision"],
        )

    def _create_client(self) -> Any:
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.config["api_key"])
            return genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            ) from None

    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: dict[str, Any] | None = None,
        use_council: bool = True,
    ) -> str:
        """Generate abductive reasoning prompt for Gemini."""
        from ..core import abduction_prompt

        return abduction_prompt(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
        )

    def _generate_completion_impl(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion using Gemini."""
        assert self.client is not None
        model = self.client.GenerativeModel(self.config.get("model", "gemini-pro"))
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            },
        )
        return str(response.text)


class OllamaProvider(BaseProvider):
    """Ollama local provider."""

    def get_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="ollama",
            display_name="Ollama (Local)",
            description="Run models locally with Ollama",
            capabilities=ProviderCapabilities(
                supports_streaming=True,
                supports_functions=False,
                supports_system_messages=False,
                max_tokens=2048,
                default_model="llama2",
            ),
            dependency_name="ollama",
            env_api_key=None,  # Ollama doesn't require API keys
            examples=["llama2", "codellama", "mistral"],
        )

    def _create_client(self) -> Any:
        try:
            import ollama

            # Configure base URL if provided
            base_url = self.config.get("base_url", "http://localhost:11434")
            # Type ignore because ollama module is dynamically typed
            ollama.host = base_url  # type: ignore[attr-defined]
            return ollama
        except ImportError:
            raise ImportError(
                "ollama package not installed. Install with: pip install ollama"
            ) from None

    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: dict[str, Any] | None = None,
        use_council: bool = True,
    ) -> str:
        """Generate abductive reasoning prompt for Ollama."""
        from ..core import abduction_prompt

        return abduction_prompt(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
        )

    def _generate_completion_impl(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion using Ollama."""
        assert self.client is not None
        response = self.client.chat(
            model=self.config.get("model", "llama2"),
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048),
            },
        )
        return str(response["message"]["content"])


class ProviderRegistry:
    """Registry for managing LLM providers."""

    def __init__(self) -> None:
        self._providers: dict[str, type[BaseProvider]] = {
            "anthropic": AnthropicProvider,
            "openai": OpenAIProvider,
            "gemini": GeminiProvider,
            "ollama": OllamaProvider,
        }

    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        return list(self._providers.keys())

    def get_provider_info(self, provider_name: str) -> ProviderInfo | None:
        """Get information about a provider."""
        provider_class = self._providers.get(provider_name)
        if provider_class:
            # Create a dummy config to get info
            dummy_provider = provider_class({})
            return dummy_provider.get_info()
        return None

    def create_provider(self, provider_name: str, config: dict[str, Any]) -> BaseProvider | None:
        """Create a provider instance."""
        provider_class = self._providers.get(provider_name)
        if provider_class:
            return provider_class(config)
        return None

    def validate_provider_config(self, provider_name: str, config: dict[str, Any]) -> list[str]:
        """Validate provider configuration."""
        provider = self.create_provider(provider_name, config)
        if provider:
            return provider.validate_config()
        return [f"Unknown provider: {provider_name}"]

    def get_fallback_provider(self) -> str:
        """Get a fallback provider when none is specified."""
        # Try to detect from environment
        from ..utils.env import detect_provider_from_env

        detected = detect_provider_from_env()
        if detected:
            return detected

        # Default to anthropic (like Hegelion defaults to its primary provider)
        return "anthropic"


# Global registry instance
_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


def get_provider_client(provider_name: str, config: dict[str, Any]) -> BaseProvider | None:
    """Get a provider client."""
    registry = get_provider_registry()
    return registry.create_provider(provider_name, config)


def validate_provider_config(provider_name: str, config: dict[str, Any]) -> list[str]:
    """Validate provider configuration."""
    registry = get_provider_registry()
    return registry.validate_provider_config(provider_name, config)


__all__ = [
    "ProviderRegistry",
    "BaseProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "OllamaProvider",
    "ProviderInfo",
    "ProviderCapabilities",
    "get_provider_registry",
    "get_provider_client",
    "validate_provider_config",
]
