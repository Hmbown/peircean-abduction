"""
Tests for Peircean MCP Setup Utility.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from peircean.mcp.setup import (
    get_default_config_path,
    get_mcp_config,
    main,
    merge_configs,
    setup_mcp,
)


class TestGetDefaultConfigPath:
    """Test config path detection for different platforms."""

    def test_macos_path(self):
        with patch.object(sys, "platform", "darwin"):
            path = get_default_config_path()
            assert "Library" in str(path)
            assert "Application Support" in str(path)
            assert "Claude" in str(path)
            assert path.name == "claude_desktop_config.json"

    def test_windows_path(self):
        with patch.object(sys, "platform", "win32"):
            with patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
                path = get_default_config_path()
                assert "Claude" in str(path)
                assert path.name == "claude_desktop_config.json"

    def test_linux_path(self):
        with patch.object(sys, "platform", "linux"):
            path = get_default_config_path()
            assert ".config" in str(path)
            assert "claude" in str(path)
            assert path.name == "claude_desktop_config.json"


class TestGetMcpConfig:
    """Test MCP configuration generation."""

    def test_config_structure(self):
        config = get_mcp_config()
        assert "mcpServers" in config
        assert "peircean" in config["mcpServers"]
        assert "command" in config["mcpServers"]["peircean"]
        assert config["mcpServers"]["peircean"]["command"] == "python"
        assert "-m" in config["mcpServers"]["peircean"]["args"]
        assert "peircean.mcp.server" in config["mcpServers"]["peircean"]["args"]


class TestMergeConfigs:
    """Test configuration merging logic."""

    def test_merge_empty_existing(self):
        existing = {}
        new = get_mcp_config()
        result = merge_configs(existing, new)
        assert "mcpServers" in result
        assert "peircean" in result["mcpServers"]

    def test_merge_preserves_other_servers(self):
        existing = {
            "mcpServers": {
                "other-server": {"command": "node", "args": ["server.js"]},
            }
        }
        new = get_mcp_config()
        result = merge_configs(existing, new)
        assert "other-server" in result["mcpServers"]
        assert "peircean" in result["mcpServers"]

    def test_merge_updates_existing_peircean(self):
        existing = {
            "mcpServers": {
                "peircean": {"command": "old-command", "args": []},
            }
        }
        new = get_mcp_config()
        result = merge_configs(existing, new)
        assert result["mcpServers"]["peircean"]["command"] == "python"

    def test_merge_preserves_other_top_level_keys(self):
        existing = {
            "someOtherSetting": True,
            "mcpServers": {},
        }
        new = get_mcp_config()
        result = merge_configs(existing, new)
        assert result["someOtherSetting"] is True


class TestSetupMcp:
    """Test setup_mcp function."""

    def test_dry_run_new_config(self, tmp_path: Path):
        config_path = tmp_path / "new_config.json"
        result = setup_mcp(config_path=config_path, write=False)

        # Should return config JSON
        config = json.loads(result)
        assert "mcpServers" in config
        assert "peircean" in config["mcpServers"]

        # Should not have written file
        assert not config_path.exists()

    def test_write_new_config(self, tmp_path: Path):
        config_path = tmp_path / "new_config.json"
        result = setup_mcp(config_path=config_path, write=True)

        # Should have written file
        assert config_path.exists()

        # File contents should match result
        with open(config_path) as f:
            written = f.read()
        assert json.loads(written) == json.loads(result)

    def test_write_creates_parent_directories(self, tmp_path: Path):
        config_path = tmp_path / "nested" / "dir" / "config.json"
        setup_mcp(config_path=config_path, write=True)

        assert config_path.exists()

    def test_merge_existing_config(self, tmp_path: Path):
        config_path = tmp_path / "existing_config.json"
        existing_config = {"mcpServers": {"other": {"command": "test"}}}
        with open(config_path, "w") as f:
            json.dump(existing_config, f)

        result = setup_mcp(config_path=config_path, write=True)

        config = json.loads(result)
        assert "other" in config["mcpServers"]
        assert "peircean" in config["mcpServers"]

    def test_backup_created(self, tmp_path: Path):
        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump({"old": "config"}, f)

        setup_mcp(config_path=config_path, write=True, backup=True)

        backup_path = config_path.with_suffix(".json.bak")
        assert backup_path.exists()

        with open(backup_path) as f:
            backup_content = json.load(f)
        assert backup_content == {"old": "config"}

    def test_no_backup_when_disabled(self, tmp_path: Path):
        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump({"old": "config"}, f)

        setup_mcp(config_path=config_path, write=True, backup=False)

        backup_path = config_path.with_suffix(".json.bak")
        assert not backup_path.exists()

    def test_default_path_used_when_none(self):
        mock_path = MagicMock()
        mock_path.return_value = Path("/fake/path/config.json")
        # Dry run so we don't actually write
        setup_mcp(config_path=None, write=False, _get_path=mock_path)
        mock_path.assert_called_once()


class TestMain:
    """Test CLI entry point."""

    def test_dry_run_output(self, capsys):
        main(args_list=[])

        captured = capsys.readouterr()
        # Should output JSON config
        assert "mcpServers" in captured.out
        # Should suggest how to apply
        assert "peircean-setup-mcp --write" in captured.out

    def test_json_flag(self, capsys):
        main(args_list=["--json"])

        captured = capsys.readouterr()
        # With --json flag (but no --write), output includes JSON and help text
        # The JSON is formatted across multiple lines, so we need to extract it
        output = captured.out.strip()
        # Find the JSON portion (starts with { and ends with })
        json_start = output.find("{")
        json_end = output.rfind("}") + 1
        json_str = output[json_start:json_end]
        config = json.loads(json_str)
        assert "mcpServers" in config

    def test_write_to_default_location(self, tmp_path: Path, capsys):
        config_path = tmp_path / "claude" / "config.json"
        mock_path = MagicMock(return_value=config_path)

        main(args_list=["--write"], _get_path=mock_path)

        assert config_path.exists()
        captured = capsys.readouterr()
        assert "Wrote configuration" in captured.out

    def test_write_to_custom_path(self, tmp_path: Path, capsys):
        config_path = tmp_path / "custom_config.json"

        main(args_list=["--write", str(config_path)])

        assert config_path.exists()
        captured = capsys.readouterr()
        assert "Wrote configuration" in captured.out

    def test_no_backup_flag(self, tmp_path: Path):
        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump({"existing": True}, f)

        main(args_list=["--write", str(config_path), "--no-backup"])

        backup_path = config_path.with_suffix(".json.bak")
        assert not backup_path.exists()

    def test_write_with_json_flag(self, tmp_path: Path, capsys):
        config_path = tmp_path / "config.json"

        main(args_list=["--write", str(config_path), "--json"])

        # With --json and --write, should still output JSON
        captured = capsys.readouterr()
        # The output should contain valid JSON
        assert "mcpServers" in captured.out
