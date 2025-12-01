"""
Peircean Abduction: Installation & Configuration Validator

Checks:
1. Python version
2. Dependencies
3. MCP Server Importability
4. Tool Registration
5. Claude Desktop Config (optional)
"""

from __future__ import annotations

import importlib.util
import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.status import Status

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


def main() -> int:
    console.print(Panel("[bold blue]Peircean Abduction Environment Check[/bold blue]"))

    all_passed = True

    with Status("Checking system...", spinner="dots"):
        if not check_python_version():
            all_passed = False

        check_dependencies()

        if not check_mcp_server():
            all_passed = False

        check_claude_config()

    if all_passed:
        console.print("\n[bold green]✨ System ready for Abduction! ✨[/bold green]")
        return 0
    else:
        console.print("\n[bold red]System check failed. Please review errors above.[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
