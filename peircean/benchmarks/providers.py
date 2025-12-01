"""
Provider-specific benchmarking utilities.

Test provider availability, configuration, and performance characteristics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from ..config import get_config
from ..providers import get_provider_client, get_provider_registry


@dataclass
class ProviderInfo:
    """Information about a provider for benchmarking."""

    name: str
    display_name: str
    available: bool
    configured: bool
    supports_interactive: bool
    configuration: dict[str, Any]
    error_message: str | None = None


def test_provider_availability(provider_name: str) -> ProviderInfo:
    """
    Test if a provider is available and properly configured.

    Args:
        provider_name: Name of the provider to test

    Returns:
        ProviderInfo with availability status and configuration details
    """
    config = get_config()
    registry = get_provider_registry()

    try:
        # Get provider info from registry
        provider_info = registry.get_provider_info(provider_name)
        if not provider_info:
            return ProviderInfo(
                name=provider_name,
                display_name=provider_name,
                available=False,
                configured=False,
                supports_interactive=False,
                configuration={},
                error_message="Provider not found in registry",
            )

        # Get provider configuration
        provider_config = config.get_provider_config()

        # Try to create client instance
        client = get_provider_client(provider_name, provider_config)

        if not client:
            return ProviderInfo(
                name=provider_name,
                display_name=provider_info.display_name,
                available=False,
                configured=False,
                supports_interactive=False,
                configuration=provider_config,
                error_message="Failed to create provider client",
            )

        # Test if client is available
        is_available = client.is_available()

        return ProviderInfo(
            name=provider_name,
            display_name=provider_info.display_name,
            available=is_available,
            configured=True,
            supports_interactive=config.interactive_mode,
            configuration=provider_config,
            error_message=None if is_available else "Provider not available (configuration issue)",
        )

    except Exception as e:
        return ProviderInfo(
            name=provider_name,
            display_name=provider_name,
            available=False,
            configured=False,
            supports_interactive=False,
            configuration={},
            error_message=str(e),
        )


def test_all_providers() -> list[ProviderInfo]:
    """Test all available providers."""

    registry = get_provider_registry()
    providers = registry.get_available_providers()

    results = []
    for provider_name in providers:
        provider_info = test_provider_availability(provider_name)
        results.append(provider_info)

    return results


def benchmark_provider_prompt_generation(
    provider_name: str,
    observation: str,
    domain: str = "general",
    num_hypotheses: int = 5,
    context: dict[str, Any] | None = None,
    use_council: bool = True,
    num_runs: int = 3,
) -> dict[str, Any]:
    """
    Benchmark prompt generation for a specific provider.

    Args:
        provider_name: Name of the provider
        observation: Observation to analyze
        domain: Analysis domain
        num_hypotheses: Number of hypotheses
        context: Additional context
        use_council: Whether to include Council of Critics
        num_runs: Number of test runs

    Returns:
        Dictionary with benchmark results
    """
    config = get_config()
    provider_config = config.get_provider_config()

    try:
        client = get_provider_client(provider_name, provider_config)
        if not client or not client.is_available():
            return {
                "provider": provider_name,
                "success": False,
                "error": "Provider not available",
                "runs": [],
            }

        # Run multiple benchmarks
        runs = []
        for i in range(num_runs):
            start_time = time.time()

            prompt = client.generate_prompt(
                observation=observation,
                domain=domain,
                num_hypotheses=num_hypotheses,
                context=context,
                use_council=use_council,
            )

            end_time = time.time()
            generation_time = end_time - start_time

            runs.append(
                {
                    "run": i + 1,
                    "prompt_length": len(prompt),
                    "generation_time_seconds": generation_time,
                    "success": True,
                }
            )

        # Calculate statistics
        generation_times = [r["generation_time_seconds"] for r in runs]
        prompt_lengths = [r["prompt_length"] for r in runs]

        return {
            "provider": provider_name,
            "success": True,
            "num_runs": num_runs,
            "avg_generation_time": sum(generation_times) / len(generation_times),
            "min_generation_time": min(generation_times),
            "max_generation_time": max(generation_times),
            "avg_prompt_length": sum(prompt_lengths) / len(prompt_lengths),
            "runs": runs,
        }

    except Exception as e:
        return {"provider": provider_name, "success": False, "error": str(e), "runs": []}


def benchmark_all_providers(
    observation: str,
    domain: str = "general",
    num_hypotheses: int = 5,
    context: dict[str, Any] | None = None,
    use_council: bool = True,
    num_runs: int = 3,
) -> dict[str, Any]:
    """
    Benchmark prompt generation across all available providers.

    Args:
        observation: Observation to analyze
        domain: Analysis domain
        num_hypotheses: Number of hypotheses
        context: Additional context
        use_council: Whether to include Council of Critics
        num_runs: Number of test runs per provider

    Returns:
        Dictionary with results for all providers
    """

    registry = get_provider_registry()
    providers = registry.get_available_providers()

    results: dict[str, Any] = {
        "observation": observation,
        "domain": domain,
        "num_hypotheses": num_hypotheses,
        "use_council": use_council,
        "num_runs_per_provider": num_runs,
        "providers": {},
        "summary": {
            "total_providers": len(providers),
            "successful_providers": 0,
            "failed_providers": 0,
        },
    }

    for provider_name in providers:
        provider_result = benchmark_provider_prompt_generation(
            provider_name=provider_name,
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
            use_council=use_council,
            num_runs=num_runs,
        )

        results["providers"][provider_name] = provider_result

        if provider_result["success"]:
            results["summary"]["successful_providers"] += 1
        else:
            results["summary"]["failed_providers"] += 1

    return results


def test_provider_configuration_completeness(provider_name: str) -> dict[str, Any]:
    """
    Test configuration completeness for a specific provider.

    Args:
        provider_name: Name of the provider to test

    Returns:
        Dictionary with configuration analysis
    """
    from ..providers import get_provider_registry

    try:
        registry = get_provider_registry()
        provider_info = registry.get_provider_info(provider_name)
        config = get_config()

        # Check environment variables
        env_vars = {}
        if provider_info and provider_info.env_api_key:
            env_vars["api_key_set"] = bool(config.api_key)

        # Check required configuration fields
        required_fields = []
        if provider_name == "ollama":
            required_fields = ["base_url"]

        configuration_status = {}
        for field in required_fields:
            configuration_status[field] = bool(getattr(config, field, None))

        # Determine overall configuration status
        api_key_configured = env_vars.get(
            "api_key_set", True
        )  # Default to True for providers without API keys
        other_fields_configured = all(configuration_status.values())

        return {
            "provider": provider_name,
            "api_key_configured": api_key_configured,
            "configuration_fields": configuration_status,
            "overall_configured": api_key_configured and other_fields_configured,
            "missing_items": [],
        }

    except Exception as e:
        return {
            "provider": provider_name,
            "error": str(e),
            "api_key_configured": False,
            "configuration_fields": {},
            "overall_configured": False,
            "missing_items": ["Configuration check failed"],
        }


class ProviderBenchmark:
    """High-level interface for provider benchmarking."""

    def __init__(self) -> None:
        self.config = get_config()

    def test_all_providers(self) -> list[ProviderInfo]:
        """Test all providers for availability and configuration."""
        return test_all_providers()

    def benchmark_current_provider(
        self, observation: str, domain: str = "general", num_runs: int = 5
    ) -> dict[str, Any]:
        """Benchmark the currently configured provider."""
        return benchmark_provider_prompt_generation(
            provider_name=self.config.provider.value,
            observation=observation,
            domain=domain,
            num_hypotheses=self.config.default_num_hypotheses,
            use_council=self.config.enable_council,
            num_runs=num_runs,
        )

    def run_comprehensive_benchmark(
        self, test_observations: list[str] | None = None
    ) -> dict[str, Any]:
        """Run comprehensive benchmark across all providers and scenarios."""
        if test_observations is None:
            test_observations = [
                "Stock dropped 5% on good news",
                "Server latency increased but CPU is flat",
                "Customer satisfaction improved while support tickets increased",
            ]

        results: dict[str, Any] = {
            "timestamp": time.time(),
            "provider_info": {},
            "benchmark_results": {},
        }

        # Test provider availability
        provider_infos = test_all_providers()
        for info in provider_infos:
            results["provider_info"][info.name] = {
                "available": info.available,
                "configured": info.configured,
                "error": info.error_message,
            }

        # Run benchmarks for available providers
        for info in provider_infos:
            if info.available:
                provider_results = []
                for i, observation in enumerate(test_observations):
                    result = benchmark_provider_prompt_generation(
                        provider_name=info.name, observation=observation, num_runs=3
                    )
                    provider_results.append(
                        {"scenario": i + 1, "observation": observation, "result": result}
                    )

                results["benchmark_results"][info.name] = provider_results

        return results
