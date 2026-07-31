import os
import urllib.error
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from promptops.utils import ROOT
from promptops.validation import (
    extract_system_instructions,
    get_modified_prompt_files,
    check_semantic_duplicates,
    validate_prompts
)

def test_extract_system_instructions():
    # 1. Normal system message
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
    }
    assert extract_system_instructions(data) == "You are a helpful assistant."

    # 2. List content for system message
    data_list = {
        "messages": [
            {"role": "system", "content": ["Line 1", "Line 2"]},
        ]
    }
    assert extract_system_instructions(data_list) == "Line 1 Line 2"

    # 3. Fallback to description
    data_desc = {
        "description": "Writes poetry.",
        "messages": [
            {"role": "user", "content": "Write a poem."}
        ]
    }
    assert extract_system_instructions(data_desc) == "Description: Writes poetry.\nWrite a poem."


@patch("subprocess.run")
def test_get_modified_prompt_files(mock_run):
    # Simulate git status output
    mock_stdout = (
        " M prompts/communication/entertainment/joke_workflow/01_topic_generator.prompt.yaml\n"
        "A  prompts/non_existent.prompt.yaml\n"  # Doesn't exist, should be skipped
        "?? prompts/communication/entertainment/joke_workflow/02_joke_writer.prompt.yaml\n"
    )
    mock_run.return_value = MagicMock(stdout=mock_stdout)

    # Let's check. Since joke_workflow files actually exist in the workspace, we should get those that exist.
    modified = get_modified_prompt_files(str(ROOT / "prompts"))
    
    # Check that 01_topic_generator.prompt.yaml is in modified files
    # 02_joke_writer.prompt.yaml is also tracked as untracked, it exists and should be in modified files
    # non_existent.prompt.yaml does not exist, so it should NOT be in modified files
    assert any("01_topic_generator.prompt.yaml" in str(p) for p in modified)
    assert any("02_joke_writer.prompt.yaml" in str(p) for p in modified)
    assert not any("non_existent.prompt.yaml" in str(p) for p in modified)


@patch.dict(os.environ, {}, clear=True)
@patch("promptops.console.warn")
def test_check_semantic_duplicates_no_key(mock_warn):
    # Ensure no key is set
    if "LLM_API_KEY" in os.environ:
        del os.environ["LLM_API_KEY"]
    if "LLM_API_KEY_SHADOW" in os.environ:
        del os.environ["LLM_API_KEY_SHADOW"]

    modified_files = [ROOT / "prompts" / "communication" / "entertainment" / "joke_workflow" / "01_topic_generator.prompt.yaml"]
    res = check_semantic_duplicates(str(ROOT / "prompts"), modified_files)
    assert res is True
    mock_warn.assert_called_once_with("Skipping semantic audit: LLM_API_KEY or LLM_API_KEY_SHADOW is not set.")


@patch.dict(os.environ, {"LLM_API_KEY": "fake-key"})
@patch("urllib.request.urlopen")
def test_check_semantic_duplicates_success(mock_urlopen):
    # Mock the response to return a valid JSON without duplicate
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "choices": [{
            "message": {
                "content": json.dumps({
                    "is_duplicate": False,
                    "matching_file": None,
                    "reason": None
                })
            }
        }]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    modified_files = [ROOT / "prompts" / "communication" / "entertainment" / "joke_workflow" / "01_topic_generator.prompt.yaml"]
    res = check_semantic_duplicates(str(ROOT / "prompts"), modified_files)
    assert res is True


@patch.dict(os.environ, {"LLM_API_KEY": "fake-key"})
@patch("urllib.request.urlopen")
@patch("promptops.console.error")
def test_check_semantic_duplicates_detected(mock_console_error, mock_urlopen):
    # Mock the response to return duplicate found
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "choices": [{
            "message": {
                "content": json.dumps({
                    "is_duplicate": True,
                    "matching_file": "prompts/communication/entertainment/joke_workflow/02_joke_writer.prompt.yaml",
                    "reason": "They are identical comedian prompts."
                })
            }
        }]
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    modified_files = [ROOT / "prompts" / "communication" / "entertainment" / "joke_workflow" / "01_topic_generator.prompt.yaml"]
    res = check_semantic_duplicates(str(ROOT / "prompts"), modified_files)
    assert res is False

    # Check that console.error was called with expected details
    any_dup_msg = any("duplicate of prompts/communication/entertainment/joke_workflow/02_joke_writer.prompt.yaml" in call[0][0] for call in mock_console_error.call_args_list)
    any_reason_msg = any("They are identical comedian prompts." in call[0][0] for call in mock_console_error.call_args_list)
    assert any_dup_msg
    assert any_reason_msg


@patch.dict(os.environ, {"LLM_API_KEY": "fake-key"})
@patch("urllib.request.urlopen")
@patch("promptops.console.warn")
def test_check_semantic_duplicates_network_error(mock_console_warn, mock_urlopen):
    # Simulate urllib error
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    modified_files = [ROOT / "prompts" / "communication" / "entertainment" / "joke_workflow" / "01_topic_generator.prompt.yaml"]
    res = check_semantic_duplicates(str(ROOT / "prompts"), modified_files)
    # Should skip gracefully and return True
    assert res is True
    mock_console_warn.assert_called_once()
    assert "network unreachable" in mock_console_warn.call_args[0][0]
