import os
import streamlit as st
import pandas as pd
from typing import Any
from pydantic import ValidationError

from promptops.validation import WorkflowSchema
from studio.helpers import (
    render_schema_form, 
    load_asset_data, 
    validate_and_save_asset,
    get_relative_asset_paths,
    render_shared_list
)
from promptops.utils import ROOT, load_yaml

st.set_page_config(page_title="Workflow Editor", layout="wide")
st.title("Workflow Editor")

base_dir = str(ROOT)
workflow_files = get_relative_asset_paths("workflow")
prompt_files = get_relative_asset_paths("prompt", extensions=[".prompt.md"])

selected_file = st.selectbox("Select a workflow to edit", ["Create New..."] + workflow_files)

# Define field-to-tab mappings for validation error routing
field_to_tab_wf = {
    "name": "Workflow Details",
    "description": "Workflow Details",
    "metadata": "Workflow Details",
    "inputs": "Workflow Details",
    "steps": "Workflow Steps",
    "testData": "Test Data"
}

def show_tab_errors_wf(tab_name: str):
    if 'wf_validation_errors' in st.session_state and st.session_state['wf_validation_errors']:
        errors = st.session_state['wf_validation_errors']
        tab_errors = []
        for err in errors:
            loc = err.get('loc', [])
            if loc:
                root_field = loc[0]
                if field_to_tab_wf.get(root_field) == tab_name:
                    loc_str = " -> ".join(str(x) for x in loc)
                    tab_errors.append(f"**{loc_str}**: {err.get('msg')}")
        if tab_errors:
            st.error("Validation issues found in this tab:\n" + "\n".join(f"- {msg}" for msg in tab_errors))

if selected_file == "Create New...":
    st.subheader("Create New Workflow")
    new_file_path = st.text_input("File Path (e.g., workflows/my_workflow.workflow.yaml)")
    data: dict[str, Any] = {
        "name": "",
        "description": "",
        "metadata": {
            "domain": "general",
            "topic": "general",
            "status": "active"
        },
        "inputs": [],
        "steps": [],
        "testData": []
    }
else:
    new_file_path = selected_file
    file_path = os.path.join(base_dir, selected_file)
    data = load_asset_data(file_path)
    if not data:
        st.stop()
st.subheader(f"Editing: {selected_file}")

# Initialize session state lists/dicts for complex fields
if 'wf_current_file' not in st.session_state or st.session_state.get('wf_current_file') != selected_file:
    st.session_state['wf_inputs'] = data.get('inputs', [])
    st.session_state['wf_steps'] = data.get('steps', [])
    st.session_state['wf_testData'] = data.get('testData', []) or []
    st.session_state['wf_current_file'] = selected_file
    st.session_state['wf_validation_errors'] = []

def get_prompt_variables(prompt_file_path):
    full_path = os.path.join(base_dir, prompt_file_path)
    p_data = load_yaml(full_path)
    return [v.get('name') for v in p_data.get('variables', [])] if p_data else []

# Define visual tabs for the Workflow Editor
wf_tabs = st.tabs(["Workflow Details", "Workflow Steps", "Test Data"])

# ----------------- TAB 1: Workflow Details -----------------
with wf_tabs[0]:
    show_tab_errors_wf("Workflow Details")
    st.subheader("Workflow Configuration")
    
    # Render basic standard fields using layout configuration mapping (Requirement 1)
    skip_fields = ["inputs", "steps", "testData"]
    layout_config_wf = {
        "General Info": ["name", "description"],
        "Metadata Settings": ["metadata"]
    }
    
    data = render_schema_form(
        WorkflowSchema, 
        data, 
        skip_fields=skip_fields, 
        layout_config=layout_config_wf, 
        layout_type="expanders"
    )
    
    st.subheader("Global Inputs")
    inputs_df = pd.DataFrame(st.session_state['wf_inputs']) if st.session_state['wf_inputs'] else pd.DataFrame(columns=["name", "description"])
    edited_inputs_df = st.data_editor(inputs_df, num_rows="dynamic", key="wf_inputs_editor")

# Collect available output variables from previous steps and global inputs
def get_available_mappings(current_step_index):
    options = [""]
    # Global inputs
    for idx, row in edited_inputs_df.iterrows():
        if pd.notna(row.get('name')):
            options.append(f"{{{{inputs.{row['name']}}}}}")
    
    # Previous steps outputs
    for i in range(current_step_index):
        s_id = st.session_state['wf_steps'][i].get('step_id')
        if s_id:
            options.append(f"{{{{steps.{s_id}.output}}}}")
            
    return options

