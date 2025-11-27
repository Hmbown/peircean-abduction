"""
Peircean Abduction: Command Line Interface

Usage:
    peircean "The stock dropped 5% on good news"
    peircean --domain financial "Market anomaly observed"
    peircean --format json "System behavior unexpected"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .core import AbductionAgent, Domain, abduction_prompt


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
        """
    )
    
    parser.add_argument(
        "observation",
        nargs="?",
        help="The surprising fact or anomalous observation to explain"
    )
    
    parser.add_argument(
        "-d", "--domain",
        choices=["general", "financial", "legal", "medical", "technical", "scientific"],
        default="general",
        help="Domain context for hypothesis templates (default: general)"
    )
    
    parser.add_argument(
        "-n", "--num-hypotheses",
        type=int,
        default=5,
        help="Number of hypotheses to generate (default: 5)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "json", "prompt"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Output just the prompt (for use with your own LLM)"
    )
    
    parser.add_argument(
        "--council",
        action="store_true",
        help="Include Council of Critics evaluation"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        help="Additional context as JSON string"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="peircean-abduction 0.1.0"
    )
    
    return parser


def run_prompt_mode(
    observation: str,
    domain: str,
    num_hypotheses: int,
    context: Optional[dict] = None
) -> None:
    """Output just the prompt for external LLM use."""
    prompt = abduction_prompt(
        observation=observation,
        context=context,
        domain=domain,
        num_hypotheses=num_hypotheses
    )
    print(prompt)


def run_interactive(
    observation: str,
    domain: str,
    num_hypotheses: int,
    format_type: str,
    use_council: bool,
    context: Optional[dict] = None,
    verbose: bool = False
) -> None:
    """Run interactive abduction (requires LLM backend)."""
    # For now, just output the prompt since we don't have a default LLM
    console.print(Panel(
        "[yellow]No LLM backend configured.[/yellow]\n\n"
        "Peircean Abduction works in two modes:\n\n"
        "1. [bold]Prompt Mode[/bold]: Generate prompts for your own LLM\n"
        "   Use: peircean --prompt \"observation\"\n\n"
        "2. [bold]MCP Server[/bold]: Integrate with Claude Desktop\n"
        "   Use: peircean-setup-mcp --write\n\n"
        "Outputting prompt for your observation:",
        title="Peircean Abduction"
    ))
    
    prompt = abduction_prompt(
        observation=observation,
        context=context,
        domain=domain,
        num_hypotheses=num_hypotheses
    )
    
    if format_type == "json":
        output = {
            "observation": observation,
            "domain": domain,
            "prompt": prompt
        }
        print(json.dumps(output, indent=2))
    else:
        console.print(Markdown(f"```\n{prompt}\n```"))


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
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
            context=context
        )
    else:
        run_interactive(
            observation=args.observation,
            domain=args.domain,
            num_hypotheses=args.num_hypotheses,
            format_type=args.format,
            use_council=args.council,
            context=context,
            verbose=args.verbose
        )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
