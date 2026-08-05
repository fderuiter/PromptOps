import subprocess
import sys
import asyncio
import logging
from pathlib import Path
from typing import Any

from promptops.utils import get_tool_name_mcp

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

from promptops.utils import load_yaml, extract_template_vars, WORKFLOWS_DIR, PROMPTS_DIR
from promptops.validation import ProomptsValidationError

# Setup basic logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


server = Server("DynamicProompts")
active_session = None
main_loop = None

class PromptDirHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(('.prompt.yaml', '.prompt.yml', '.prompt.md', 'skills.md', '.workflow.yaml', '.workflow.yml')):
            logger.info(f"File change detected: {event.src_path}")
            # Trigger document rebuild without blocking
            subprocess.Popen(["uv", "run", "promptops", "docs"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if active_session and main_loop:
                asyncio.run_coroutine_threadsafe(
                    active_session.send_tool_list_changed(),
                    main_loop
                )


def build_schema(prompt_content_or_vars):
    if isinstance(prompt_content_or_vars, list):
        variables = prompt_content_or_vars
    else:
        variables = prompt_content_or_vars.get('variables') or prompt_content_or_vars.get('vars') or prompt_content_or_vars.get('inputs')

    properties = {}
    required = []
    
    if variables:
        if isinstance(variables, list):
            for var in variables:
                if isinstance(var, dict):
                    name = var.get('name')
                    if not name:
                        continue
                    properties[name] = {
                        "type": "string",
                        "description": var.get('description', f"The {name} input.")
                    }
                    if var.get('required', True):
                        required.append(name)
                elif isinstance(var, str):
                    properties[var] = {
                        "type": "string",
                        "description": f"The {var} input."
                    }
                    required.append(var)
        elif isinstance(variables, dict):
            for name, desc in variables.items():
                properties[name] = {
                    "type": "string",
                    "description": str(desc) if desc else f"The {name} input."
                }
                required.append(name)
    elif isinstance(prompt_content_or_vars, dict):
        extracted_vars = extract_template_vars(prompt_content_or_vars)
        for var in extracted_vars:
            properties[var] = {
                "type": "string",
                "description": f"The {var} input."
            }
            required.append(var)
            
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }

def build_routing_map() -> dict[str, dict[str, Any]]:
    """
    Builds an in-memory routing map of active tools synchronously.
    It uses the existing CLI agent discovery engine to get active,
    non-overridden tools, guaranteeing zero duplicates and matching reports.
    """
    from promptops.agent import get_tools_info
    from promptops.utils import get_tool_name_mcp, parse_skill_manifest, load_yaml, PROMPTS_DIR
    from pathlib import Path

    routing_map = {}
    try:
        tools_info, manifests, prompts, skills, workflows = get_tools_info(PROMPTS_DIR)
    except Exception as e:
        logger.error(f"Error in CLI discovery engine get_tools_info: {e}")
        return routing_map

    # Build manifest skills helper map
    manifest_skills = {}
    for m in manifests:
        manifest_skills[m["path"]] = m["skills"]

    # Process skills
    for s in skills:
        tool_name = s["tool_name"]
        path_str = s["path"]
        original_name = s["original_name"]
        
        # Look up the actual skill dict in the parsed manifest skills
        skill_dict = None
        for sd in manifest_skills.get(path_str, []):
            if get_tool_name_mcp(Path(path_str), sd) == tool_name:
                skill_dict = sd
                break
        if not skill_dict:
            for sd in manifest_skills.get(path_str, []):
                if sd.get("name") == original_name:
                    skill_dict = sd
                    break
                    
        if skill_dict:
            routing_map[tool_name] = {
                "type": "skill",
                "path": path_str,
                "skill": skill_dict,
                "description": skill_dict.get("description", "Agent Skill"),
                "variables": skill_dict.get("variables", []),
                "original_name": original_name,
            }
            
    # Process prompts (active, non-overridden prompts only)
    for p in prompts:
        tool_name = p["tool_name"]
        path_str = p["path"]
        try:
            content = load_yaml(path_str)
            if content:
                routing_map[tool_name] = {
                    "type": "prompt",
                    "path": path_str,
                    "content": content,
                    "description": content.get("description", "Prompt Tool"),
                    "original_name": p["original_name"],
                }
        except Exception as e:
            logger.error(f"Error loading prompt {path_str}: {e}")

    # Process workflows
    for w in workflows:
        tool_name = w["tool_name"]
        path_str = w["path"]
        try:
            content = load_yaml(path_str)
            if content:
                routing_map[tool_name] = {
                    "type": "workflow",
                    "path": path_str,
                    "content": content,
                    "description": content.get("description", "Workflow Tool"),
                    "original_name": w["original_name"],
                }
        except Exception as e:
            logger.error(f"Error loading workflow {path_str}: {e}")

    return routing_map

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    global active_session
    try:
        active_session = server.request_context.session
    except:
        active_session = None

    routing_map = build_routing_map()
    tools = []
    for name, info in routing_map.items():
        if info["type"] == "skill":
            tools.append(types.Tool(
                name=name,
                description=info["description"],
                inputSchema=build_schema(info["variables"])
            ))
        elif info["type"] in ("prompt", "workflow"):
            tools.append(types.Tool(
                name=name,
                description=info["description"],
                inputSchema=build_schema(info["content"])
            ))
            
    logger.info(f"Discovered {len(tools)} tools via routing map.")
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    if arguments is None:
        arguments = {}
        
    from promptops.engine import simulate_prompt_execution, run_workflow

    routing_map = build_routing_map()
    
    if name not in routing_map:
        raise ValueError(f"Tool not found: {name}")
        
    info = routing_map[name]
    path_str = info["path"]
    
    if info["type"] == "prompt":
        content = info["content"]
        try:
            fidelity: dict[str, Any] = {}
            out = simulate_prompt_execution(content, arguments, prompt_file=path_str, strict_mode=False, chaos_mode=False, fidelity_report=fidelity)
            return [types.TextContent(type="text", text=f"--- Executing Prompt: {content.get('name')} ---\n\n{out}")]
        except ProomptsValidationError as e:
            return [types.TextContent(type="text", text=f"--- Validation Error ---\n\nResponse validation failed for '{name}': {e}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"--- Execution Error ---\n\nExecution failed for '{name}': {e}")]
            
    elif info["type"] == "workflow":
        content = info["content"]
        try:
            fidelity = {}
            state = run_workflow(path_str, arguments, verbose=False, strict_mode=False, chaos_mode=False, fidelity_report=fidelity)
            out = ""
            if state:
                final_output_step_id = content.get('steps', [{}])[-1].get('step_id')
                if final_output_step_id and final_output_step_id in state['steps']:
                    out = state['steps'][final_output_step_id]['output']
            return [types.TextContent(type="text", text=f"--- Executing Workflow: {content.get('name')} ---\n\n{out}")]
        except ProomptsValidationError as e:
            return [types.TextContent(type="text", text=f"--- Validation Error ---\n\nResponse validation failed for '{name}': {e}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"--- Execution Error ---\n\nExecution failed for '{name}': {e}")]
            
    elif info["type"] == "skill":
        skill = info["skill"]
        try:
            content = {
                "name": skill["name"],
                "description": skill.get("description", ""),
                "variables": skill.get("variables", []),
                "messages": [{"role": "system", "content": skill.get("instructions", "")}],
                "testData": skill.get("testData", [])
            }
            fidelity = {}
            out = simulate_prompt_execution(content, arguments, prompt_file=path_str, strict_mode=False, chaos_mode=False, fidelity_report=fidelity)
            return [types.TextContent(
                type="text",
                text=f"--- Executing Skill: {skill['name']} ---\n\n{out}"
            )]
        except ProomptsValidationError as e:
            return [types.TextContent(type="text", text=f"--- Validation Error ---\n\nResponse validation failed for '{name}': {e}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"--- Execution Error ---\n\nExecution failed for '{name}': {e}")]
            
    else:
        raise ValueError(f"Unknown tool type: {info['type']}")

async def run():
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    observer = Observer()
    handler = PromptDirHandler()
    
    # Watch prompts directory
    observer.schedule(handler, path=str(PROMPTS_DIR), recursive=True)
    logger.info(f"Started monitoring {PROMPTS_DIR} for changes.")
    
    # Watch workflows directory
    workflows_path = str(WORKFLOWS_DIR)
    if Path(workflows_path).exists():
        observer.schedule(handler, path=workflows_path, recursive=True)
        logger.info(f"Started monitoring {workflows_path} for changes.")
        
    observer.start()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="DynamicProompts",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=True,
                        resources_changed=True,
                        tools_changed=True
                    ),
                    experimental_capabilities={},
                ),
            )
        )
    
    observer.stop()
    observer.join()

if __name__ == "__main__":
    asyncio.run(run())
