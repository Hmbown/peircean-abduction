"""
Utility functions for benchmarking Peircean Abduction.

Performance measurement, result aggregation, and reporting utilities.
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

console = Console()


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    scenario_name: str
    provider_name: str
    prompt_length: int
    generation_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    additional_metrics: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.additional_metrics is None:
            self.additional_metrics = {}


@dataclass
class BenchmarkSummary:
    """Summary statistics for benchmark results."""

    scenario_name: str
    provider_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_prompt_length: float
    avg_generation_time: float
    min_generation_time: float
    max_generation_time: float
    std_deviation: float
    success_rate: float


def measure_prompt_generation(
    observation: str,
    domain: str = "general",
    num_hypotheses: int = 5,
    context: Optional[Dict[str, Any]] = None,
    use_council: bool = True
) -> Tuple[str, float]:
    """
    Measure prompt generation performance.

    Args:
        observation: The observation to analyze
        domain: Analysis domain
        num_hypotheses: Number of hypotheses to generate
        context: Additional context
        use_council: Whether to include Council of Critics

    Returns:
        Tuple of (generated_prompt, time_taken_seconds)
    """
    from ..core import abduction_prompt

    start_time = time.time()
    prompt = abduction_prompt(
        observation=observation,
        context=context,
        domain=domain,
        num_hypotheses=num_hypotheses
    )
    end_time = time.time()

    generation_time = end_time - start_time
    return prompt, generation_time


def run_benchmark_scenario(
    scenario_name: str,
    provider_name: str,
    observation: str,
    domain: str = "general",
    num_hypotheses: int = 5,
    context: Optional[Dict[str, Any]] = None,
    use_council: bool = True
) -> BenchmarkResult:
    """
    Run a single benchmark scenario.

    Args:
        scenario_name: Name of the scenario
        provider_name: Name of the provider being tested
        observation: The observation to analyze
        domain: Analysis domain
        num_hypotheses: Number of hypotheses to generate
        context: Additional context
        use_council: Whether to include Council of Critics

    Returns:
        BenchmarkResult with performance metrics
    """
    try:
        prompt, generation_time = measure_prompt_generation(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
            use_council=use_council
        )

        return BenchmarkResult(
            scenario_name=scenario_name,
            provider_name=provider_name,
            prompt_length=len(prompt),
            generation_time_seconds=generation_time,
            success=True
        )

    except Exception as e:
        return BenchmarkResult(
            scenario_name=scenario_name,
            provider_name=provider_name,
            prompt_length=0,
            generation_time_seconds=0.0,
            success=False,
            error_message=str(e)
        )


def calculate_summary(results: List[BenchmarkResult]) -> BenchmarkSummary:
    """Calculate summary statistics for benchmark results."""
    if not results:
        raise ValueError("No results to summarize")

    scenario_name = results[0].scenario_name
    provider_name = results[0].provider_name

    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]

    if not successful_results:
        # All runs failed
        return BenchmarkSummary(
            scenario_name=scenario_name,
            provider_name=provider_name,
            total_runs=len(results),
            successful_runs=0,
            failed_runs=len(failed_results),
            avg_prompt_length=0.0,
            avg_generation_time=0.0,
            min_generation_time=0.0,
            max_generation_time=0.0,
            std_deviation=0.0,
            success_rate=0.0
        )

    generation_times = [r.generation_time_seconds for r in successful_results]
    prompt_lengths = [r.prompt_length for r in successful_results]

    return BenchmarkSummary(
        scenario_name=scenario_name,
        provider_name=provider_name,
        total_runs=len(results),
        successful_runs=len(successful_results),
        failed_runs=len(failed_results),
        avg_prompt_length=statistics.mean(prompt_lengths),
        avg_generation_time=statistics.mean(generation_times),
        min_generation_time=min(generation_times),
        max_generation_time=max(generation_times),
        std_deviation=statistics.stdev(generation_times) if len(generation_times) > 1 else 0.0,
        success_rate=len(successful_results) / len(results)
    )


def print_results_table(summaries: List[BenchmarkSummary]) -> None:
    """Print a formatted table of benchmark results."""
    table = Table(title="Benchmark Results Summary")
    table.add_column("Scenario", style="cyan", no_wrap=True)
    table.add_column("Provider", style="green")
    table.add_column("Runs", justify="center", style="white")
    table.add_column("Success %", justify="center", style="yellow")
    table.add_column("Avg Time (s)", justify="right", style="blue")
    table.add_column("Min Time (s)", justify="right", style="dim")
    table.add_column("Max Time (s)", justify="right", style="dim")
    table.add_column("Avg Length", justify="right", style="magenta")

    for summary in summaries:
        success_rate = f"{summary.success_rate * 100:.1f}%"
        avg_time = f"{summary.avg_generation_time:.3f}"
        min_time = f"{summary.min_generation_time:.3f}"
        max_time = f"{summary.max_generation_time:.3f}"
        avg_length = f"{summary.avg_prompt_length:.0f}"
        runs = f"{summary.successful_runs}/{summary.total_runs}"

        table.add_row(
            summary.scenario_name,
            summary.provider_name,
            runs,
            success_rate,
            avg_time,
            min_time,
            max_time,
            avg_length
        )

    console.print(table)


def save_results_json(results: List[BenchmarkResult], filepath: Path) -> None:
    """Save benchmark results to JSON file."""
    data = {
        "results": [asdict(result) for result in results],
        "summary": {
            "total_results": len(results),
            "successful_results": len([r for r in results if r.success]),
            "failed_results": len([r for r in results if not r.success])
        }
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_results_json(filepath: Path) -> List[BenchmarkResult]:
    """Load benchmark results from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    results = []
    for result_data in data["results"]:
        result = BenchmarkResult(**result_data)
        results.append(result)

    return results


