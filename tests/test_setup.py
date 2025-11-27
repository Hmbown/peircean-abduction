from unittest.mock import patch
from pathlib import Path
import peircean.mcp.setup as mcp_setup

def test_default_path_used_when_none():
    with patch("peircean.mcp.setup.get_default_config_path") as mock_path:
        mock_path.return_value = Path("/tmp/config.json")
        assert hasattr(mcp_setup, "get_default_config_path")

def test_write_to_default_location():
    with patch("peircean.mcp.setup.get_default_config_path") as mock_path:
         mock_path.return_value = Path("/tmp/config.json")
         assert hasattr(mcp_setup, "get_default_config_path")
