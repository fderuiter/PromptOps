from streamlit.testing.v1 import AppTest
from pathlib import Path
import os

STUDIO_DIR = Path(__file__).parent.parent / "studio"
ROOT_DIR = Path(__file__).parent.parent

def test_app_launches():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/app.py"))
    at.run(timeout=15)
    assert not at.exception

def test_prompt_editor_launches_and_saves():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Find and set folder and file name inputs
    at.selectbox(key="prompt_folder_selectbox").set_value(".").run()
    at.text_input(key="prompt_file_name_input").set_value("test_new").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    success_found = False
    for el in at.success:
        if "Saved successfully and validated!" in el.value:
            success_found = True
            break
    
    assert success_found, "App did not report successful save"
    
    # Check if file was created
    test_file = ROOT_DIR / "prompts" / "test_new.prompt.md"
    assert test_file.exists()
    test_file.unlink()
    
    # Clean up
    if test_file.exists():
        os.remove(str(test_file))


def test_workflow_editor_launches_and_saves():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "2_🔄_Workflow_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Find and set folder and file name inputs
    at.selectbox(key="wf_folder_selectbox").set_value(".").run()
    at.text_input(key="wf_file_name_input").set_value("test_new").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Workflow":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    success_found = False
    for el in at.success:
        if "Saved workflow successfully and validated!" in el.value:
            success_found = True
            break
    
    assert success_found, "App did not report successful save"
    
    # Check if file was created
    test_file = ROOT_DIR / "workflows" / "test_new.workflow.yaml"
    assert test_file.exists()
    test_file.unlink()
    
    # Clean up
    if test_file.exists():
        os.remove(str(test_file))


def test_prompt_editor_saves_mcp_and_output_schema():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception
    
    # Check the checkbox to enable structured output schema
    at.checkbox(key="has_output_schema_chk").check().run()
    
    at.session_state['tools'] = [
        {
            "name": "test_calculator",
            "description": "Calculates sums",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        }
    ]
    at.session_state['output_schema'] = {
        "type": "object",
        "properties": {
            "result": {"type": "number", "description": "The result"}
        },
        "required": ["result"]
    }
    at.run()
    
    at.selectbox(key="prompt_folder_selectbox").set_value(".").run()
    at.text_input(key="prompt_file_name_input").set_value("test_mcp_schema").run()
    
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    test_file = ROOT_DIR / "prompts" / "test_mcp_schema.prompt.md"
    assert test_file.exists()
    
    from promptops.utils import load_yaml
    saved_data = load_yaml(str(test_file))
    assert saved_data is not None
    assert "tools" in saved_data
    assert saved_data["tools"][0]["name"] == "test_calculator"
    assert saved_data["tools"][0]["inputSchema"]["properties"]["a"]["type"] == "number"
    assert "output_schema" in saved_data
    assert saved_data["output_schema"]["properties"]["result"]["type"] == "number"
    
    test_file.unlink()


def test_workflow_editor_saves_test_data():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "2_🔄_Workflow_Editor.py"))
    at.run(timeout=15)
    assert not at.exception
    
    at.session_state['wf_inputs'] = [{"name": "scenario", "description": "scenario description"}]
    at.session_state['wf_testData'] = [
        {
            "inputs": {
                "scenario": "test case scenario data"
            }
        }
    ]
    at.run()
    
    at.selectbox(key="wf_folder_selectbox").set_value(".").run()
    at.text_input(key="wf_file_name_input").set_value("test_wf_data").run()
    
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Workflow":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    test_file = ROOT_DIR / "workflows" / "test_wf_data.workflow.yaml"
    assert test_file.exists()
    
    from promptops.utils import load_yaml
    saved_data = load_yaml(str(test_file))
    assert saved_data is not None
    assert "testData" in saved_data
    assert saved_data["testData"][0]["inputs"]["scenario"] == "test case scenario data"
    
    test_file.unlink()


def test_prompt_editor_blocks_traversal_path():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Try to use a traversal sequence in name
    at.selectbox(key="prompt_folder_selectbox").set_value(".").run()
    at.text_input(key="prompt_file_name_input").set_value("../unsafe").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    
    # Check that it did not save, and shows error
    assert any("Path validation failed" in err.value for err in at.error)
    
    # Check that no file named unsafe or .. was created
    test_file = ROOT_DIR / "prompts" / "unsafe.prompt.md"
    assert not test_file.exists()


