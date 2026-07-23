import os
import streamlit as st
from typing import Dict, Any, Type, List, Callable
from pydantic import BaseModel, ValidationError
import json

from promptops.utils import ROOT, iter_prompt_files, iter_workflow_files, load_yaml, save_yaml

def get_relative_asset_paths(asset_type: str, extensions: List[str] = None) -> list[str]:
    """
    Scans the workspace for prompt or workflow files, returning a sorted list of relative paths.
    Conforms to the standard workspace traverser.
    """
    base_dir = str(ROOT)
    if asset_type.lower() == "prompt":
        files = list(iter_prompt_files())
    elif asset_type.lower() == "workflow":
        files = list(iter_workflow_files())
    else:
        raise ValueError(f"Unknown asset type: {asset_type}")
        
    if extensions:
        files = [f for f in files if any(str(f).endswith(ext) for ext in extensions)]
    
    return sorted([os.path.relpath(str(f), base_dir) for f in files])

def render_file_selector(asset_type: str, key: str, label: str = None, extensions: List[str] = None) -> str:
    """
    Renders a unified selectbox for prompt or workflow files using relative paths.
    """
    paths = get_relative_asset_paths(asset_type, extensions=extensions)
    if not label:
        label = f"Select a {asset_type.lower()} file"
    return st.selectbox(label, options=paths, key=key)

def render_schema_form(
    schema_class: Type[BaseModel],
    data: Dict[str, Any],
    skip_fields: List[str] = None,
    key_prefix: str = "",
    layout_config: Dict[str, List[str]] = None,
    layout_type: str = "tabs"
) -> Dict[str, Any]:
    """
    Dynamically generates Streamlit inputs from a Pydantic model's JSON schema.
    Can accept a layout configuration mapping to render fields inside tabs or collapsible sections.
    """
    if skip_fields is None:
        skip_fields = []
        
    schema = schema_class.model_json_schema()
    properties = schema.get("properties", {})
    
    def render_field(field_name: str, field_info: Dict[str, Any], data_dict: Dict[str, Any]) -> Any:
        val = data_dict.get(field_name, "")
        
        # Determine the label to use
        if "title" in field_info:
            label = field_info["title"]
        elif "description" in field_info and field_info["description"]:
            label = field_info["description"]
        else:
            label = field_name
            
        if field_name == "metadata":
            st.subheader("Metadata")
            if "metadata" not in data_dict or not data_dict["metadata"]:
                data_dict["metadata"] = {}
                
            meta_schema = {}
            if "$defs" in schema:
                for def_name, def_schema in schema["$defs"].items():
                    if "Metadata" in def_name:
                        meta_schema = def_schema.get("properties", {})
                        break
                        
            for m_key, m_info in meta_schema.items():
                m_val = data_dict["metadata"].get(m_key, m_info.get("default", ""))
                m_label = m_info.get("title", m_key)
                if m_info.get("type") == "boolean":
                    data_dict["metadata"][m_key] = st.checkbox(m_label, value=bool(m_val), key=f"{key_prefix}meta_{m_key}")
                elif m_info.get("type") == "array":
                    m_val_str = ", ".join(m_val) if isinstance(m_val, list) else ""
                    res = st.text_input(m_label, value=m_val_str, key=f"{key_prefix}meta_{m_key}")
                    data_dict["metadata"][m_key] = [x.strip() for x in res.split(",") if x.strip()]
                else:
                    data_dict["metadata"][m_key] = st.text_input(m_label, value=m_val, key=f"{key_prefix}meta_{m_key}")
        elif field_info.get("type") == "string":
            if field_name == "description" or "description" in field_name.lower():
                data_dict[field_name] = st.text_area(label, value=val, key=f"{key_prefix}{field_name}")
            else:
                data_dict[field_name] = st.text_input(label, value=val, key=f"{key_prefix}{field_name}")
        elif field_info.get("type") == "boolean":
            data_dict[field_name] = st.checkbox(label, value=bool(val), key=f"{key_prefix}{field_name}")
            
        return data_dict

    if layout_config:
        if layout_type == "tabs":
            tabs = st.tabs(list(layout_config.keys()))
            for tab, (tab_name, fields) in zip(tabs, layout_config.items()):
                with tab:
                    for field_name in fields:
                        if field_name in skip_fields or field_name not in properties:
                            continue
                        data = render_field(field_name, properties[field_name], data)
        else: # collapsible / expanders
            for section_title, fields in layout_config.items():
                with st.expander(section_title, expanded=True):
                    for field_name in fields:
                        if field_name in skip_fields or field_name not in properties:
                            continue
                        data = render_field(field_name, properties[field_name], data)
    else:
        for field_name, field_info in properties.items():
            if field_name in skip_fields:
                continue
            data = render_field(field_name, field_info, data)
            
    return data

def load_asset_data(file_path: str, raw: bool = True) -> Dict[str, Any]:
    """Loads and returns YAML data. Standardizes error displays."""
    try:
        if os.path.exists(file_path):
            return load_yaml(file_path, raw=raw) or {}
    except Exception as e:
        st.error(f"Failed to load file: {e}")
    return {}

