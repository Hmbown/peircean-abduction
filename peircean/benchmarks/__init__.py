"""
Peircean Abduction: Performance Benchmarks

Benchmark suite for measuring and comparing performance across
different providers, configurations, and usage patterns.

Usage:
    peircean-bench                          # Run all benchmarks
    peircean-bench --prompt-generation      # Test prompt generation speed
    peircean-bench --provider <name>        # Test specific provider
    peircean-bench --scenario <name>        # Run specific scenario
    peircean-bench --export-json results.json
"""

from .providers import ProviderBenchmark
from .runner import main as run_benchmarks
from .scenarios import (
    BenchmarkScenario,
    get_scenario_by_name,
    get_standard_scenarios,
)

__all__ = [
    "run_benchmarks",
    "BenchmarkScenario",
    "get_standard_scenarios",
    "get_scenario_by_name",
    "ProviderBenchmark",
]