def test_prompt_editor_blocks_traversal_folder():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Select the "[Create New Subfolder...]" option and use traversal sequence
    at.selectbox(key="prompt_folder_selectbox").set_value("[Create New Subfolder...]").run()
    at.text_input(key="prompt_new_folder_input").set_value("../unsafe_dir").run()
    at.text_input(key="prompt_file_name_input").set_value("test_file").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    
    # Check that it did not save, and shows error
    assert any("Path validation failed" in err.value for err in at.error)
    
    # Check that folder and file are not created
    unsafe_dir = ROOT_DIR / "unsafe_dir"
    assert not unsafe_dir.exists()


def test_prompt_editor_creates_new_subfolder_automatically():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Select "[Create New Subfolder...]"
    at.selectbox(key="prompt_folder_selectbox").set_value("[Create New Subfolder...]").run()
    at.text_input(key="prompt_new_folder_input").set_value("automated_test_folder").run()
    at.text_input(key="prompt_file_name_input").set_value("test_auto").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    # Check if folder and file were created
    target_dir = ROOT_DIR / "prompts" / "automated_test_folder"
    target_file = target_dir / "test_auto.prompt.md"
    
    assert target_dir.exists()
    assert target_file.exists()
    
    # Clean up
    target_file.unlink()
    target_dir.rmdir()


def test_prompt_editor_saves_strategic_metadata():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "1_📝_Prompt_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Find and set folder and file name inputs
    at.selectbox(key="prompt_folder_selectbox").set_value(".").run()
    at.text_input(key="prompt_file_name_input").set_value("test_strategic").run()

    # Set the strategic metadata fields
    at.text_input(key="meta_strategic_positioning").set_value("High-value healthcare automation").run()
    at.text_input(key="meta_target_audience").set_value("Clinical practitioners").run()
    at.text_input(key="meta_core_mission").set_value("Streamline clinical operations").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Changes":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    # Check if file was created and contains correct metadata
    test_file = ROOT_DIR / "prompts" / "test_strategic.prompt.md"
    assert test_file.exists()
    
    from promptops.utils import load_yaml
    saved_data = load_yaml(str(test_file))
    assert saved_data is not None
    assert "metadata" in saved_data
    assert saved_data["metadata"]["strategic_positioning"] == "High-value healthcare automation"
    assert saved_data["metadata"]["target_audience"] == "Clinical practitioners"
    assert saved_data["metadata"]["core_mission"] == "Streamline clinical operations"

    test_file.unlink()


def test_workflow_editor_saves_strategic_metadata():
    at = AppTest.from_file(str(STUDIO_DIR / "studio/pages" / "2_🔄_Workflow_Editor.py"))
    at.run(timeout=15)
    assert not at.exception

    # Find and set folder and file name inputs
    at.selectbox(key="wf_folder_selectbox").set_value(".").run()
    at.text_input(key="wf_file_name_input").set_value("test_wf_strategic").run()

    # Set the strategic metadata fields
    at.text_input(key="meta_strategic_positioning").set_value("Global scale coordination").run()
    at.text_input(key="meta_target_audience").set_value("Enterprise ops").run()
    at.text_input(key="meta_core_mission").set_value("Automate complex multi-step workflows").run()
    
    # Click save
    save_btn = None
    for btn in at.button:
        if btn.label == "Save Workflow":
            save_btn = btn
            break
            
    assert save_btn is not None
    save_btn.click().run()
    assert not at.exception
    
    # Check if file was created and contains correct metadata
    test_file = ROOT_DIR / "workflows" / "test_wf_strategic.workflow.yaml"
    assert test_file.exists()
    
    from promptops.utils import load_yaml
    saved_data = load_yaml(str(test_file))
    assert saved_data is not None
    assert "metadata" in saved_data
    assert saved_data["metadata"]["strategic_positioning"] == "Global scale coordination"
    assert saved_data["metadata"]["target_audience"] == "Enterprise ops"
    assert saved_data["metadata"]["core_mission"] == "Automate complex multi-step workflows"

    test_file.unlink()