def validate_and_save_asset(
    file_path: str,
    data: Dict[str, Any],
    schema_class: Type[BaseModel],
    save_callback: Callable = None,
    success_message: str = None
) -> bool:
    """
    Validates data against the Pydantic schema_class.
    If valid, saves/serializes YAML to disk, or runs the custom save_callback (if any).
    Displays success/error notifications to the user in a consistent Streamlit banner style.
    """
    try:
        # Validate using Pydantic model instantiation
        schema_class(**data)
        
        # Save operation
        if save_callback:
            save_callback(file_path, data)
        else:
            save_yaml(file_path, data)
            
        msg = success_message or f"Successfully saved and validated {os.path.basename(file_path)}!"
        st.success(msg)
        return True
    except json.JSONDecodeError as e:
        st.error(f"JSON Parsing Error: {e}")
        return False
    except ValidationError as e:
        st.error("Validation Error: " + str(e))
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def _get_all_matching_templates(indices: List[int], key_patterns: List[str]) -> List[str]:
    """Finds all key templates currently present in session state for any of the given indices."""
    import streamlit as st
    templates = set()
    for idx in indices:
        for key in list(st.session_state.keys()):
            for pattern in key_patterns:
                if "{}" in pattern:
                    prefix_part, suffix_part = pattern.split("{}", 1)
                    if key.startswith(prefix_part):
                        expected_prefix = prefix_part + str(idx)
                        if key.startswith(expected_prefix):
                            dynamic_suffix = key[len(expected_prefix):]
                            # Make sure the dynamic suffix matches suffix_part if there is one
                            if suffix_part == "" or dynamic_suffix.startswith(suffix_part):
                                templates.add(prefix_part + "{}" + dynamic_suffix)
                else:
                    # Pattern is a simple prefix
                    if key.startswith(f"{pattern}{idx}_") or key == f"{pattern}{idx}":
                        suffix = key[len(f"{pattern}{idx}"):]
                        templates.add(f"{pattern}{{}}{suffix}")
    return list(templates)


def _swap_session_keys(i: int, j: int, key_patterns: List[str]):
    """Swaps keys in st.session_state matching format patterns for indices i and j."""
    import streamlit as st
    templates = _get_all_matching_templates([i, j], key_patterns)
    for template in templates:
        key_i = template.format(i)
        key_j = template.format(j)
        val_i = st.session_state.get(key_i, None)
        val_j = st.session_state.get(key_j, None)
        
        if val_j is not None:
            st.session_state[key_i] = val_j
        elif key_i in st.session_state:
            del st.session_state[key_i]
            
        if val_i is not None:
            st.session_state[key_j] = val_i
        elif key_j in st.session_state:
            del st.session_state[key_j]


def _delete_session_keys(i: int, length: int, key_patterns: List[str]):
    """Shifts keys matching format patterns down when item at index i is deleted."""
    import streamlit as st
    # Find all templates for all possible indices in the list
    templates = _get_all_matching_templates(list(range(length)), key_patterns)
    
    for idx in range(i, length - 1):
        for template in templates:
            key_curr = template.format(idx)
            key_next = template.format(idx + 1)
            if key_next in st.session_state:
                st.session_state[key_curr] = st.session_state[key_next]
            elif key_curr in st.session_state:
                del st.session_state[key_curr]
                
    last_idx = length - 1
    for template in templates:
        key_last = template.format(last_idx)
        if key_last in st.session_state:
            del st.session_state[key_last]


def render_shared_list(
    session_state_key: str,
    item_renderer: Callable[[int, Any], None],
    key_patterns: List[str] = None,
    col_widths: List[float] = [8.5, 1.5]
) -> None:
    """
    Renders a unified sequence of list items with standard controls:
    - Move Up (disabled for the first item)
    - Move Down (disabled for the last item)
    - Delete (standard delete button across editors)
    
    Ensures identical layout ratio and standard Streamlit styling.
    Strictly manages order changes and deletion, leaving content editing/rendering to the item_renderer.
    Automatically handles session state synchronization and triggers rerun.
    """
    import streamlit as st
    items = st.session_state.get(session_state_key, [])
    if not items:
        return

    if key_patterns is None:
        key_patterns = []

    for i in range(len(items)):
        # Render standard columns layout for identical layout ratios across both editors
        col_content, col_actions = st.columns(col_widths)
        
        with col_content:
            item_renderer(i, items[i])
            
        with col_actions:
            # Standard vertical spacing
            st.write("") # creates slight top alignment spacing
            
            up_disabled = (i == 0)
            down_disabled = (i == len(items) - 1)
            
            # Action buttons use unified, consistent plain-text labels and secondary button styles
            if st.button("Move Up", key=f"move_up_{session_state_key}_{i}", disabled=up_disabled, use_container_width=True):
                items[i], items[i-1] = items[i-1], items[i]
                _swap_session_keys(i, i - 1, key_patterns)
                st.rerun()
                
            if st.button("Move Down", key=f"move_down_{session_state_key}_{i}", disabled=down_disabled, use_container_width=True):
                items[i], items[i+1] = items[i+1], items[i]
                _swap_session_keys(i, i + 1, key_patterns)
                st.rerun()
                
            if st.button("Delete", key=f"delete_{session_state_key}_{i}", use_container_width=True):
                items.pop(i)
                _delete_session_keys(i, len(items) + 1, key_patterns)
                st.rerun()

