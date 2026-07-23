import os
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from pydantic import ValidationError

from promptops.validation import PromptSchema
from studio.helpers import (
    render_schema_form, 
    load_asset_data, 
    validate_and_save_asset,
    get_relative_asset_paths,
    render_shared_list
)
from promptops.utils import ROOT

st.set_page_config(page_title="Prompt Editor", layout="wide")
st.title("Prompt Editor")

base_dir = str(ROOT)
prompt_files = get_relative_asset_paths("prompt", extensions=[".prompt.md"])

selected_file = st.selectbox("Select a prompt to edit", ["Create New..."] + prompt_files)

# Define field-to-tab mappings for validation error routing
field_to_tab = {
    "name": "Details & Variables",
    "version": "Details & Variables",
    "description": "Details & Variables",
    "metadata": "Details & Variables",
    "model": "Details & Variables",
    "modelParameters": "Details & Variables",
    "variables": "Details & Variables",
    "messages": "Messages",
    "tools": "MCP Tools",
    "output_schema": "Output Schema",
    "testData": "Test Data & Evaluators",
    "evaluators": "Test Data & Evaluators"
}

def show_tab_errors(tab_name: str):
    if 'validation_errors' in st.session_state and st.session_state['validation_errors']:
        errors = st.session_state['validation_errors']
        tab_errors = []
        for err in errors:
            loc = err.get('loc', [])
            if loc:
                root_field = loc[0]
                if field_to_tab.get(root_field) == tab_name:
                    loc_str = " -> ".join(str(x) for x in loc)
                    tab_errors.append(f"**{loc_str}**: {err.get('msg')}")
        if tab_errors:
            st.error("Validation issues found in this tab:\n" + "\n".join(f"- {msg}" for msg in tab_errors))

# Helpers for MCP tool schema flat-mapping
def mcp_to_flat_params(tool_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    input_schema = tool_data.get("inputSchema", {}) or {}
    properties = input_schema.get("properties", {}) or {}
    required_list = input_schema.get("required", []) or []
    
    flat_params = []
    for k, v in properties.items():
        flat_params.append({
            "name": k,
            "type": v.get("type", "string"),
            "description": v.get("description", ""),
            "required": k in required_list
        })
    return flat_params

def flat_params_to_mcp(flat_params: List[Dict[str, Any]]) -> Dict[str, Any]:
    properties = {}
    required = []
    for p in flat_params:
        p_name = p.get("name")
        if p_name and str(p_name).strip():
            p_name = str(p_name).strip()
            properties[p_name] = {
                "type": p.get("type", "string"),
                "description": p.get("description", "")
            }
            if p.get("required"):
                required.append(p_name)
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }

# Helpers for Output Schema flat-mapping
def output_schema_to_flat(schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    properties = schema_data.get("properties", {}) or {}
    required_list = schema_data.get("required", []) or []
    
    flat_params = []
    for k, v in properties.items():
        flat_params.append({
            "key": k,
            "type": v.get("type", "string"),
            "description": v.get("description", ""),
            "required": k in required_list
        })
    return flat_params

def flat_to_output_schema(flat_params: List[Dict[str, Any]]) -> Dict[str, Any]:
    properties = {}
    required = []
    for p in flat_params:
        p_name = p.get("key") or p.get("name")
        if p_name and str(p_name).strip():
            p_name = str(p_name).strip()
            properties[p_name] = {
                "type": p.get("type", "string"),
                "description": p.get("description", "")
            }
            if p.get("required"):
                required.append(p_name)
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }

if selected_file == "Create New...":
    st.subheader("Create New Prompt")
    new_file_path = st.text_input("File Path (e.g., prompts/my_prompt.prompt.md)")
    data: Dict[str, Any] = {
        "name": "",
        "version": "0.1.0",
        "description": "",
        "metadata": {
            "domain": "general",
            "complexity": "low",
            "tags": ["skill"],
            "status": "active"
        },
        "model": "gpt-4",
        "modelParameters": {"temperature": 0.1, "max_tokens": 1000},
        "variables": [{"name": "input", "description": "User input", "required": True}],
        "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "{{input}}"}],
        "testData": [{"inputs": {"input": "test"}, "expected": "Output"}],
        "evaluators": []
    }
else:
    new_file_path = selected_file
    file_path = os.path.join(base_dir, selected_file)
    data = load_asset_data(file_path)
    if not data:
        st.stop()
st.subheader(f"Editing: {selected_file}")

