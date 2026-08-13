"""Module docstring."""
import os
import sys
import json
import shutil
import difflib
from pathlib import Path
from typing import Tuple, List, Dict, Any

from promptops.utils import iter_prompt_files, load_yaml, iter_skill_manifests, parse_skill_manifest, iter_workflow_files, get_tool_name, get_tool_name_mcp, resolve_skill_from_path, deep_merge

def get_tools_info(prompts_dir: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Missing docstring."""
    manifests = []
    skills = []
    
    manifested_tool_names = set()
    
    for path in iter_skill_manifests(str(prompts_dir)):
        try:
            manifest = parse_skill_manifest(path)
            domain = manifest["metadata"].get("domain") or path.parent.name
            manifests.append({"path": str(path), "domain": domain, "skills": manifest["skills"]})
            
            for skill in manifest["skills"]:
                tool_name = get_tool_name_mcp(path, skill)
                manifested_tool_names.add(tool_name.lower())
                skills.append({
                    "original_name": skill["name"],
                    "tool_name": tool_name,
                    "path": str(path)
                })
        except Exception:
            pass

    tools_info = []
    prompts = []
    for path in iter_prompt_files(str(prompts_dir)):
        try:
            content = load_yaml(str(path))
        except Exception:
            continue
            
        original_name, tool_name = get_tool_name(path, content)
        
        overridden = False
        overriding_manifest = None
        skills_md_path = path.parent / "skills.md"
        if skills_md_path.exists():
            try:
                manifest = parse_skill_manifest(skills_md_path)
                match = resolve_skill_from_path(path, manifest.get("skills", []))
                if match:
                    overridden = True
                    overriding_manifest = str(skills_md_path)
            except Exception:
                pass
                
        if not overridden and tool_name.lower() in manifested_tool_names and skills_md_path.exists():
             overridden = True
             overriding_manifest = str(skills_md_path)
             
        if not overridden:
            prompts.append({
                "original_name": original_name,
                "tool_name": tool_name,
                "path": str(path)
            })
            
        tools_info.append({
            "path": str(path),
            "original_name": original_name,
            "tool_name": tool_name,
            "truncated": len(original_name) > 64,
            "overridden": overridden,
            "overriding_manifest": overriding_manifest
        })
        
    workflows = []
    from promptops.utils import WORKFLOWS_DIR as current_workflows_dir
    for path in iter_workflow_files(str(current_workflows_dir)):
        try:
            content = load_yaml(str(path))
        except Exception:
            continue
            
        original_name, tool_name = get_tool_name(path, content)
        workflows.append({
            "original_name": original_name,
            "tool_name": tool_name,
            "path": str(path)
        })
    
    return tools_info, manifests, prompts, skills, workflows

def generate_config(prompts_dir: str):
    """Missing docstring."""
    root = Path(prompts_dir).resolve().parent
    python_path = sys.executable
    script_path = str(root / "mcp_server.py")
    cwd = str(root)
    
    config = {
        "mcpServers": {
            "proompts": {
                "command": python_path,
                "args": [script_path],
                "env": {
                    "PYTHONPATH": cwd
                }
            }
        }
    }
    print(json.dumps(config, indent=2))

def discovery_report(prompts_dir: str):
    """Missing docstring."""
    prompts_dir_path = Path(prompts_dir).resolve()
    tools_info, manifests, prompts, skills, workflows = get_tools_info(prompts_dir_path)
    
    print("=== Discovery Report ===")
    
    print("\n--- Workflows ---")
    for t in sorted(workflows, key=lambda x: x["tool_name"]):
        print(f"- {t['tool_name']}")
        
    print("\n--- Prompts ---")
    for t in sorted(prompts, key=lambda x: x["tool_name"]):
        print(f"- {t['tool_name']}")
        
    print("\n--- Skills ---")
    for t in sorted(skills, key=lambda x: x["tool_name"]):
        print(f"- {t['tool_name']}")
        
    print("\n--- Tool Name Transformations ---")
    for t in sorted(tools_info, key=lambda x: x["original_name"]):
        if t["tool_name"] != t["original_name"]:
            print(f"- {t['original_name']} -> {t['tool_name']}")

    print("\n--- Overridden Tools ---")
    for t in sorted(tools_info, key=lambda x: x["path"]):
        if t["overridden"]:
            try:
                rel_path = str(Path(t["path"]).relative_to(prompts_dir_path.parent))
                rel_manifest = str(Path(t["overriding_manifest"]).relative_to(prompts_dir_path.parent))
            except ValueError:
                rel_path = t["path"]
                rel_manifest = t["overriding_manifest"]
            print(f"- {rel_path} is overridden by {rel_manifest}")


def resolve_claude_desktop_config_path(platform: str = None, env: dict = None) -> Path:
    """Resolve the platform-specific path to the Claude Desktop config file."""
    if platform is None:
        platform = sys.platform
    if env is None:
        env = os.environ
        
    home = env.get("HOME") or env.get("USERPROFILE") or os.path.expanduser("~")
    home_path = Path(home)
    
    if platform == "darwin":
        return home_path / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif platform == "win32":
        appdata = env.get("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        else:
            return home_path / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:
        # Fallback for Linux or others
        return home_path / ".config" / "Claude" / "claude_desktop_config.json"


def register_agent(prompts_dir: str):
    """Interactively register the proompts MCP server with Claude Desktop."""
    config_path = resolve_claude_desktop_config_path()
    print(f"Target system configuration path: {config_path}")
    
    if sys.platform not in ("darwin", "win32"):
        print("Warning: Claude Desktop is not officially supported on this operating system.")
        
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_config = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Existing configuration file is not valid JSON ({e}).")
            choice = input("Would you like to overwrite it with a fresh configuration? [y/N]: ").strip().lower()
            if choice not in ("y", "yes"):
                print("Registration aborted.")
                return
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            return

    root = Path(prompts_dir).resolve().parent
    python_path = sys.executable
    script_path = str(root / "mcp_server.py")
    cwd = str(root)
    
    proposed_mcp = {
        "mcpServers": {
            "proompts": {
                "command": python_path,
                "args": [script_path],
                "env": {
                    "PYTHONPATH": cwd
                }
            }
        }
    }
    
    updated_config = deep_merge(existing_config, proposed_mcp)
    
    original_json_str = json.dumps(existing_config, indent=2)
    proposed_json_str = json.dumps(updated_config, indent=2)
    
    print("\n--- Proposed Configuration Changes (Visual Diff) ---")
    diff_lines = list(difflib.unified_diff(
        original_json_str.splitlines(),
        proposed_json_str.splitlines(),
        fromfile="Current Configuration",
        tofile="Proposed Configuration",
        lineterm=""
    ))
    
    if not diff_lines:
        print("No changes to make; the proompts MCP server is already registered with identical configuration.")
        return
        
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            print(f"\033[32m{line}\033[0m")  # Green
        elif line.startswith("-") and not line.startswith("---"):
            print(f"\033[31m{line}\033[0m")  # Red
        elif line.startswith("^"):
            print(f"\033[36m{line}\033[0m")  # Cyan
        else:
            print(line)
            
    confirm = input("\nDo you want to apply these changes to your Claude Desktop configuration? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Changes discarded. Registration aborted.")
        return
        
    # Create backup if original exists
    if config_path.exists():
        backup_path = config_path.with_suffix(config_path.suffix + ".bak")
        try:
            shutil.copy2(config_path, backup_path)
            print(f"Backup created at: {backup_path}")
        except Exception as e:
            print(f"Warning: Failed to create backup file: {e}")
            
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(proposed_json_str)
            f.write("\n")
        print("Successfully registered proompts MCP server with Claude Desktop!")
    except Exception as e:
        print(f"Error writing configuration file: {e}")
