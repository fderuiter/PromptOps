import sys
import json
from pathlib import Path
from unittest.mock import patch


from promptops.agent import resolve_claude_desktop_config_path, register_agent


def test_resolve_claude_desktop_config_path_mac():
    env = {"HOME": "/Users/testuser"}
    path = resolve_claude_desktop_config_path(platform="darwin", env=env)
    assert path == Path("/Users/testuser/Library/Application Support/Claude/claude_desktop_config.json")


def test_resolve_claude_desktop_config_path_windows_with_appdata():
    env = {
        "USERPROFILE": "C:/Users/testuser",
        "APPDATA": "C:/Users/testuser/AppData/Roaming"
    }
    path = resolve_claude_desktop_config_path(platform="win32", env=env)
    assert path.as_posix() == "C:/Users/testuser/AppData/Roaming/Claude/claude_desktop_config.json"


def test_resolve_claude_desktop_config_path_windows_fallback():
    env = {
        "USERPROFILE": "C:/Users/testuser"
    }
    env.pop("APPDATA", None)
    path = resolve_claude_desktop_config_path(platform="win32", env=env)
    assert path.as_posix() == "C:/Users/testuser/AppData/Roaming/Claude/claude_desktop_config.json"


def test_resolve_claude_desktop_config_path_linux():
    env = {"HOME": "/home/testuser"}
    path = resolve_claude_desktop_config_path(platform="linux", env=env)
    assert path == Path("/home/testuser/.config/Claude/claude_desktop_config.json")


@patch("promptops.agent.resolve_claude_desktop_config_path")
@patch("promptops.agent.input")
def test_register_agent_new_file(mock_input, mock_resolve, tmp_path):
    config_file = tmp_path / "claude_desktop_config.json"
    mock_resolve.return_value = config_file
    mock_input.return_value = "y"
    
    register_agent(prompts_dir=str(tmp_path / "prompts"))
    
    assert config_file.exists()
    
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "mcpServers" in data
    assert "proompts" in data["mcpServers"]
    assert data["mcpServers"]["proompts"]["command"] == sys.executable
    assert data["mcpServers"]["proompts"]["args"] == [str(tmp_path / "mcp_server.py")]
    assert data["mcpServers"]["proompts"]["env"]["PYTHONPATH"] == str(tmp_path)
    
    backup_file = config_file.with_suffix(config_file.suffix + ".bak")
    assert not backup_file.exists()


@patch("promptops.agent.resolve_claude_desktop_config_path")
@patch("promptops.agent.input")
def test_register_agent_merge_existing(mock_input, mock_resolve, tmp_path):
    config_file = tmp_path / "claude_desktop_config.json"
    
    existing_data = {
        "mcpServers": {
            "existing_server": {
                "command": "node",
                "args": ["other.js"]
            }
        },
        "customKey": "customValue"
    }
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2)
        
    mock_resolve.return_value = config_file
    mock_input.return_value = "yes"
    
    register_agent(prompts_dir=str(tmp_path / "prompts"))
    
    backup_file = config_file.with_suffix(config_file.suffix + ".bak")
    assert backup_file.exists()
    with open(backup_file, "r", encoding="utf-8") as f:
        backup_data = json.load(f)
    assert backup_data == existing_data
    
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["customKey"] == "customValue"
    assert "existing_server" in data["mcpServers"]
    assert "proompts" in data["mcpServers"]
    assert data["mcpServers"]["proompts"]["command"] == sys.executable


@patch("promptops.agent.resolve_claude_desktop_config_path")
@patch("promptops.agent.input")
def test_register_agent_abort_on_prompt(mock_input, mock_resolve, tmp_path):
    config_file = tmp_path / "claude_desktop_config.json"
    mock_resolve.return_value = config_file
    mock_input.return_value = "n"
    
    register_agent(prompts_dir=str(tmp_path / "prompts"))
    assert not config_file.exists()


@patch("promptops.agent.resolve_claude_desktop_config_path")
@patch("promptops.agent.input")
def test_register_agent_invalid_json_overwrite_confirm(mock_input, mock_resolve, tmp_path):
    config_file = tmp_path / "claude_desktop_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        f.write("{invalid_json")
        
    mock_resolve.return_value = config_file
    mock_input.side_effect = ["y", "y"]
    
    register_agent(prompts_dir=str(tmp_path / "prompts"))
    
    assert config_file.exists()
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "proompts" in data["mcpServers"]


@patch("promptops.agent.resolve_claude_desktop_config_path")
@patch("promptops.agent.input")
def test_register_agent_invalid_json_overwrite_reject(mock_input, mock_resolve, tmp_path):
    config_file = tmp_path / "claude_desktop_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        f.write("{invalid_json")
        
    mock_resolve.return_value = config_file
    mock_input.return_value = "n"
    
    register_agent(prompts_dir=str(tmp_path / "prompts"))
    
    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "{invalid_json"
