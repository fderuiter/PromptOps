import os
import pytest
from pathlib import Path
from pydantic import ValidationError
from promptops.validation import PromptSchema, validate_prompts
from promptops.utils import load_requirements, REQUIREMENTS_FILE, save_yaml

def test_pydantic_rejects_invalid_requirements_structure():
    """
    Pydantic models reject prompt configurations where the requirements metadata field uses an invalid structure.
    """
    # Valid structure (list of strings)
    valid_content = {
        "name": "Test Prompt",
        "version": "1.0.0",
        "description": "A test prompt.",
        "metadata": {
            "domain": "general",
            "complexity": "low",
            "requirements": ["REQ-001", "REQ-002"]
        },
        "model": "gpt-4",
        "modelParameters": {"temperature": 0.5},
        "messages": [
            {"role": "system", "content": "You are an assistant. {{input}}"},
            {"role": "user", "content": "Hello"}
        ],
        "variables": [{"name": "input", "description": "Input text"}],
        "testData": [],
        "evaluators": []
    }
    
    # Should validate successfully
    schema = PromptSchema(**valid_content)
    assert schema.metadata.requirements == ["REQ-001", "REQ-002"]
    
    # Invalid structure - dictionary where a list is expected
    invalid_content_dict = dict(valid_content)
    invalid_content_dict["metadata"] = dict(valid_content["metadata"])
    invalid_content_dict["metadata"]["requirements"] = {"REQ-001": "invalid"}
    
    with pytest.raises(ValidationError):
        PromptSchema(**invalid_content_dict)

    # Invalid structure - integer where a list is expected
    invalid_content_int = dict(valid_content)
    invalid_content_int["metadata"] = dict(valid_content["metadata"])
    invalid_content_int["metadata"]["requirements"] = 12345
    
    with pytest.raises(ValidationError):
        PromptSchema(**invalid_content_int)


def test_parse_requirements_yaml_structures(tmp_path):
    """
    The system must parse various formats of local specification files containing master requirement lists.
    """
    req_file = tmp_path / "requirements.yaml"
    
    # 1. Dictionary with "requirements" key holding a list of dicts with id
    data1 = {
        "requirements": [
            {"id": "REQ-101", "description": "First req"},
            {"id": "REQ-102", "description": "Second req"}
        ]
    }
    save_yaml(req_file, data1)
    os.environ["PROMPTOPS_REQUIREMENTS_PATH"] = str(req_file)
    try:
        parsed1 = load_requirements()
        assert parsed1 == {"REQ-101", "REQ-102"}
    finally:
        if "PROMPTOPS_REQUIREMENTS_PATH" in os.environ:
            del os.environ["PROMPTOPS_REQUIREMENTS_PATH"]

    # 2. Flat list of strings
    data2 = ["REQ-201", "REQ-202"]
    save_yaml(req_file, data2)
    os.environ["PROMPTOPS_REQUIREMENTS_PATH"] = str(req_file)
    try:
        parsed2 = load_requirements()
        assert parsed2 == {"REQ-201", "REQ-202"}
    finally:
        if "PROMPTOPS_REQUIREMENTS_PATH" in os.environ:
            del os.environ["PROMPTOPS_REQUIREMENTS_PATH"]

    # 3. Flat dictionary with ID as keys
    data3 = {
        "REQ-301": "Desc 1",
        "REQ-302": "Desc 2"
    }
    save_yaml(req_file, data3)
    os.environ["PROMPTOPS_REQUIREMENTS_PATH"] = str(req_file)
    try:
        parsed3 = load_requirements()
        assert parsed3 == {"REQ-301", "REQ-302"}
    finally:
        if "PROMPTOPS_REQUIREMENTS_PATH" in os.environ:
            del os.environ["PROMPTOPS_REQUIREMENTS_PATH"]


def test_validate_prompts_compares_mapped_requirements(tmp_path, capsys):
    """
    Validation tool must compare mapped prompt tags against master list and print explicit errors.
    """
    # Setup temporary requirements.yaml
    req_file = tmp_path / "requirements.yaml"
    data = {
        "requirements": [
            {"id": "REQ-001", "description": "Valid Req 1"},
            {"id": "REQ-002", "description": "Valid Req 2"}
        ]
    }
    save_yaml(req_file, data)
    
    # Create valid and invalid prompt files
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    
    # Needs overview.md because directory hygiene is checked!
    (prompts_dir / "overview.md").write_text("# Test Prompts\n", encoding="utf-8")
    
    # Valid Prompt
    valid_prompt_content = {
        "name": "Valid Prompt",
        "version": "1.0.0",
        "description": "Description",
        "metadata": {
            "domain": "general",
            "complexity": "low",
            "requirements": ["REQ-001"]
        },
        "model": "gpt-4",
        "modelParameters": {"temperature": 0.5},
        "messages": [
            {"role": "system", "content": "System message {{input}}"},
            {"role": "user", "content": "User message"}
        ],
        "variables": [{"name": "input", "description": "Input variable"}],
        "testData": [],
        "evaluators": []
    }
    save_yaml(prompts_dir / "valid.prompt.yaml", valid_prompt_content)
    
    # Invalid Prompt (references non-existent requirement REQ-999)
    invalid_prompt_content = dict(valid_prompt_content)
    invalid_prompt_content["name"] = "Invalid Prompt"
    invalid_prompt_content["metadata"] = dict(valid_prompt_content["metadata"])
    invalid_prompt_content["metadata"]["requirements"] = ["REQ-001", "REQ-999"]
    save_yaml(prompts_dir / "invalid.prompt.yaml", invalid_prompt_content)
    
    # Run validation with the temporary requirements path set
    os.environ["PROMPTOPS_REQUIREMENTS_PATH"] = str(req_file)
    os.environ["PROMPTOPS_REGISTRY"] = str(prompts_dir)
    try:
        # Validate, which should return False due to REQ-999
        result = validate_prompts(str(prompts_dir), strict=False)
        assert result is False
        
        # Verify clear error output printed to stdout/terminal
        captured = capsys.readouterr()
        assert "REQ-999" in captured.out or "REQ-999" in captured.err
        assert "Requirement ID(s) missing from master list" in captured.out or "Requirement ID(s) missing from master list" in captured.err
        
    finally:
        if "PROMPTOPS_REQUIREMENTS_PATH" in os.environ:
            del os.environ["PROMPTOPS_REQUIREMENTS_PATH"]
        if "PROMPTOPS_REGISTRY" in os.environ:
            del os.environ["PROMPTOPS_REGISTRY"]
