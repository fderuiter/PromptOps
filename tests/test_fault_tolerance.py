import os
import sys
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

from promptops.utils import load_yaml, save_yaml
from studio.helpers import load_asset_data

def test_load_yaml_propagates_yaml_syntax_error(tmp_path):
    # Create an invalid YAML file
    bad_yaml = tmp_path / "broken.yaml"
    bad_yaml.write_text("key:\n  - incomplete: [\n", encoding="utf-8")
    
    with pytest.raises(yaml.YAMLError):
        load_yaml(bad_yaml)

def test_load_yaml_propagates_jinja_render_error(tmp_path):
    # Create a YAML with a broken Jinja tag
    bad_jinja = tmp_path / "broken_jinja.yaml"
    bad_jinja.write_text("name: {{ invalid {% }}", encoding="utf-8")
    
    with pytest.raises(Exception):
        load_yaml(bad_jinja)

def test_load_asset_data_propagates_errors(tmp_path):
    bad_yaml = tmp_path / "broken.yaml"
    bad_yaml.write_text("key:\n  - incomplete: [\n", encoding="utf-8")
    
    with pytest.raises(yaml.YAMLError):
        load_asset_data(str(bad_yaml))

def test_inject_test_data_aborts_on_corrupt_workflow():
    # We patch iter_workflow_files to return a list with a single non-existent file path
    # which will cause load_yaml to throw FileNotFoundError, triggering the exception handler in inject_test_data
    with patch("promptops.utils.iter_workflow_files") as mock_iter:
        mock_iter.return_value = [Path("/nonexistent_or_broken_file.yaml")]
        
        with pytest.raises(SystemExit) as excinfo:
            import importlib
            import tools.scripts.inject_test_data
            importlib.reload(tools.scripts.inject_test_data)
        
        assert excinfo.value.code == 1

def test_prompt_editor_handles_corrupt_asset():
    # Create a corrupted file in prompts/
    bad_prompt = Path("/app/prompts/broken_test.prompt.md")
    bad_prompt.write_text("key:\n  - [broken\n", encoding="utf-8")
    
    try:
        # Run AppTest on Prompt Editor
        at = AppTest.from_file("/app/studio/studio/pages/1_📝_Prompt_Editor.py")
        at.run(timeout=15)
        
        # Select the broken prompt
        selectbox = at.selectbox[0]
        if selectbox:
            selectbox.set_value("prompts/broken_test.prompt.md").run()
            
            # Verify that an error message is rendered
            assert len(at.error) > 0
            error_msg = at.error[0].value
            assert "Syntax Error" in error_msg or "Parsing Failure" in error_msg
    finally:
        if bad_prompt.exists():
            bad_prompt.unlink()

def test_workflow_editor_handles_corrupt_asset():
    # Create a corrupted file in workflows/
    bad_wf = Path("/app/workflows/broken_test.workflow.yaml")
    bad_wf.write_text("steps:\n  - map_inputs: { [\n", encoding="utf-8")
    
    try:
        at = AppTest.from_file("/app/studio/studio/pages/2_🔄_Workflow_Editor.py")
        at.run(timeout=15)
        
        selectbox = at.selectbox[0]
        if selectbox:
            selectbox.set_value("workflows/broken_test.workflow.yaml").run()
            
            assert len(at.error) > 0
            error_msg = at.error[0].value
            assert "Syntax Error" in error_msg or "Parsing Failure" in error_msg
    finally:
        if bad_wf.exists():
            bad_wf.unlink()