# Initialize session state lists/dicts for complex fields
if 'current_file' not in st.session_state or st.session_state['current_file'] != selected_file:
    st.session_state['current_file'] = selected_file
    st.session_state['messages'] = data.get('messages', [])
    st.session_state['tools'] = data.get('tools', []) or []
    st.session_state['output_schema'] = data.get('output_schema', {}) or {}
    st.session_state['testData'] = data.get('testData', [])
    st.session_state['evaluators'] = data.get('evaluators', [])
    st.session_state['validation_errors'] = []

# Define main visual tabs for the visual prompt editor
main_tabs = st.tabs(["Details & Variables", "Messages", "MCP Tools", "Output Schema", "Test Data & Evaluators"])

# ----------------- TAB 1: Details & Variables -----------------
with main_tabs[0]:
    show_tab_errors("Details & Variables")
    st.subheader("Details & Variables")
    
    # Render basic standard fields using layout configuration mapping (Requirement 1)
    skip_fields = ["variables", "messages", "testData", "evaluators", "modelParameters", "tools", "output_schema", "last_modified"]
    layout_config_basic = {
        "General Info": ["name", "version", "description"],
        "Metadata Settings": ["metadata"],
        "System Options": ["safety_opt_out"]
    }
    
    data = render_schema_form(
        PromptSchema, 
        data, 
        skip_fields=skip_fields, 
        layout_config=layout_config_basic, 
        layout_type="expanders"
    )
    
    st.subheader("Model Parameters")
    model_params = data.get('modelParameters', {})
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.number_input("Temperature", min_value=0.0, max_value=2.0, value=float(model_params.get('temperature', 0.1)), step=0.1)
    with col2:
        max_tokens = st.number_input("Max Tokens", min_value=1, value=int(model_params.get('max_tokens', 1000)), step=100)
    
    st.subheader("Variables")
    variables = data.get('variables', [])
    var_df = pd.DataFrame(variables) if variables else pd.DataFrame(columns=["name", "description", "required"])
    edited_var_df = st.data_editor(var_df, num_rows="dynamic", key="var_editor")

# ----------------- TAB 2: Messages -----------------
with main_tabs[1]:
    show_tab_errors("Messages")
    st.subheader("Messages")
    
    def render_message_item(i, msg):
        col_role, col_text = st.columns([2, 8])
        with col_role:
            st.session_state['messages'][i]['role'] = st.selectbox(f"Role {i}", ["system", "user", "assistant"], index=["system", "user", "assistant"].index(msg.get('role', 'user')), key=f"role_{i}")
        with col_text:
            st.session_state['messages'][i]['content'] = st.text_area(f"Content {i}", value=msg.get('content', ''), key=f"content_{i}")
            
            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 6])
            if btn_col1.button("✨ Optimize", key=f"opt_{i}"):
                st.session_state[f"show_opt_diff_{i}"] = True
                st.session_state[f"show_san_diff_{i}"] = False
            if btn_col2.button("🧹 Sanitize", key=f"san_{i}"):
                st.session_state[f"show_san_diff_{i}"] = True
                st.session_state[f"show_opt_diff_{i}"] = False
                
            if st.session_state.get(f"show_opt_diff_{i}"):
                st.markdown("**Optimization Proposed Changes (Side-by-Side):**")
                diff_col1, diff_col2 = st.columns(2)
                original = st.session_state['messages'][i]['content']
                from promptops.utils import optimize_prompt
                proposed = optimize_prompt(original)
                
                with diff_col1:
                    st.text_area("Original", value=original, disabled=True, key=f"orig_opt_{i}", height=150)
                with diff_col2:
                    st.text_area("Optimized", value=proposed, disabled=True, key=f"prop_opt_{i}", height=150)
                    
                ac_col1, ac_col2, _ = st.columns([2, 2, 6])
                if ac_col1.button("✅ Accept", key=f"acc_opt_{i}"):
                    st.session_state['messages'][i]['content'] = proposed
                    st.session_state[f"content_{i}"] = proposed
                    st.session_state[f"show_opt_diff_{i}"] = False
                    st.rerun()
                if ac_col2.button("❌ Reject", key=f"rej_opt_{i}"):
                    st.session_state[f"show_opt_diff_{i}"] = False
                    st.rerun()

            if st.session_state.get(f"show_san_diff_{i}"):
                st.markdown("**Sanitization Proposed Changes (Side-by-Side):**")
                diff_col1, diff_col2 = st.columns(2)
                original = st.session_state['messages'][i]['content']
                from promptops.utils import sanitize_prompt
                proposed = sanitize_prompt(original)
                
                with diff_col1:
                    st.text_area("Original", value=original, disabled=True, key=f"orig_san_{i}", height=150)
                with diff_col2:
                    st.text_area("Sanitized", value=proposed, disabled=True, key=f"prop_san_{i}", height=150)
                    
                ac_col1, ac_col2, _ = st.columns([2, 2, 6])
                if ac_col1.button("✅ Accept", key=f"acc_san_{i}"):
                    st.session_state['messages'][i]['content'] = proposed
                    st.session_state[f"content_{i}"] = proposed
                    st.session_state[f"show_san_diff_{i}"] = False
                    st.rerun()
                if ac_col2.button("❌ Reject", key=f"rej_san_{i}"):
                    st.session_state[f"show_san_diff_{i}"] = False
                    st.rerun()

    key_patterns = [
        "role_{}",
        "content_{}",
        "show_opt_diff_{}",
        "show_san_diff_{}",
        "orig_opt_{}",
        "prop_opt_{}",
        "orig_san_{}",
        "prop_san_{}",
        "acc_opt_{}",
        "rej_opt_{}",
        "acc_san_{}",
        "rej_san_{}",
    ]
    render_shared_list(
        session_state_key="messages",
        item_renderer=render_message_item,
        key_patterns=key_patterns,
        col_widths=[8.5, 1.5]
    )

    if st.button("Add Message"):
        st.session_state['messages'].append({"role": "user", "content": ""})
        st.rerun()

