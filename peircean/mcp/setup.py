"""
Peircean Abduction: MCP Setup Utility

Automatically configures MCP hosts (Claude Desktop, Cursor) to use the
Peircean Abduction server.

Usage:
    peircean-setup-mcp --write ~/.claude_desktop_config.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def get_default_config_path() -> Path:
    """Get the default Claude Desktop config path for the current OS."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "claude" / "claude_desktop_config.json"


def get_mcp_config() -> dict[str, Any]:
    """Get the MCP configuration for Peircean Logic Harness."""
    return {
        "mcpServers": {
            "peircean": {
                "command": "python",
                "args": ["-m", "peircean.mcp.server"]
            }
        }
    }


def merge_configs(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Merge new config into existing, preserving other servers."""
    result = existing.copy()

    if "mcpServers" not in result:
        result["mcpServers"] = {}

    # Add/update our server
    result["mcpServers"]["peircean"] = new["mcpServers"]["peircean"]

    return result


def setup_mcp(
    config_path: Path | None = None,
    write: bool = False,
    backup: bool = True
) -> str:
    """
    Setup MCP configuration.
    
    Args:
        config_path: Path to config file (None for default)
        write: Actually write the file (False = dry run)
        backup: Create backup before modifying
        
    Returns:
        The configuration JSON string
    """
    path = config_path or get_default_config_path()
    new_config = get_mcp_config()
    
    # Check for existing config
    if path.exists():
        with open(path) as f:
            existing = json.load(f)
        final_config = merge_configs(existing, new_config)
    else:
        final_config = new_config
    
    config_json = json.dumps(final_config, indent=2)
    
    if write:
        # Create backup
        if backup and path.exists():
            backup_path = path.with_suffix(".json.bak")
            shutil.copy(path, backup_path)
            print(f"Created backup: {backup_path}")
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config
        with open(path, "w") as f:
            f.write(config_json)
        
        print(f"Wrote configuration to: {path}")
    
    return config_json


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Setup Peircean Abduction MCP server configuration"
    )
    parser.add_argument(
        "--write",
        type=str,
        nargs="?",
        const="default",
        help="Write config to file (optionally specify path)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup of existing config"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output just the JSON config"
    )
    
    args = parser.parse_args()
    
    # Determine config path
    if args.write == "default":
        config_path = get_default_config_path()
    elif args.write:
        config_path = Path(args.write)
    else:
        config_path = None
    
    # Run setup
    config = setup_mcp(
        config_path=config_path,
        write=bool(args.write),
        backup=not args.no_backup
    )
    
    # Output
    if args.json or not args.write:
        print(config)
    
    if not args.write:
        print("\n# To apply this configuration, run:")
        print(f"#   peircean-setup-mcp --write {get_default_config_path()}")


if __name__ == "__main__":
    main()
