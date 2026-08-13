import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from promptops.validation import validate_prompts, load_strategic_config, StrategicConfig
from tools.scripts.enrich_prompts import enrich_file

def test_active_prompt_strategic_variable_placeholder_fails(tmp_path):
    # Setup temporary prompt file and directory hygiene
    prompt_dir = tmp_path / "prompts_test"
    prompt_dir.mkdir()
    
    # Create overview.md to satisfy directory hygiene
    overview_file = prompt_dir / "overview.md"
    overview_file.write_text("# Overview", encoding="utf-8")
    
    prompt_content = {
        "name": "Test Active Prompt",
        "version": "0.1.0",
        "description": "Writes poetry.",
        "metadata": {
            "domain": "communication",
            "status": "active",
            "complexity": "low"
        },
        "variables": [
            {
                "name": "system_context",
                "description": "TODO",  # Blocked!
                "required": True
            }
        ],
        "model": "gpt-4o-mini",
        "modelParameters": {
            "temperature": 0.7
        },
        "messages": [
            {"role": "system", "content": "You are a poet. Context: {{system_context}}"},
            {"role": "user", "content": "Write a poem."}
        ],
        "testData": [
            {"inputs": {"system_context": "sad"}, "expected": "Some sad poem"}
        ],
        "evaluators": []
    }
    
    prompt_file = prompt_dir / "test_active.prompt.yaml"
    prompt_file.write_text(yaml.dump(prompt_content), encoding="utf-8")
    
    # Run validate_prompts
    # Skip semantic checks to avoid hitting external LLMs
    res = validate_prompts(str(prompt_dir), skip_semantic=True)
    assert res is False


def test_draft_prompt_strategic_variable_placeholder_warns_and_passes(tmp_path):
    # Setup temporary prompt file and directory hygiene
    prompt_dir = tmp_path / "prompts_test"
    prompt_dir.mkdir()
    
    overview_file = prompt_dir / "overview.md"
    overview_file.write_text("# Overview", encoding="utf-8")
    
    prompt_content = {
        "name": "Test Draft Prompt",
        "version": "0.1.0",
        "description": "Writes poetry.",
        "metadata": {
            "domain": "communication",
            "status": "draft",  # Draft status!
            "complexity": "low"
        },
        "variables": [
            {
                "name": "system_context",
                "description": "TODO",  # Warning only!
                "required": True
            }
        ],
        "model": "gpt-4o-mini",
        "modelParameters": {
            "temperature": 0.7
        },
        "messages": [
            {"role": "system", "content": "You are a poet. Context: {{system_context}}"},
            {"role": "user", "content": "Write a poem."}
        ],
        "testData": [
            {"inputs": {"system_context": "sad"}, "expected": "Some sad poem"}
        ],
        "evaluators": []
    }
    
    prompt_file = prompt_dir / "test_draft.prompt.yaml"
    prompt_file.write_text(yaml.dump(prompt_content), encoding="utf-8")
    
    with patch("promptops.console.warn") as mock_warn:
        res = validate_prompts(str(prompt_dir), skip_semantic=True)
        assert res is True
        mock_warn.assert_called()
        # Verify the warning contains strategic variable info
        warnings = [call[0][0] for call in mock_warn.call_args_list]
        assert any("Strategic variable 'system_context'" in w for w in warnings)


def test_custom_strategic_variable_instantly_applied(tmp_path):
    # Setup temporary prompt file and directory hygiene
    prompt_dir = tmp_path / "prompts_test"
    prompt_dir.mkdir()
    
    overview_file = prompt_dir / "overview.md"
    overview_file.write_text("# Overview", encoding="utf-8")
    
    prompt_content = {
        "name": "Test Custom Variable Prompt",
        "version": "0.1.0",
        "description": "Writes poetry.",
        "metadata": {
            "domain": "communication",
            "status": "active",
            "complexity": "low"
        },
        "variables": [
            {
                "name": "special_custom_variable",
                "description": "blocked_custom_placeholder",  # Custom placeholder!
                "required": True
            }
        ],
        "model": "gpt-4o-mini",
        "modelParameters": {
            "temperature": 0.7
        },
        "messages": [
            {"role": "system", "content": "You are a poet. Context: {{special_custom_variable}}"},
            {"role": "user", "content": "Write a poem."}
        ],
        "testData": [
            {"inputs": {"special_custom_variable": "sad"}, "expected": "Some sad poem"}
        ],
        "evaluators": []
    }
    
    prompt_file = prompt_dir / "test_custom.prompt.yaml"
    prompt_file.write_text(yaml.dump(prompt_content), encoding="utf-8")
    
    # Originally, special_custom_variable is NOT a strategic variable, so it should pass validation
    res_before = validate_prompts(str(prompt_dir), skip_semantic=True)
    assert res_before is True
    
    # Backup the original strategic_config.yaml file
    config_path = Path(__file__).parent.parent / "promptops" / "promptops" / "strategic_config.yaml"
    original_config_content = config_path.read_text(encoding="utf-8")
    
    try:
        # Dynamically append new strategic variable name to config file
        new_config_content = original_config_content + """
  - name: "special_custom_variable"
    blocked_patterns:
      - "blocked_custom_placeholder"
"""
        config_path.write_text(new_config_content, encoding="utf-8")
        
        # Run validation again - it should instantly apply and FAIL now!
        res_after = validate_prompts(str(prompt_dir), skip_semantic=True)
        assert res_after is False
        
    finally:
        # Restore the original config content
        config_path.write_text(original_config_content, encoding="utf-8")


def test_enrich_prompts_outputs_annotated_placeholder(tmp_path):
    # Setup temporary prompt file
    prompt_dir = tmp_path / "prompts_test"
    prompt_dir.mkdir()
    
    prompt_content = {
        "name": "Test Enrichment",
        "version": "0.1.0",
        "description": "Writes poetry.",
        "metadata": {
            "domain": "communication",
            "status": "draft",
            "complexity": "low"
        },
        "variables": [
            {
                "name": "system_context",
                "description": "TODO",  # Needs enrichment!
                "required": True
            }
        ],
        "model": "gpt-4o-mini",
        "modelParameters": {
            "temperature": 0.7
        },
        "messages": [
            {"role": "system", "content": "You are a poet. Context: {{system_context}}"},
            {"role": "user", "content": "Write a poem."}
        ],
        "testData": [
            {"inputs": {"system_context": "sad"}, "expected": "Some sad poem"}
        ],
        "evaluators": []
    }
    
    prompt_file = prompt_dir / "test_enrich.prompt.yaml"
    prompt_file.write_text(yaml.dump(prompt_content), encoding="utf-8")
    
    # Run the enrichment script on this file
    res = enrich_file(prompt_file)
    assert res is True
    
    # Read the updated file content and verify the variable has been annotated
    enriched_content = yaml.safe_load(prompt_file.read_text(encoding="utf-8"))
    system_context_var = enriched_content["variables"][0]
    assert system_context_var["name"] == "system_context"
    assert system_context_var["description"].startswith("[Automated]")
