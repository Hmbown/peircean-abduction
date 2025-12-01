"""
Peircean Abduction: Command Line Interface

Usage:
    peircean "The stock dropped 5% on good news"
    peircean --domain financial "Market anomaly observed"
    peircean --format json "System behavior unexpected"
"""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .core import abduction_prompt

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="peircean",
        description="Abductive reasoning harness for LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  peircean "Stock dropped 5% on good news"
  peircean --domain technical "CPU dropped but latency increased"
  peircean --prompt "The surprising fact to analyze"
  peircean --format json "Observation" | jq .
        """,
    )

    parser.add_argument(
        "observation", nargs="?", help="The surprising fact or anomalous observation to explain"
    )

    # Management Commands
    parser.add_argument(
        "--install", action="store_true", help="Install MCP server to Claude Desktop config"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify installation and environment"
    )

    parser.add_argument(
        "--json", action="store_true", help="Output JSON (for install or interactive mode)"
    )

    parser.add_argument(
        "-d",
        "--domain",
        choices=["general", "financial", "legal", "medical", "technical", "scientific"],
        default="general",
        help="Domain context for hypothesis templates (default: general)",
    )

    parser.add_argument(
        "-n",
        "--num-hypotheses",
        type=int,
        default=5,
        help="Number of hypotheses to generate (default: 5)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json", "prompt"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--prompt", action="store_true", help="Output just the prompt (for use with your own LLM)"
    )

    parser.add_argument(
        "--council", action="store_true", help="Include Council of Critics evaluation"
    )

    parser.add_argument("--context", type=str, help="Additional context as JSON string")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    parser.add_argument("--version", action="version", version="peircean-abduction 0.2.0")

    return parser


def run_prompt_mode(
    observation: str, domain: str, num_hypotheses: int, context: dict | None = None
) -> None:
    """Output just the prompt for external LLM use."""
    prompt = abduction_prompt(
        observation=observation, context=context, domain=domain, num_hypotheses=num_hypotheses
    )
    print(prompt)


def run_interactive(
    observation: str,
    domain: str,
    num_hypotheses: int,
    format_type: str,
    use_council: bool,
    context: dict | None = None,
    verbose: bool = False,
) -> None:
    """Run interactive abduction (requires LLM backend)."""
    # For now, just output the prompt since we don't have a default LLM
    console.print(
        Panel(
            "[yellow]No LLM backend configured locally.[/yellow]\n\n"
            "To use Peircean Abduction:\n\n"
            "1. [bold]Via Claude Desktop / Cursor (Recommended)[/bold]\n"
            "   Run: [green]peircean --install[/green]\n"
            "   Then restart Claude and use the tools directly in chat.\n\n"
            "2. [bold]Via CLI Prompt[/bold]\n"
            '   Use: [blue]peircean --prompt "your observation"[/blue]\n'
            "   (Copy the output into any LLM)\n\n"
            "Outputting prompt for your observation below:",
            title="Peircean Abduction",
        )
    )

    prompt = abduction_prompt(
        observation=observation, context=context, domain=domain, num_hypotheses=num_hypotheses
    )

    if format_type == "json":
        output = {"observation": observation, "domain": domain, "prompt": prompt}
        print(json.dumps(output, indent=2))
    else:
        console.print(Markdown(f"```\n{prompt}\n```"))


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle Management Commands
    if args.verify:
        from .validate import main as validate_main
        return validate_main()

    if args.install:
        from .mcp.setup import main as setup_main

        if args.json:
             # Just output JSON, don't write
            setup_main(["--json"])
        else:
            # Invoke setup with --write default
            console.print("[bold]Installing MCP Server config...[/bold]")
            setup_main(["--write"])
        return 0

    # Check for observation
    if not args.observation:
        parser.print_help()
        return 1

    # Parse context if provided
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing context JSON: {e}[/red]")
            return 1

    # Run in appropriate mode
    if args.prompt or args.format == "prompt":
        run_prompt_mode(
            observation=args.observation,
            domain=args.domain,
            num_hypotheses=args.num_hypotheses,
            context=context,
        )
    else:
        run_interactive(
            observation=args.observation,
            domain=args.domain,
            num_hypotheses=args.num_hypotheses,
            format_type=args.format,
            use_council=args.council,
            context=context,
            verbose=args.verbose,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
