"""
Peircean Abduction: Interactive Configuration Wizard

Guides users through setting up their peircean-abduction configuration
with interactive prompts, validation, and helpful suggestions.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..config import Provider
from ..providers import get_provider_registry
from ..utils.env import detect_provider_from_env

RICH_AVAILABLE = True


def rich_print(text: str, style: str = "") -> None:
    """Fallback print function when Rich is not available."""
    if RICH_AVAILABLE and Console:
        assert Console is not None
        console = Console()
        console.print(text, style=style)
    else:
        print(text)


def rich_prompt(
    message: str, choices: list | None = None, default: str | None = None, password: bool = False
) -> str:
    """Fallback prompt function when Rich is not available."""
    if RICH_AVAILABLE and Prompt:
        prompt = Prompt()
        if choices:
            return prompt.ask(message, choices=choices, default=default or "", password=password)
        else:
            return prompt.ask(message, default=default or "", password=password)
    else:
        if choices:
            choice_str = "/".join(choices)
            if default:
                message += f" [{choice_str}] ({default})"
            else:
                message += f" [{choice_str}]"
        elif default:
            message += f" ({default})"

        while True:
            response = input(f"{message}: ").strip()
            if not response and default:
                return default
            if choices and response in choices:
                return response
            if not choices:
                return response
            print(f"Please choose from: {', '.join(choices)}")


def rich_confirm(message: str, default: bool = False) -> bool:
    """Fallback confirm function when Rich is not available."""
    if RICH_AVAILABLE and Confirm:
        confirm = Confirm()
        return confirm.ask(message, default=default)
    else:
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{message} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ["y", "yes"]:
                return True
            if response in ["n", "no"]:
                return False
            print("Please answer 'y' or 'n'")


def welcome_message() -> None:
    """Display welcome message."""
    if RICH_AVAILABLE and Panel and Console:
        assert Console is not None
        console = Console()
        console.print(
            Panel(
                "[bold blue]🔮 Peircean Abduction Configuration Wizard[/bold blue]\n\n"
                "This wizard will help you configure your Peircean Abduction setup.\n"
                "You'll be able to choose your LLM provider, set up API keys,\n"
                "and configure optional features like interactive mode.\n\n"
                "[dim]You can press Ctrl+C to exit at any time.[/dim]",
                title="Welcome",
                border_style="blue",
            )
        )
    else:
        print("\n" + "=" * 60)
        print("🔮 Peircean Abduction Configuration Wizard")
        print("=" * 60)
        print("\nThis wizard will help you configure your Peircean Abduction setup.")
        print("You'll be able to choose your LLM provider, set up API keys,")
        print("and configure optional features like interactive mode.")
        print("\nYou can press Ctrl+C to exit at any time.\n")


def select_provider() -> Provider:
    """Guide user through provider selection."""
    rich_print("\n[bold]🤖 LLM Provider Selection[/bold]")

    # Show available providers
    registry = get_provider_registry()
    providers = registry.get_available_providers()

    if RICH_AVAILABLE and Table and Console:
        assert Console is not None
        console = Console()
        table = Table(title="Available Providers")
        table.add_column("Choice", style="cyan", width=8)
        table.add_column("Provider", style="white", width=15)
        table.add_column("Description", style="dim", width=40)

        for i, provider_name in enumerate(providers, 1):
            provider_info = registry.get_provider_info(provider_name)
            if provider_info:
                table.add_row(str(i), provider_name, provider_info.description)

        console.print(table)
    else:
        print("\nAvailable Providers:")
        for i, provider_name in enumerate(providers, 1):
            provider_info = registry.get_provider_info(provider_name)
            if provider_info:
                print(f"  {i}. {provider_name} - {provider_info.description}")

    # Auto-detect if possible
    detected = detect_provider_from_env()
    if detected:
        detected_provider = Provider(detected)
        rich_print(f"\n[green]✅ Detected provider from environment: {detected}[/green]")
        use_detected = rich_confirm(f"Use {detected} as your provider?", default=True)
        if use_detected:
            return detected_provider

    # Manual selection
    choices = [str(i) for i in range(1, len(providers) + 1)]
    choice = rich_prompt("\nSelect your provider (enter number)", choices=choices, default="1")

    selected_index = int(choice) - 1
    selected_provider = providers[selected_index]
    return Provider(selected_provider)


def configure_provider(provider: Provider) -> dict[str, str]:
    """Configure the selected provider."""
    rich_print(f"\n[bold]⚙️  Configure {provider.value.title()} Provider[/bold]")

    config = {}

    if provider == Provider.OLLAMA:
        # Ollama configuration
        host = rich_prompt("Ollama host URL", default="http://localhost:11434")
        config["base_url"] = host

        model = rich_prompt("Ollama model name", default="llama2")
        config["model"] = model

        rich_print("\n[dim]Note: Make sure Ollama is running and the model is pulled![/dim]")

    else:
        # API key based providers
        env_var = f"{provider.value.upper()}_API_KEY"
        rich_print(f"\nYou can set your API key via the {env_var} environment variable.")

        use_env_key = rich_confirm(f"Use {env_var} environment variable?", default=True)

        if not use_env_key:
            api_key = rich_prompt(f"Enter your {provider.value.title()} API key", password=True)
            config["api_key"] = api_key
        else:
            rich_print(f"[green]✅ Will use {env_var} environment variable[/green]")

        # Model selection
        registry = get_provider_registry()
        provider_info = registry.get_provider_info(provider.value)
        if provider_info and provider_info.examples:
            if len(provider_info.examples) == 1:
                selected_model = provider_info.examples[0]
                rich_print(f"[green]✅ Using default model: {selected_model}[/green]")
            else:
                model_choices = provider_info.examples[:3]  # Limit to 3 examples
                rich_print(f"\nAvailable models for {provider.value.title()}:")
                for i, model in enumerate(model_choices, 1):
                    rich_print(f"  {i}. {model}")

                model_choice = rich_prompt(
                    "Select model (enter number)",
                    choices=[str(i) for i in range(1, len(model_choices) + 1)],
                    default="1",
                )
                selected_model = model_choices[int(model_choice) - 1]

            config["model"] = selected_model

    return config


def configure_features() -> dict[str, bool]:
    """Configure optional features."""
    rich_print("\n[bold]🎛️  Optional Features[/bold]")

    features = {}

    # Interactive mode
    rich_print(
        "\n[dim]Interactive mode allows direct LLM API calls instead of just generating prompts.[/dim]"
    )
    rich_print("[dim]This is optional - the default prompt-only mode works like Hegelion.[/dim]")

    interactive = rich_confirm("Enable interactive mode (requires API key)?", default=False)
    features["interactive_mode"] = interactive

    # Council of Critics
    council = rich_confirm("Enable Council of Critics evaluation by default?", default=True)
    features["enable_council"] = council

    # Debug mode
    debug = rich_confirm("Enable debug mode for verbose output?", default=False)
    features["debug_mode"] = debug

    return features


def create_env_file(
    provider: Provider, config: dict[str, str], features: dict[str, bool]
) -> Path | None:
    """Create .env file with user configuration."""
    create_env = rich_confirm("\nCreate .env file with your configuration?", default=True)

    if not create_env:
        return None

    env_path = Path(".env")

    # Check if .env already exists
    if env_path.exists():
        backup = rich_confirm(".env file already exists. Create backup?", default=True)
        if backup:
            backup_path = env_path.with_suffix(".env.backup")
            env_path.rename(backup_path)
            rich_print(f"[green]✅ Created backup: {backup_path}[/green]")

    # Create .env content
    content_lines = [
        "# Peircean Abduction Configuration",
        "# Generated by configuration wizard",
        "",
        "# Provider Selection",
        f"PEIRCEAN_PROVIDER={provider.value}",
        f"PEIRCEAN_MODEL={config.get('model', '')}",
        "",
        "# Feature Toggles",
        f"PEIRCEAN_ENABLE_COUNCIL={'true' if features.get('enable_council', True) else 'false'}",
        f"PEIRCEAN_INTERACTIVE_MODE={'true' if features.get('interactive_mode', False) else 'false'}",
        f"PEIRCEAN_DEBUG_MODE={'true' if features.get('debug_mode', False) else 'false'}",
        "",
        "# Performance",
        "PEIRCEAN_TEMPERATURE=0.7",
        "PEIRCEAN_TIMEOUT_SECONDS=60",
        "PEIRCEAN_MAX_RETRIES=3",
        "",
        "# Default Abduction Settings",
        "PEIRCEAN_DEFAULT_DOMAIN=general",
        "PEIRCEAN_DEFAULT_NUM_HYPOTHESES=5",
        "",
    ]

    # Add provider-specific configuration
    if provider != Provider.OLLAMA and "api_key" in config:
        content_lines.extend(
            [
                "# API Key",
                f"PEIRCEAN_API_KEY={config['api_key']}",
                "",
            ]
        )

    if config.get("base_url"):
        content_lines.extend(
            [
                "# Base URL",
                f"PEIRCEAN_BASE_URL={config['base_url']}",
                "",
            ]
        )

    if provider == Provider.OLLAMA:
        content_lines.extend(
            [
                "# Ollama Configuration",
                f"OLLAMA_HOST={config.get('base_url', 'http://localhost:11434')}",
                "",
            ]
        )

    # Write .env file
    try:
        with open(env_path, "w") as f:
            f.write("\n".join(content_lines))

        rich_print(f"[green]✅ Created .env file at {env_path.absolute()}[/green]")
        return env_path
    except Exception as e:
        rich_print(f"[red]❌ Failed to create .env file: {e}[/red]")
        return None


def setup_ide_integration() -> bool:
    """Offer to set up IDE integration."""
    rich_print("\n[bold]🔗 IDE Integration[/bold]")
    rich_print("Peircean Abduction works best with IDE integration via MCP.")

    setup_ide = rich_confirm("Set up Claude Desktop/Cursor integration now?", default=True)

    if setup_ide:
        try:
            from ..mcp.setup import main as setup_main

            rich_print("\n[blue]Setting up MCP integration...[/blue]")
            setup_main(["--write"])
            return True
        except Exception as e:
            rich_print(f"[red]❌ Failed to set up IDE integration: {e}[/red]")
            rich_print("[yellow]You can run 'peircean --install' later to set this up.[/yellow]")
            return False

    return False


def completion_summary(env_file: Path | None, ide_setup: bool) -> None:
    """Display completion summary."""
    if RICH_AVAILABLE and Panel and Console:
        assert Console is not None
        console = Console()
        console.print(
            Panel(
                "[bold green]✨ Configuration Complete! ✨[/bold green]\n\n"
                "Your Peircean Abduction setup is ready to use.\n\n"
                "[bold]Next steps:[/bold]\n"
                "• peircean config show     - View your configuration\n"
                "• peircean --verify        - Verify your setup\n"
                "• peircean 'observation'   - Start analyzing\n"
                "\n[dim]Thank you for using Peircean Abduction! 🚀[/dim]",
                title="Setup Complete",
                border_style="green",
            )
        )
    else:
        print("\n" + "=" * 60)
        print("✨ Configuration Complete! ✨")
        print("=" * 60)
        print("\nYour Peircean Abduction setup is ready to use.")
        print("\nNext steps:")
        print("• peircean config show     - View your configuration")
        print("• peircean --verify        - Verify your setup")
        print("• peircean 'observation'   - Start analyzing")
        print("\nThank you for using Peircean Abduction! 🚀")

    if env_file:
        rich_print(f"\n[dim]Configuration saved to: {env_file.absolute()}[/dim]")

    if ide_setup:
        rich_print("\n[dim]IDE integration configured successfully[/dim]")
    else:
        rich_print("\n[dim]Run 'peircean --install' to set up IDE integration[/dim]")


def run_config_wizard() -> int:
    """Run the interactive configuration wizard."""
    try:
        # Welcome
        welcome_message()

        # Provider selection
        provider = select_provider()

        # Provider configuration
        provider_config = configure_provider(provider)

        # Feature configuration
        features = configure_features()

        # Create .env file
        env_file = create_env_file(provider, provider_config, features)

        # IDE integration setup
        ide_setup = setup_ide_integration()

        # Completion summary
        completion_summary(env_file, ide_setup)

        return 0

    except KeyboardInterrupt:
        rich_print("\n[yellow]⚠️  Configuration cancelled by user[/yellow]")
        return 1
    except Exception as e:
        rich_print(f"\n[red]❌ Configuration wizard failed: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(run_config_wizard())
