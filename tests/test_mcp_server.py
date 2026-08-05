import pytest
from unittest.mock import patch
from pathlib import Path
import mcp.types as types

from mcp_server import build_routing_map, handle_list_tools, handle_call_tool

def test_mcp_server_discovery_and_resolution(tmp_path):
    prompts_dir = tmp_path / "prompts"
    workflows_dir = tmp_path / "workflows"
    
    # Create directory structure
    cra_dir = prompts_dir / "clinical" / "cra"
    cra_dir.mkdir(parents=True, exist_ok=True)
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Base prompt file that WILL be overridden
    base_prompt_content = """
name: Risk-Based Monitoring (RBM) Plan Builder
version: "1.0.0"
description: Develop a site-level risk-based monitoring plan.
variables:
  - name: input
    description: The primary input or query text for the prompt
    required: true
model: gpt-4o-mini
messages:
  - role: system
    content: "You are a base prompt."
  - role: user
    content: "{{input}}"
testData:
  - input:
      input: "hello"
    expected: "base prompt response"
"""
    base_prompt_file = cra_dir / "risk_based_monitoring.prompt.yaml"
    base_prompt_file.write_text(base_prompt_content, encoding="utf-8")
    
    # 2. Standalone active prompt that WILL NOT be overridden
    unrelated_prompt_content = """
name: Unrelated Prompt Tool
version: "1.0.0"
description: This is a standalone prompt.
variables:
  - name: input
    description: Some input
    required: true
model: gpt-4o-mini
messages:
  - role: user
    content: "{{input}}"
testData:
  - input:
      input: "hello"
    expected: "standalone response"
"""
    unrelated_prompt_file = cra_dir / "unrelated.prompt.yaml"
    unrelated_prompt_file.write_text(unrelated_prompt_content, encoding="utf-8")
    
    # 3. Custom skill manifest defining the override skill
    skills_md_content = """# Domain Agent Skills: Clinical Cra
## Metadata
- **Domain Namespace:** clinical.cra
- **Target Runtime:** PromptOps / MCP Server

---

## Skill: Risk-Based Monitoring (RBM) Plan Builder
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Develop a site-level risk-based monitoring plan with risk matrix, KRIs, and adaptive strategy.

### Core Instructions
```text
[SYSTEM]
You are an overriding custom skill manifest.

[USER]
{{ input }}
```

### Few-Shot Assertions
**Input Context:**
```yaml
input: "hello"
```
**Asserted Output:**
```text
override skill response
```
"""
    skills_file = cra_dir / "skills.md"
    skills_file.write_text(skills_md_content, encoding="utf-8")

    # Patch the directory constants used by mcp_server and promptops
    with patch("mcp_server.PROMPTS_DIR", prompts_dir), \
         patch("promptops.utils.PROMPTS_DIR", prompts_dir), \
         patch("promptops.utils.WORKFLOWS_DIR", workflows_dir), \
         patch("mcp_server.WORKFLOWS_DIR", workflows_dir):
         
        # Execute build_routing_map
        routing_map = build_routing_map()
        
        # Verify overridden base tool is filtered out and overridden by the skill
        # The tool names are namespaced
        # Let's search for keys containing "risk_based_monitoring" or matching RBM plan builder
        rbm_tool_key = None
        unrelated_tool_key = None
        for key in routing_map.keys():
            if "risk_based_monitoring" in key.lower() or "rbm" in key.lower():
                rbm_tool_key = key
            if "unrelated" in key.lower():
                unrelated_tool_key = key
                
        assert rbm_tool_key is not None, "RBM tool should be present in the routing map"
        assert unrelated_tool_key is not None, "Unrelated standalone prompt should be present in the routing map"
        
        # Verify types of mapped tools
        assert routing_map[rbm_tool_key]["type"] == "skill", "The RBM tool must map to 'skill' type, not 'prompt' base type"
        assert routing_map[unrelated_tool_key]["type"] == "prompt", "The unrelated prompt must map to 'prompt' type"
        
        # Verify handle_list_tools list does not contain duplicate registrations
        import asyncio
        tools = asyncio.run(handle_list_tools())
        
        # Check tool names and count
        tool_names = [t.name for t in tools]
        assert len(tool_names) == len(set(tool_names)), "There must be zero duplicate tool registrations visible"
        assert len(tools) == 2, f"There should only be 2 active tools, got: {tool_names}"
        
        # Verify that executing the overridden tool runs the manifest skill's custom instructions instead of the base prompt
        call_res = asyncio.run(handle_call_tool(rbm_tool_key, {"input": "hello"}))
        
        assert len(call_res) == 1
        assert isinstance(call_res[0], types.TextContent)
        text = call_res[0].text
        assert "override skill response" in text, "Calling the overridden tool must run the overriding skill and return its expected result"
        assert "base prompt response" not in text, "The deprecated base prompt template must be ignored"
        
        # Verify executing unrelated tool runs successfully
        unrelated_res = asyncio.run(handle_call_tool(unrelated_tool_key, {"input": "hello"}))
        assert "standalone response" in unrelated_res[0].text
