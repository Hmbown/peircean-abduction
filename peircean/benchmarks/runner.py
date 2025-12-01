"""
Main benchmark runner for Peircean Abduction.

CLI interface for running performance benchmarks across different scenarios and providers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, TaskID, track
from rich.panel import Panel

from .scenarios import (
    get_standard_scenarios,
    get_scenario_by_name,
    get_scenarios_by_tag,
    get_scenarios_by_domain,
    get_quick_scenarios,
    get_complex_scenarios,
    get_council_scenarios,
    BenchmarkScenario,
)
from .utils import (
    run_benchmark_scenario,
    calculate_summary,
    print_results_table,
    save_results_json,
    load_results_json,
    get_system_info,
    validate_scenario_expectations,
    create_progress_report,
)
from .providers import (
    test_all_providers,
    benchmark_all_providers,
    ProviderBenchmark,
)

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for benchmark runner."""
    parser = argparse.ArgumentParser(
        prog="peircean-bench",
        description="Performance benchmarks for Peircean Abduction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  peircean-bench                          # Run all standard scenarios
  peircean-bench --quick                  # Run quick scenarios only
  peircean-bench --complex                # Run complex scenarios only
  peircean-bench --scenario simple_financial
  peircean-bench --domain financial
  peircean-bench --tag quick
  peircean-bench --providers              # Test provider availability
  peircean-bench --prompt-generation      # Test prompt generation only
  peircean-bench --export-json results.json
        """,
    )

    # Scenario selection
    parser.add_argument("--scenario", type=str, help="Run specific scenario by name")

    parser.add_argument(
        "--domain",
        type=str,
        choices=["general", "financial", "legal", "medical", "technical", "scientific"],
        help="Run scenarios for specific domain",
    )

    parser.add_argument("--tag", type=str, help="Run scenarios with specific tag")

    parser.add_argument("--quick", action="store_true", help="Run quick scenarios only")

    parser.add_argument("--complex", action="store_true", help="Run complex scenarios only")

    parser.add_argument(
        "--council", action="store_true", help="Run Council of Critics scenarios only"
    )

    # Provider testing
    parser.add_argument(
        "--providers", action="store_true", help="Test provider availability and configuration"
    )

    parser.add_argument("--provider", type=str, help="Test specific provider")

    parser.add_argument("--all-providers", action="store_true", help="Test all available providers")

    # Test types
    parser.add_argument(
        "--prompt-generation", action="store_true", help="Test prompt generation performance only"
    )

    # Output options
    parser.add_argument("--export-json", type=str, help="Export results to JSON file")

    parser.add_argument(
        "--import-json", type=str, help="Import results from JSON file for comparison"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument(
        "--runs", type=int, default=3, help="Number of runs per scenario (default: 3)"
    )

    parser.add_argument("--no-table", action="store_true", help="Don't display results table")

    # System info
    parser.add_argument("--system-info", action="store_true", help="Show system information only")

    parser.add_argument("--version", action="version", version="peircean-bench 1.2.0")

    return parser


def get_scenarios_from_args(args: argparse.Namespace) -> List[BenchmarkScenario]:
    """Get scenarios based on command line arguments."""
    if args.scenario:
        scenario = get_scenario_by_name(args.scenario)
        if not scenario:
            console.print(f"[red]Scenario '{args.scenario}' not found[/red]")
            sys.exit(1)
        return [scenario]

    if args.domain:
        return get_scenarios_by_domain(args.domain)

    if args.tag:
        return get_scenarios_by_tag(args.tag)

    if args.quick:
        return get_quick_scenarios()

    if args.complex:
        return get_complex_scenarios()

    if args.council:
        return get_council_scenarios()

    # Default: all standard scenarios
    return get_standard_scenarios()


def run_provider_tests(args: argparse.Namespace) -> int:
    """Run provider availability and configuration tests."""
    console.print(Panel("[bold blue]Provider Availability Tests[/bold blue]"))

    if args.provider:
        from .providers import test_provider_availability

        provider_info = test_provider_availability(args.provider)
        providers = [provider_info]
    else:
        providers = test_all_providers()

    # Display results
    from rich.table import Table

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan", width=15)
    table.add_column("Display Name", style="white", width=20)
    table.add_column("Available", style="green", width=10)
    table.add_column("Configured", style="yellow", width=10)
    table.add_column("Error", style="red", width=30)

    for provider_info in providers:
        available = "✅ Yes" if provider_info.available else "❌ No"
        configured = "✅ Yes" if provider_info.configured else "❌ No"
        error = provider_info.error_message or ""

        table.add_row(provider_info.name, provider_info.display_name, available, configured, error)

    console.print(table)

    # If all providers are requested, run benchmarks too
    if args.all_providers:
        console.print("\n[bold blue]Running Provider Benchmarks[/bold blue]")

        test_observation = "Stock price dropped 5% on good news"
        results = benchmark_all_providers(observation=test_observation, num_runs=args.runs)

        for provider_name, result in results["providers"].items():
            if result["success"]:
                console.print(f"\n[green]✅ {provider_name}[/green]")
                console.print(f"  Avg time: {result['avg_generation_time']:.3f}s")
                console.print(f"  Avg length: {result['avg_prompt_length']:.0f} chars")
            else:
                console.print(f"\n[red]❌ {provider_name}[/red]")
                console.print(f"  Error: {result['error']}")

    return 0


def run_prompt_generation_tests(
    scenarios: List[BenchmarkScenario], args: argparse.Namespace
) -> int:
    """Run prompt generation performance tests."""
    console.print(Panel(f"[bold blue]Prompt Generation Benchmarks[/bold blue]"))
    console.print(f"Running {len(scenarios)} scenarios with {args.runs} runs each")

    from ..config import get_config

    config = get_config()
    provider_name = config.provider.value

    all_results = []

    with Progress() as progress:
        total_tasks = len(scenarios) * args.runs
        task = progress.add_task("[green]Running benchmarks...", total=total_tasks)

        for scenario in scenarios:
            scenario_results = []

            for run in range(args.runs):
                result = run_benchmark_scenario(
                    scenario_name=scenario.name,
                    provider_name=provider_name,
                    observation=scenario.observation,
                    domain=scenario.domain,
                    num_hypotheses=scenario.num_hypotheses,
                    context=scenario.context,
                    use_council=scenario.use_council,
                )

                scenario_results.append(result)
                all_results.append(result)

                # Validate against expectations
                validation = validate_scenario_expectations(
                    result, scenario.expected_min_prompt_length, scenario.expected_max_time_seconds
                )

                if args.verbose:
                    status = "✅" if result.success else "❌"
                    console.print(
                        f"{status} {scenario.name} (run {run + 1}): {result.generation_time_seconds:.3f}s"
                    )

                progress.advance(task)

            # Calculate scenario summary
            if scenario_results:
                summary = calculate_summary(scenario_results)
                if args.verbose:
                    console.print(
                        f"  Summary: {summary.success_rate:.1%} success, {summary.avg_generation_time:.3f}s avg"
                    )

    # Calculate overall summaries by scenario
    from collections import defaultdict

    results_by_scenario = defaultdict(list)
    for result in all_results:
        results_by_scenario[result.scenario_name].append(result)

    summaries = []
    for scenario_name, scenario_results in results_by_scenario.items():
        summary = calculate_summary(scenario_results)
        summaries.append(summary)

    # Display results table
    if not args.no_table and summaries:
        console.print("\n")
        print_results_table(summaries)

    # Export results if requested
    if args.export_json:
        export_path = Path(args.export_json)
        save_results_json(all_results, export_path)
        console.print(f"\n[green]✅ Results exported to {export_path}[/green]")

    return 0


def main() -> int:
    """Main benchmark runner entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle system info
    if args.system_info:
        system_info = get_system_info()
        console.print(Panel("[bold blue]System Information[/bold blue]"))
        console.print(json.dumps(system_info, indent=2))
        return 0

    # Handle provider tests
    if args.providers or args.provider or args.all_providers:
        return run_provider_tests(args)

    # Get scenarios to run
    scenarios = get_scenarios_from_args(args)

    if not scenarios:
        console.print("[red]No scenarios found matching criteria[/red]")
        return 1

    # Display what will be run
    console.print(Panel(f"[bold blue]Peircean Abduction Benchmarks[/bold blue]"))
    console.print(f"Running {len(scenarios)} scenario(s):")
    for scenario in scenarios:
        console.print(f"  • {scenario.name}: {scenario.description}")

    # Run benchmarks
    if args.prompt_generation or not args.providers:
        return run_prompt_generation_tests(scenarios, args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
