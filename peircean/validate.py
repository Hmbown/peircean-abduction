"""
Peircean Abduction: Installation & Configuration Validator

Enhanced validator with provider-agnostic configuration support:

1. Python version compatibility
2. Core and optional dependencies
3. Provider availability and connectivity
4. Configuration validation
5. MCP Server functionality
6. Environment setup
7. IDE integration status
"""

from __future__ import annotations

import importlib.util
import json
import sys
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

try:
    from .config import get_config, reload_config
    from .providers import get_provider_registry
    from .utils.env import validate_environment
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

console = Console()


def check_python_version() -> bool:
    """Check if Python version is 3.10+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        console.print(f"[red]❌ Python 3.10+ required (found {sys.version.split()[0]})[/red]")
        return False
    console.print(f"[green]✅ Python {version.major}.{version.minor} detected[/green]")
    return True


def check_dependencies() -> None:
    """Check optional dependencies."""
    dependencies = ["anthropic", "openai", "mcp"]

    for dep in dependencies:
        if importlib.util.find_spec(dep):
            console.print(f"[green]✅ Optional dependency '{dep}' found[/green]")
        else:
            console.print(
                f"[yellow]⚠️  Optional dependency '{dep}' not found "
                "(some features may be limited)[/yellow]"
            )


def check_mcp_server() -> bool:
    """Check if MCP server can be loaded."""
    try:
        from peircean.mcp.server import mcp

        # Try to access tools (handling FastMCP implementation details)
        tools = []
        if hasattr(mcp, "_tools"):
            tools = list(mcp._tools.keys())
        elif hasattr(mcp, "tools"):
            tools = list(mcp.tools.keys())

        required_tools = [
            "peircean_observe_anomaly",
            "peircean_generate_hypotheses",
            "peircean_evaluate_via_ibe",
        ]

        missing = [t for t in required_tools if t not in tools]

        if not missing:
            console.print(
                f"[green]✅ MCP Server loads correctly ({len(tools)} tools registered)[/green]"
            )
            return True
        else:
            console.print(f"[red]❌ MCP Server missing required tools: {missing}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]❌ Failed to load MCP server: {e}[/red]")
        return False


def check_claude_config() -> None:
    """Check Claude Desktop configuration."""
    # Import dynamically to avoid circular imports or path issues
    try:
        from peircean.mcp.setup import get_default_config_path

        config_path = get_default_config_path()

        if not config_path.exists():
            console.print(
                "[yellow]⚠️  Claude Desktop config not found (normal if not installed)[/yellow]"
            )
            return

        try:
            with open(config_path) as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})
            if "peircean" in servers:
                cmd = servers["peircean"].get("command", "")
                args = servers["peircean"].get("args", [])

                console.print("[green]✅ Found 'peircean' in Claude config[/green]")
                console.print(f"   Command: [dim]{cmd} {' '.join(args)}[/dim]")

                # Verify python path matches current env
                if cmd != sys.executable:
                    console.print(
                        "[yellow]⚠️  Config uses different Python interpreter than current env[/yellow]"
                    )
                    console.print(f"   Config:  {cmd}")
                    console.print(f"   Current: {sys.executable}")
            else:
                console.print("[yellow]⚠️  'peircean' not found in Claude config[/yellow]")
                console.print("[blue]   Run 'peircean install' to configure[/blue]")

        except json.JSONDecodeError:
            console.print("[red]❌ Claude config file is invalid JSON[/red]")

    except ImportError:
        pass


def check_enhanced_dependencies() -> Dict[str, bool]:
    """Check core and optional dependencies with detailed status."""
    results = {}

    # Core dependencies (required)
    core_deps = ["pydantic", "httpx", "tenacity", "rich"]
    console.print("\n[bold]Core Dependencies:[/bold]")

    for dep in core_deps:
        if importlib.util.find_spec(dep):
            console.print(f"  [green]✅ {dep}[/green]")
            results[dep] = True
        else:
            console.print(f"  [red]❌ {dep} (required)[/red]")
            results[dep] = False

    # Optional dependencies by provider
    console.print("\n[bold]Provider Dependencies:[/bold]")
    provider_deps = {
        "anthropic": ["anthropic"],
        "openai": ["openai"],
        "gemini": ["google-generativeai"],
        "ollama": ["ollama"],
        "environment": ["python-dotenv"],
        "mcp": ["mcp"],
    }

    for provider, deps in provider_deps.items():
        all_found = True
        for dep in deps:
            if importlib.util.find_spec(dep):
                console.print(f"  [green]✅ {dep} ({provider})[/green]")
            else:
                console.print(f"  [yellow]⚠️  {dep} ({provider}) - optional[/yellow]")
                all_found = False

        results[f"{provider}_deps"] = all_found

    return results


def check_provider_configuration() -> Dict[str, Any]:
    """Check provider configuration and availability."""
    if not CONFIG_AVAILABLE:
        console.print("\n[yellow]⚠️  Configuration system not available[/yellow]")
        return {"available": False}

    console.print("\n[bold]Provider Configuration:[/bold]")

    try:
        config = get_config()
        registry = get_provider_registry()

        # Check current provider
        current_provider = config.provider.value
        console.print(f"  Current provider: [cyan]{current_provider}[/cyan]")

        # Validate current provider configuration
        issues = config.validate_config()
        if issues:
            console.print("  [red]❌ Configuration issues:[/red]")
            for issue in issues:
                console.print(f"    • {issue}")
        else:
            console.print("  [green]✅ Configuration valid[/green]")

        # Check provider availability
        provider_config = config.get_provider_config()
        provider_client = registry.create_provider(current_provider, provider_config)

        if provider_client and provider_client.is_available():
            console.print("  [green]✅ Provider client available[/green]")
            available = True
        else:
            console.print("  [yellow]⚠️  Provider client not available (API key or connectivity issue)[/yellow]")
            available = False

        # Check all providers
        console.print("\n[bold]All Providers Status:[/bold]")
        table = Table()
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("API Key", style="yellow")

        for provider_name in registry.get_available_providers():
            provider_info = registry.get_provider_info(provider_name)
            if provider_info:
                # Check if API key is available
                has_key = bool(provider_info.env_api_key and
                              (importlib.util.find_spec(provider_info.dependency_name) if provider_info.dependency_name else True))

                status = "✅ Available" if has_key else "⚠️ Config needed"
                key_status = "✅ Set" if has_key else "❌ Missing"

                table.add_row(provider_name, status, key_status)

        console.print(table)

        return {
            "available": available,
            "current_provider": current_provider,
            "config_issues": issues,
            "all_providers": registry.get_available_providers(),
        }

    except Exception as e:
        console.print(f"  [red]❌ Error checking provider configuration: {e}[/red]")
        return {"available": False, "error": str(e)}


def check_environment_setup() -> Dict[str, Any]:
    """Check environment configuration and .env file."""
    if not CONFIG_AVAILABLE:
        console.print("\n[yellow]⚠️  Environment validation not available[/yellow]")
        return {"available": False}

    console.print("\n[bold]Environment Setup:[/bold]")

    try:
        env_validation = validate_environment()

        if env_validation["loaded_env_file"]:
            console.print(f"  [green]✅ .env file loaded: {env_validation['loaded_env_file']}[/green]")
        else:
            console.print("  [yellow]⚠️  No .env file found[/yellow]")

        if env_validation["environment_variables"]:
            console.print("  [green]✅ Environment variables found:[/green]")
            for var, value in env_validation["environment_variables"].items():
                console.print(f"    {var}: {value}")

        if env_validation["valid"]:
            console.print("  [green]✅ Environment configuration valid[/green]")
        else:
            console.print("  [red]❌ Environment configuration issues:[/red]")
            for issue in env_validation["issues"]:
                console.print(f"    • {issue}")

        if env_validation["warnings"]:
            console.print("  [yellow]⚠️  Warnings:[/yellow]")
            for warning in env_validation["warnings"]:
                console.print(f"    • {warning}")

        return env_validation

    except Exception as e:
        console.print(f"  [red]❌ Error checking environment: {e}[/red]")
        return {"available": False, "error": str(e)}


def check_ide_integrations() -> Dict[str, bool]:
    """Check IDE integration status."""
    console.print("\n[bold]IDE Integration Status:[/bold]")

    results = {}

    # Claude Desktop
    try:
        from peircean.mcp.setup import get_default_config_path
        config_path = get_default_config_path()

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            servers = config.get("mcpServers", {})
            if "peircean" in servers:
                console.print("  [green]✅ Claude Desktop configured[/green]")
                results["claude_desktop"] = True
            else:
                console.print("  [yellow]⚠️  Claude Desktop: peircean not configured[/yellow]")
                results["claude_desktop"] = False
        else:
            console.print("  [yellow]⚠️  Claude Desktop: config file not found[/yellow]")
            results["claude_desktop"] = False
    except Exception:
        console.print("  [red]❌ Claude Desktop: error checking config[/red]")
        results["claude_desktop"] = False

    # Cursor (checks same config as Claude Desktop)
    # Note: Cursor uses the same MCP configuration as Claude Desktop
    if results.get("claude_desktop"):
        console.print("  [green]✅ Cursor: should work with Claude Desktop config[/green]")
        results["cursor"] = True
    else:
        console.print("  [yellow]⚠️  Cursor: requires MCP configuration[/yellow]")
        results["cursor"] = False

    # VS Code (Continue.dev)
    # This would require checking VS Code settings, which is more complex
    console.print("  [blue]ℹ️  VS Code: manual configuration required for Continue.dev[/blue]")
    results["vscode"] = "manual"

    return results


def main() -> int:
    console.print(Panel("[bold blue]🔍 Peircean Abduction Enhanced System Check[/bold blue]"))

    all_passed = True
    results = {}

    with Status("Performing comprehensive system check...", spinner="dots"):
        # Basic checks
        if not check_python_version():
            all_passed = False
            results["python"] = False

        # Enhanced dependency check
        dep_results = check_enhanced_dependencies()
        results["dependencies"] = dep_results

        # MCP server check
        if not check_mcp_server():
            all_passed = False
            results["mcp_server"] = False
        else:
            results["mcp_server"] = True

        # Enhanced checks
        provider_results = check_provider_configuration()
        results["provider"] = provider_results

        env_results = check_environment_setup()
        results["environment"] = env_results

        ide_results = check_ide_integrations()
        results["ide"] = ide_results

        # Original IDE check for backward compatibility
        check_claude_config()

    # Summary
    console.print("\n" + "="*50)
    console.print("[bold]📊 System Check Summary[/bold]")
    console.print("="*50)

    # Core requirements status
    core_ok = (
        results.get("python", False) and
        results.get("mcp_server", False) and
        all(results.get(k, True) for k in ["pydantic", "httpx", "tenacity", "rich"] if k in results.get("dependencies", {}))
    )

    if core_ok:
        console.print("[green]✅ Core requirements satisfied[/green]")
    else:
        console.print("[red]❌ Core requirements missing[/red]")
        all_passed = False

    # Provider status
    if provider_results.get("available", False):
        console.print("[green]✅ Provider configuration working[/green]")
    else:
        console.print("[yellow]⚠️  Provider configuration needs setup[/yellow]")

    # Environment status
    if env_results.get("valid", False):
        console.print("[green]✅ Environment configuration valid[/green]")
    else:
        console.print("[yellow]⚠️  Environment configuration has issues[/yellow]")

    # IDE integration status
    ide_count = sum(1 for v in ide_results.values() if v is True)
    if ide_count > 0:
        console.print(f"[green]✅ {ide_count} IDE(s) configured[/green]")
    else:
        console.print("[yellow]⚠️  No IDEs configured (run 'peircean --install')[/yellow]")

    # Final verdict
    console.print("\n" + "="*50)
    if all_passed and core_ok:
        console.print("[bold green]🎉 System ready for Abduction! 🎉[/bold green]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("• [blue]peircean config show[/blue] - View configuration")
        console.print("• [blue]peircean config wizard[/blue] - Interactive setup")
        console.print("• [blue]peircean 'your observation'[/blue] - Start analyzing")
        return 0
    else:
        console.print("[bold red]❌ System check failed. Please review errors above.[/bold red]")
        console.print("\n[dim]Recommended fixes:[/dim]")
        if not results.get("python", False):
            console.print("• Upgrade to Python 3.10+")
        if not results.get("mcp_server", False):
            console.print("• Install MCP dependencies: [blue]pip install mcp[/blue]")
        if not dep_results.get("pydantic", False):
            console.print("• Install missing dependencies: [blue]pip install -e .[/blue]")
        if not provider_results.get("available", False):
            console.print("• Configure provider: [blue]peircean config wizard[/blue]")
        if ide_count == 0:
            console.print("• Setup IDE integration: [blue]peircean --install[/blue]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