def compare_results(results_a: List[BenchmarkResult], results_b: List[BenchmarkResult]) -> Dict[str, Any]:
    """Compare two sets of benchmark results."""
    if not results_a or not results_b:
        return {"error": "Both result sets must be non-empty"}

    summary_a = calculate_summary(results_a)
    summary_b = calculate_summary(results_b)

    # Calculate performance differences
    time_improvement = (summary_a.avg_generation_time - summary_b.avg_generation_time) / summary_a.avg_generation_time
    length_diff = summary_b.avg_prompt_length - summary_a.avg_prompt_length
    success_rate_diff = (summary_b.success_rate - summary_a.success_rate) * 100

    return {
        "baseline": asdict(summary_a),
        "comparison": asdict(summary_b),
        "improvements": {
            "time_improvement_percent": time_improvement * 100,
            "prompt_length_difference": length_diff,
            "success_rate_improvement_percent": success_rate_diff
        },
        "better_performance": summary_b.avg_generation_time < summary_a.avg_generation_time,
        "higher_success_rate": summary_b.success_rate > summary_a.success_rate
    }


def get_system_info() -> Dict[str, Any]:
    """Get system information for benchmarking context."""
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "timestamp": time.time()
    }


def validate_scenario_expectations(
    result: BenchmarkResult,
    expected_min_prompt_length: int,
    expected_max_time_seconds: float
) -> Dict[str, bool]:
    """Validate benchmark result against scenario expectations."""
    if not result.success:
        return {"prompt_length_valid": False, "time_valid": False}

    return {
        "prompt_length_valid": result.prompt_length >= expected_min_prompt_length,
        "time_valid": result.generation_time_seconds <= expected_max_time_seconds
    }


def create_progress_report(scenarios: List[str], providers: List[str]) -> str:
    """Create a progress report for benchmark execution."""
    total_scenarios = len(scenarios)
    total_providers = len(providers)
    total_benchmarks = total_scenarios * total_providers

    return f"""
Benchmark Progress Report
========================

Scenarios to test: {total_scenarios}
Providers to test: {total_providers}
Total benchmarks: {total_benchmarks}

Scenarios: {', '.join(scenarios)}
Providers: {', '.join(providers)}
"""