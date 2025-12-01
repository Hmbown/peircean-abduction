"""
Peircean Abduction: Command Line Interface

Usage:
    peircean "The stock dropped 5% on good news"
    peircean --domain financial "Market anomaly observed"
    peircean --format json "System behavior unexpected"
    peircean config show
    peircean config validate
"""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import get_config
from .core import abduction_prompt
from .providers import get_provider_registry
from .utils.env import validate_environment

# Import wizard components inline to avoid circular import issues
try:
    from .wizard.config_wizard import run_config_wizard

    CONFIG_WIZARD_AVAILABLE = True
except ImportError:
    CONFIG_WIZARD_AVAILABLE = False

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

Configuration:
  peircean config show          Show current configuration
  peircean config validate      Validate configuration
  peircean config providers     List available providers
  peircean config wizard        Interactive configuration setup
        """,
    )

    # Primary argument - the observation to analyze
    parser.add_argument(
        "observation", nargs="?", help="The surprising fact or anomalous observation to explain"
    )

    # Configuration commands (when no observation provided)
    parser.add_argument(
        "config_action",
        nargs="?",
        choices=["show", "validate", "providers", "wizard"],
        help="Configuration action (use without observation)",
    )

    # Management Commands
    parser.add_argument(
        "--install", action="store_true", help="Install MCP server to Claude Desktop config"
    )
    parser.add_argument("--verify", action="store_true", help="Verify installation and environment")

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

    parser.add_argument("--version", action="version", version="peircean-abduction 1.2.3")

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
    """Run interactive abduction with optional LLM integration."""
    config = get_config()

    # Default to prompt-only mode like Hegelion
    if not config.interactive_mode:
        console.print(
            Panel(
                f"[blue]🤔 Peircean Abduction - Prompt Mode[/blue]\n\n"
                f"[bold]Provider:[/bold] {config.provider.value} ({config.model})\n"
                f"[bold]Council of Critics:[/bold] {'✅ Enabled' if use_council else '❌ Disabled'}\n\n"
                "[yellow]Interactive mode is disabled (default behavior like Hegelion)[/yellow]\n\n"
                "To use Peircean Abduction:\n\n"
                "1. [bold]Via Claude Desktop / Cursor (Recommended)[/bold]\n"
                "   Run: [green]peircean --install[/green]\n"
                "   Then restart Claude and use the tools directly in chat.\n\n"
                "2. [bold]Via CLI Prompt[/bold]\n"
                '   Use: [blue]peircean --prompt "your observation"[/blue]\n'
                "   (Copy the output into any LLM)\n\n"
                "3. [bold]Enable Interactive Mode[/bold]\n"
                "   Run: [green]peircean config wizard[/green]\n"
                "   Or set: PEIRCEAN_INTERACTIVE_MODE=true\n\n"
                "Outputting prompt for your observation below:",
                title="Peircean Abduction",
            )
        )

        prompt = abduction_prompt(
            observation=observation, context=context, domain=domain, num_hypotheses=num_hypotheses
        )

        if format_type == "json":
            output = {
                "observation": observation,
                "domain": domain,
                "num_hypotheses": num_hypotheses,
                "use_council": use_council,
                "prompt": prompt,
            }
            print(json.dumps(output, indent=2))
        else:
            console.print(Markdown(f"```\n{prompt}\n```"))
        return

    # Interactive mode with actual LLM calls
    console.print(
        Panel(
            f"[green]🚀 Peircean Abduction - Interactive Mode[/green]\n\n"
            f"[bold]Provider:[/bold] {config.provider.value} ({config.model})\n"
            f"[bold]Council of Critics:[/bold] {'✅ Enabled' if use_council else '❌ Disabled'}\n\n"
            "[blue]Generating abductive reasoning...[/blue]",
            title="Peircean Abduction",
        )
    )

    try:
        # Get provider client
        from .providers import get_provider_client

        provider_client = get_provider_client(config.provider.value, config.get_provider_config())

        if not provider_client or not provider_client.is_available():
            console.print("[red]❌ Provider not available. Falling back to prompt mode.[/red]")
            # Fall back to prompt mode
            prompt = abduction_prompt(
                observation=observation,
                context=context,
                domain=domain,
                num_hypotheses=num_hypotheses,
            )
            console.print(Markdown(f"```\n{prompt}\n```"))
            return

        # Generate prompt
        prompt = provider_client.generate_prompt(
            observation=observation,
            domain=domain,
            num_hypotheses=num_hypotheses,
            context=context,
            use_council=use_council,
        )

        # Generate completion
        completion = provider_client.generate_completion(
            prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        if completion:
            if format_type == "json":
                output = {
                    "observation": observation,
                    "domain": domain,
                    "num_hypotheses": num_hypotheses,
                    "use_council": use_council,
                    "provider": config.provider.value,
                    "model": config.model,
                    "result": completion,
                }
                print(json.dumps(output, indent=2))
            else:
                console.print("[bold]📋 Abductive Analysis Result:[/bold]")
                console.print(Markdown(completion))
        else:
            console.print(
                "[red]❌ Failed to generate completion. Falling back to prompt mode.[/red]"
            )
            console.print(Markdown(f"```\n{prompt}\n```"))

    except Exception as e:
        console.print(f"[red]❌ Error in interactive mode: {e}[/red]")
        console.print("[yellow]Falling back to prompt mode:[/yellow]")
        prompt = abduction_prompt(
            observation=observation, context=context, domain=domain, num_hypotheses=num_hypotheses
        )
        console.print(Markdown(f"```\n{prompt}\n```"))


def cmd_config_show() -> int:
    """Show current configuration."""
    config = get_config()

    console.print(Panel("[bold blue]Current Configuration[/bold blue]"))

    # Create a rich table for configuration display
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan", width=25)
    table.add_column("Value", style="white")

    config_dict = config.to_dict()
    for key, value in config_dict.items():
        if key == "api_key_set":
            value = "✅ Set" if value else "❌ Not set"
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)

    # Show provider-specific info
    registry = get_provider_registry()
    provider_info = registry.get_provider_info(config.provider.value)
    if provider_info:
        console.print(f"\n[bold]Provider:[/bold] {provider_info.display_name}")
        console.print(f"[dim]{provider_info.description}[/dim]")
        if provider_info.examples:
            console.print(f"[bold]Examples:[/bold] {', '.join(provider_info.examples[:3])}")

    return 0


def cmd_config_validate() -> int:
    """Validate configuration."""
    config = get_config()

    console.print("[bold blue]Peircean Abduction CLI v1.2.3[/bold blue]")

    # Validate general configuration
    issues = config.validate_config()

    if not issues:
        console.print("[green]✅ Configuration is valid![/green]")
    else:
        console.print("[red]❌ Configuration issues found:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")

    # Validate environment
    env_validation = validate_environment()
    if not env_validation["valid"]:
        console.print("\n[red]❌ Environment validation failed:[/red]")
        for issue in env_validation["issues"]:
            console.print(f"  • {issue}")

    if env_validation["warnings"]:
        console.print("\n[yellow]⚠️  Warnings:[/yellow]")
        for warning in env_validation["warnings"]:
            console.print(f"  • {warning}")

    if env_validation["loaded_env_file"]:
        console.print(f"\n[green]✅ Loaded .env file:[/green] {env_validation['loaded_env_file']}")

    return 0 if not issues else 1


def cmd_config_providers() -> int:
    """List available providers."""
    registry = get_provider_registry()
    providers = registry.get_available_providers()

    console.print(Panel("[bold blue]Available Providers[/bold blue]"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan", width=15)
    table.add_column("Display Name", style="white", width=20)
    table.add_column("Description", style="dim", width=40)
    table.add_column("Status", style="green", width=10)

    for provider_name in providers:
        provider_info = registry.get_provider_info(provider_name)
        if provider_info:
            # Check if provider is available
            provider_config = get_config().get_provider_config()
            provider_instance = registry.create_provider(provider_name, provider_config)
            available = (
                "✅ Available"
                if provider_instance and provider_instance.is_available()
                else "⚠️ Config needed"
            )

            table.add_row(
                provider_name, provider_info.display_name, provider_info.description, available
            )

    console.print(table)

    # Show current provider
    current_config = get_config()
    console.print(f"\n[bold]Current Provider:[/bold] {current_config.provider.value}")

    return 0


def cmd_config_wizard() -> int:
    """Interactive configuration wizard."""
    if not CONFIG_WIZARD_AVAILABLE:
        console.print("[red]❌ Configuration wizard not available[/red]")
        console.print("Please install the optional dependencies for the wizard.")
        return 1
    return run_config_wizard()


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle Configuration Commands
    # Special case: if observation is "config" and we have a config_action, treat it as config command
    if args.observation == "config" and args.config_action:
        if args.config_action == "show":
            return cmd_config_show()
        elif args.config_action == "validate":
            return cmd_config_validate()
        elif args.config_action == "providers":
            return cmd_config_providers()
        elif args.config_action == "wizard":
            return cmd_config_wizard()

    # Handle explicit config action (if observation was somehow skipped or empty)
    if not args.observation and args.config_action:
        if args.config_action == "show":
            return cmd_config_show()
        elif args.config_action == "validate":
            return cmd_config_validate()
        elif args.config_action == "providers":
            return cmd_config_providers()
        elif args.config_action == "wizard":
            return cmd_config_wizard()
        else:
            parser.print_help()
            return 1

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
    if not args.observation and not args.config_action:
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