# ----------------- TAB 3: MCP Tools -----------------
with main_tabs[2]:
    show_tab_errors("MCP Tools")
    st.subheader("MCP-Compliant Tools Editor")
    
    if st.button("➕ Add MCP Tool"):
        st.session_state['tools'].append({
            "name": f"new_tool_{len(st.session_state['tools']) + 1}",
            "description": "",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        })
        st.rerun()
        
    for i, tool in enumerate(st.session_state['tools']):
        with st.expander(f"🛠️ Tool {i+1}: {tool.get('name', 'Unnamed Tool')}", expanded=True):
            col1, col2 = st.columns([8, 2])
            with col1:
                tool_name = st.text_input("Tool Name", value=tool.get('name', ''), key=f"tool_name_{i}")
                st.session_state['tools'][i]['name'] = tool_name
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Remove Tool", key=f"del_tool_{i}"):
                    st.session_state['tools'].pop(i)
                    st.rerun()
                    
            tool_desc = st.text_area("Tool Description", value=tool.get('description', ''), key=f"tool_desc_{i}")
            st.session_state['tools'][i]['description'] = tool_desc
            
            flat_params = mcp_to_flat_params(tool)
            df_params = pd.DataFrame(flat_params) if flat_params else pd.DataFrame(columns=["name", "type", "description", "required"])
            
            st.markdown("**Parameters (Properties)**")
            edited_tool_df = st.data_editor(
                df_params,
                num_rows="dynamic",
                key=f"tool_params_editor_{i}",
                column_config={
                    "type": st.column_config.SelectboxColumn(
                        options=["string", "number", "integer", "boolean", "array", "object"]
                    )
                }
            )
            
            # Update MCP schema on edit
            updated_flat = edited_tool_df.to_dict('records')
            st.session_state['tools'][i]['inputSchema'] = flat_params_to_mcp(updated_flat)

    st.markdown("---")
    st.markdown("### Read-Only Tools JSON Preview")
    st.json(st.session_state['tools'])

# ----------------- TAB 4: Output Schema -----------------
with main_tabs[3]:
    show_tab_errors("Output Schema")
    st.subheader("Output Schema Configuration")
    
    has_output_schema = st.checkbox("Enforce Structured Output Schema", value=bool(st.session_state['output_schema']), key="has_output_schema_chk")
    
    if has_output_schema:
        if not st.session_state['output_schema'] or st.session_state['output_schema'].get("type") != "object":
            st.session_state['output_schema'] = {"type": "object", "properties": {}, "required": []}
            
        flat_os = output_schema_to_flat(st.session_state['output_schema'])
        df_os = pd.DataFrame(flat_os) if flat_os else pd.DataFrame(columns=["key", "type", "description", "required"])
        
        st.markdown("Define the expected properties in the JSON response:")
        edited_os_df = st.data_editor(
            df_os,
            num_rows="dynamic",
            key="output_schema_editor",
            column_config={
                "type": st.column_config.SelectboxColumn(
                    options=["string", "number", "integer", "boolean", "array", "object"]
                )
            }
        )
        
        updated_os_flat = edited_os_df.to_dict('records')
        st.session_state['output_schema'] = flat_to_output_schema(updated_os_flat)
    else:
        st.session_state['output_schema'] = None
        
    st.markdown("---")
    st.markdown("### Read-Only Output Schema JSON Preview")
    if st.session_state['output_schema']:
        st.json(st.session_state['output_schema'])
    else:
        st.info("No output schema defined.")