# ----------------- TAB 2: Workflow Steps -----------------
with wf_tabs[1]:
    show_tab_errors_wf("Workflow Steps")
    st.subheader("Workflow Steps & Visualizer")
    
    def render_workflow_step_item(i, step):
        with st.expander(f"Step {i+1}: {step.get('step_id', 'Un-named')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                step_id = st.text_input(f"Step ID", value=step.get('step_id', ''), key=f"step_id_{i}")
                st.session_state['wf_steps'][i]['step_id'] = step_id
            with col2:
                prompt_idx = 0
                if step.get('prompt_file') in prompt_files:
                    prompt_idx = prompt_files.index(step.get('prompt_file'))
                prompt_file = st.selectbox(f"Prompt File", prompt_files, index=prompt_idx, key=f"prompt_file_{i}")
                st.session_state['wf_steps'][i]['prompt_file'] = prompt_file
                
            st.markdown("**Map Inputs (Live Variable Mapping)**")
            required_vars = get_prompt_variables(prompt_file)
            
            if 'map_inputs' not in st.session_state['wf_steps'][i]:
                st.session_state['wf_steps'][i]['map_inputs'] = {}
                
            map_inputs = st.session_state['wf_steps'][i]['map_inputs']
            available_mappings = get_available_mappings(i)
            
            for req_var in required_vars:
                current_val = map_inputs.get(req_var, "")
                
                mapping_col1, mapping_col2 = st.columns(2)
                with mapping_col1:
                    st.markdown(f"`{req_var}`")
                with mapping_col2:
                    options = list(available_mappings)
                    if current_val and current_val not in options:
                        options.append(current_val)
                        
                    sel_index = options.index(current_val) if current_val in options else 0
                    selected_mapping = st.selectbox(f"Map for {req_var}", options, index=sel_index, key=f"map_{i}_{req_var}")
                    st.session_state['wf_steps'][i]['map_inputs'][req_var] = selected_mapping
                    
            st.markdown("**Step Transitions (Next)**")
            if 'next' not in st.session_state['wf_steps'][i]:
                st.session_state['wf_steps'][i]['next'] = []
                
            next_edges = st.session_state['wf_steps'][i]['next']
            if not isinstance(next_edges, list):
                if isinstance(next_edges, str):
                    next_edges = [{"target": next_edges}]
                else:
                    next_edges = []
                st.session_state['wf_steps'][i]['next'] = next_edges
                
            for e_idx, edge in enumerate(next_edges):
                ecol1, ecol2, ecol3, ecol4 = st.columns([3, 2, 3, 1])
                
                from promptops.validation import TransitionConstraint
                condition_str = edge.get("condition", "")
                
                constraint = TransitionConstraint.from_jinja_expression(condition_str)
                cond_var = constraint.variable or ""
                cond_op = constraint.operator
                cond_val = constraint.value or ""
                
                with ecol1:
                    if cond_op == "Custom Jinja2":
                        st.text_input("Custom Condition", value=cond_val, key=f"cond_custom_{i}_{e_idx}", disabled=True)
                    else:
                        target_var = st.selectbox("Condition Source", [""] + available_mappings, index=(available_mappings.index(f"{{{{{cond_var}}}}}") if f"{{{{{cond_var}}}}}" in available_mappings else 0) if cond_var else 0, key=f"cond_src_{i}_{e_idx}")
                with ecol2:
                    selected_op = st.selectbox("Operator", ["Always", "==", "!=", ">", "<", "Custom Jinja2"], index=["Always", "==", "!=", ">", "<", "Custom Jinja2"].index(cond_op) if cond_op in ["Always", "==", "!=", ">", "<", "Custom Jinja2"] else 0, key=f"cond_op_{i}_{e_idx}")
                with ecol3:
                    if selected_op not in ["Always", "Custom Jinja2"]:
                        selected_val = st.text_input("Value", value=cond_val, key=f"cond_val_{i}_{e_idx}")
                        if target_var:
                            stripped_var = target_var.replace("{{", "").replace("}}", "")
                            new_constraint = TransitionConstraint(variable=stripped_var, operator=selected_op, value=selected_val)
                            st.session_state['wf_steps'][i]['next'][e_idx]["condition"] = new_constraint.to_jinja_expression()
                    elif selected_op == "Always":
                        if "condition" in st.session_state['wf_steps'][i]['next'][e_idx]:
                            del st.session_state['wf_steps'][i]['next'][e_idx]["condition"]
                            
                with ecol4:
                    all_step_ids = [s.get("step_id") for s in st.session_state['wf_steps'] if s.get("step_id")]
                    target_idx = all_step_ids.index(edge.get("target")) if edge.get("target") in all_step_ids else 0
                    selected_target = st.selectbox("Target", all_step_ids, index=target_idx if all_step_ids else 0, key=f"cond_tgt_{i}_{e_idx}")
                    st.session_state['wf_steps'][i]['next'][e_idx]["target"] = selected_target

            if st.button("Add Branch", key=f"add_branch_{i}"):
                st.session_state['wf_steps'][i]['next'].append({"target": ""})
                st.rerun()

    key_patterns = [
        "step_id_{}",
        "prompt_file_{}",
        "map_{}_",
        "cond_custom_{}_",
        "cond_src_{}_",
        "cond_op_{}_",
        "cond_val_{}_",
        "cond_tgt_{}_",
    ]
    render_shared_list(
        session_state_key="wf_steps",
        item_renderer=render_workflow_step_item,
        key_patterns=key_patterns,
        col_widths=[8.5, 1.5]
    )

    if st.button("Add Step"):
        st.session_state['wf_steps'].append({"step_id": f"step_{len(st.session_state['wf_steps'])+1}", "prompt_file": prompt_files[0] if prompt_files else "", "map_inputs": {}})
        st.rerun()

    st.subheader("Visualizer")
    steps = st.session_state['wf_steps']
    if steps:
        try:
            from promptops.validation import WorkflowSchema
            from promptops.visualization import MermaidGrapher
            from streamlit_mermaid import st_mermaid
            
            temp_data = dict(data)
            temp_data['inputs'] = edited_inputs_df.to_dict('records')
            temp_data['steps'] = steps
            wf = WorkflowSchema(**temp_data)
            mermaid_code = MermaidGrapher.generate(wf)
            if mermaid_code:
                st_mermaid(mermaid_code, height=500)
            else:
                st.info("Graph is empty.")
        except ImportError:
            st.warning("Visualizer package is missing. The Workflow Editor remains functional, but graph rendering is disabled.")
            st.info("To enable graph visualizations, please install the visualizer extra: `pip install .[visualizer]`")
        except Exception as e:
            st.warning(f"Could not generate visualizer yet: {e}")
    else:
        st.info("No steps defined yet.")

# ----------------- TAB 3: Test Data -----------------
with wf_tabs[2]:
    show_tab_errors_wf("Test Data")
    st.subheader("Workflow-level Test Data (Requirement 4)")
    
    if st.button("➕ Add Workflow Test Case", key="add_wf_tc"):
        st.session_state['wf_testData'].append({"inputs": {}})
        st.rerun()
        
    for idx, tc in enumerate(st.session_state['wf_testData']):
        with st.expander(f"📁 Test Case {idx+1}", expanded=True):
            col1, col2 = st.columns([8, 2])
            with col2:
                if st.button("🗑️ Remove Test Case", key=f"remove_wf_tc_{idx}"):
                    st.session_state['wf_testData'].pop(idx)
                    st.rerun()
                    
            with col1:
                st.markdown("**Global Inputs Mapping**")
                tc_inputs = tc.get('inputs', tc.get('vars', {})) or {}
                updated_inputs = {}
                
                # Fetch currently defined global inputs
                global_inputs_list = []
                for index, row in edited_inputs_df.iterrows():
                    name = row.get('name')
                    if pd.notna(name) and str(name).strip():
                        global_inputs_list.append(str(name).strip())
                        
                if not global_inputs_list:
                    st.info("No global inputs defined. Define global inputs in the 'Workflow Details' tab first.")
                else:
                    for inp in global_inputs_list:
                        updated_inputs[inp] = st.text_input(
                            f"Value for global input: `{inp}`",
                            value=str(tc_inputs.get(inp, "")),
                            key=f"wf_tc_{idx}_{inp}"
                        )
                st.session_state['wf_testData'][idx]['inputs'] = updated_inputs

    st.markdown("---")
    st.markdown("### Read-Only Test Data JSON Preview")
    st.json(st.session_state['wf_testData'])

# Global Save Button (Primary action)
st.markdown("---")
if st.button("Save Workflow", type="primary"):
    if not new_file_path.endswith('.workflow.yaml') and not new_file_path.endswith('.workflow.yml'):
        st.error("File path must end with .workflow.yaml or .workflow.yml")
    else:
        # Reconcile state back to the data schema (Requirement 5)
        data['inputs'] = edited_inputs_df.to_dict('records')
        data['steps'] = st.session_state['wf_steps']
        data['testData'] = st.session_state['wf_testData'] if st.session_state['wf_testData'] else None
        
        try:
            # Perform strict local Pydantic validation first
            WorkflowSchema(**data)
            
            # Clear previous session state errors on success
            st.session_state['wf_validation_errors'] = []
            
            full_path = os.path.join(base_dir, new_file_path)
            if validate_and_save_asset(full_path, data, WorkflowSchema, success_message="Saved workflow successfully and validated!"):
                st.rerun()
        except ValidationError as e:
            st.session_state['wf_validation_errors'] = e.errors()
            st.error("Validation failed. Please inspect the dynamic error messages in individual tabs.")
            st.rerun()