# ----------------- TAB 5: Test Data & Evaluators -----------------
with main_tabs[4]:
    show_tab_errors("Test Data & Evaluators")
    st.subheader("Test Data & Evaluators")
    
    st.markdown("### Test Data")
    for i, td in enumerate(st.session_state['testData']):
        with st.expander(f"Test Case {i+1}", expanded=True):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                st.markdown("**Inputs**")
                inputs_json = td.get('inputs', td.get('input', {}))
                
                updated_inputs = {}
                for var in data.get('variables', []):
                    var_name = var.get('name')
                    if var_name:
                        updated_inputs[var_name] = st.text_input(f"{var_name}", value=inputs_json.get(var_name, ""), key=f"td_inputs_{i}_{var_name}")
                
                if 'input' in td:
                    st.session_state['testData'][i]['input'] = updated_inputs
                else:
                    st.session_state['testData'][i]['inputs'] = updated_inputs
            with col2:
                st.session_state['testData'][i]['expected'] = st.text_area(f"Expected Output", value=str(td.get('expected', '')), key=f"td_expected_{i}")
            with col3:
                if st.button("X", key=f"del_td_{i}"):
                    st.session_state['testData'].pop(i)
                    st.rerun()

    if st.button("Add Test Case"):
        st.session_state['testData'].append({"inputs": {}, "expected": ""})
        st.rerun()

    st.markdown("### Evaluators")
    for i, ev in enumerate(st.session_state['evaluators']):
        with st.expander(f"Evaluator: {ev.get('name', 'New')}", expanded=True):
            col1, col2, col3 = st.columns([3, 6, 1])
            with col1:
                st.session_state['evaluators'][i]['name'] = st.text_input(f"Name", value=ev.get('name', ''), key=f"ev_name_{i}")
            with col2:
                st.markdown("**Logic Builder**")
                
                from promptops.validation import EvaluatorRule
                
                py_logic = ev.get('python', '')
                rule = EvaluatorRule.from_python_expression(py_logic)
                eval_type = rule.rule_type
                eval_value = rule.value
                
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    sel_type = st.selectbox("Rule Type", ["Contains", "Does Not Contain", "Regex Match", "Length >", "Length <", "Custom Python"], index=["Contains", "Does Not Contain", "Regex Match", "Length >", "Length <", "Custom Python"].index(eval_type) if eval_type in ["Contains", "Does Not Contain", "Regex Match", "Length >", "Length <", "Custom Python"] else 5, key=f"ev_type_{i}")
                
                with subcol2:
                    if sel_type != "Custom Python":
                        val = st.text_input("Value", value=eval_value, key=f"ev_val_{i}")
                        new_rule = EvaluatorRule(rule_type=sel_type, value=val)
                        st.session_state['evaluators'][i]['python'] = new_rule.to_python_expression()
                    else:
                        st.session_state['evaluators'][i]['python'] = st.text_area("Custom Python", value=py_logic, key=f"ev_py_{i}")
            with col3:
                if st.button("X", key=f"del_ev_{i}"):
                    st.session_state['evaluators'].pop(i)
                    st.rerun()

    if st.button("Add Evaluator"):
        st.session_state['evaluators'].append({"name": "", "python": ""})
        st.rerun()

# Global Save Button (Primary action)
st.markdown("---")
if st.button("Save Changes", type="primary"):
    if not new_file_path.endswith('.prompt.md'):
        st.error("File path must end with .prompt.md")
    else:
        # Construct parameters and list editors back into the main dataset (Requirement 5)
        data['modelParameters'].update({"temperature": temperature, "max_tokens": max_tokens})
        data['variables'] = edited_var_df.to_dict('records')
        data['messages'] = st.session_state['messages']
        data['tools'] = st.session_state['tools'] if st.session_state['tools'] else None
        data['output_schema'] = st.session_state['output_schema'] if st.session_state['output_schema'] else None
        data['testData'] = st.session_state['testData']
        data['evaluators'] = st.session_state['evaluators']
        
        try:
            # Perform strict local Pydantic validation first
            PromptSchema(**data)
            
            # Clear previous session state errors on success
            st.session_state['validation_errors'] = []
            
            # Save and notify
            full_path = os.path.join(base_dir, new_file_path)
            if validate_and_save_asset(full_path, data, PromptSchema, success_message="Saved successfully and validated!"):
                st.rerun()
        except ValidationError as e:
            st.session_state['validation_errors'] = e.errors()
            st.error("Validation failed. Please inspect the dynamic error messages in individual tabs.")
            st.rerun()
