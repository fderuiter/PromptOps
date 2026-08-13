"""
Shared UI helper functions for the Studio package.
Provides asset loading, rendering, validation, and session-state management.
"""

import os
import json
import yaml
from typing import Dict, Any, Type, List, Callable, Union
import streamlit as st
import pandas as pd
from pydantic import BaseModel, ValidationError

from promptops.utils import (
    ROOT,
    iter_prompt_files,
    iter_workflow_files,
    load_yaml,
    save_yaml,
)


def get_relative_asset_paths(
    asset_type: str, extensions: List[str] = None
) -> list[str]:
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


def render_file_selector(
    asset_type: str, key: str, label: str = None, extensions: List[str] = None
) -> str:
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
    layout_type: str = "tabs",
) -> Dict[str, Any]:
    """
    Dynamically generates Streamlit inputs from a Pydantic model's JSON schema.
    Can accept a layout configuration mapping to render fields inside tabs or collapsible sections.
    """
    if skip_fields is None:
        skip_fields = []

    schema = schema_class.model_json_schema()
    properties = schema.get("properties", {})

    def render_field(
        field_name: str, field_info: Dict[str, Any], data_dict: Dict[str, Any]
    ) -> Any:
        """
        Renders a single schema field using appropriate Streamlit input elements.
        """
        val = data_dict.get(field_name, "")

        # Determine the label to use
        if "title" in field_info:
            label = field_info["title"]
        elif "description" in field_info and field_info["description"]:
            label = field_info["description"]
        else:
            label = field_name

        def resolve_ref(schema_part: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(schema_part, dict):
                return {}
            ref = schema_part.get("$ref")
            if ref and ref.startswith("#/$defs/"):
                def_name = ref.split("/")[-1]
                return schema.get("$defs", {}).get(def_name, {})
            return schema_part

        field_info = resolve_ref(field_info)

        # Resolve field type and constraints
        field_type = field_info.get("type")
        minimum = field_info.get("minimum")
        maximum = field_info.get("maximum")

        subschemas = []
        if "anyOf" in field_info:
            subschemas.extend(field_info["anyOf"])
        if "oneOf" in field_info:
            subschemas.extend(field_info["oneOf"])
        if "allOf" in field_info:
            subschemas.extend(field_info["allOf"])

        for sub in subschemas:
            sub_resolved = resolve_ref(sub)
            if not field_type and sub_resolved.get("type"):
                field_type = sub_resolved.get("type")
            if minimum is None and "minimum" in sub_resolved:
                minimum = sub_resolved["minimum"]
            if maximum is None and "maximum" in sub_resolved:
                maximum = sub_resolved["maximum"]

        if not field_type:
            if "properties" in field_info:
                field_type = "object"
            elif "items" in field_info:
                field_type = "array"

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
                m_info = resolve_ref(m_info)
                m_val = data_dict["metadata"].get(m_key, m_info.get("default", ""))
                m_label = m_info.get("title", m_key)
                if m_info.get("type") == "boolean":
                    data_dict["metadata"][m_key] = st.checkbox(
                        m_label, value=bool(m_val), key=f"{key_prefix}meta_{m_key}"
                    )
                elif m_info.get("type") == "array":
                    m_val_str = ", ".join(m_val) if isinstance(m_val, list) else ""
                    res = st.text_input(
                        m_label, value=m_val_str, key=f"{key_prefix}meta_{m_key}"
                    )
                    data_dict["metadata"][m_key] = [
                        x.strip() for x in res.split(",") if x.strip()
                    ]
                else:
                    data_dict["metadata"][m_key] = st.text_input(
                        m_label, value=m_val, key=f"{key_prefix}meta_{m_key}"
                    )
        elif field_type == "string":
            if field_name == "description" or "description" in field_name.lower():
                data_dict[field_name] = st.text_area(
                    label, value=val, key=f"{key_prefix}{field_name}"
                )
            else:
                data_dict[field_name] = st.text_input(
                    label, value=val, key=f"{key_prefix}{field_name}"
                )
        elif field_type == "boolean":
            data_dict[field_name] = st.checkbox(
                label, value=bool(val), key=f"{key_prefix}{field_name}"
            )
        elif field_type in ("integer", "number"):
            if minimum is not None:
                minimum = int(minimum) if field_type == "integer" else float(minimum)
            if maximum is not None:
                maximum = int(maximum) if field_type == "integer" else float(maximum)
            
            raw_val = data_dict.get(field_name)
            if raw_val is None or raw_val == "":
                raw_val = field_info.get("default")
            
            if raw_val is None or raw_val == "":
                if minimum is not None:
                    default_val = minimum
                elif maximum is not None:
                    default_val = maximum
                else:
                    default_val = 0 if field_type == "integer" else 0.0
            else:
                try:
                    default_val = int(raw_val) if field_type == "integer" else float(raw_val)
                except ValueError:
                    if minimum is not None:
                        default_val = minimum
                    elif maximum is not None:
                        default_val = maximum
                    else:
                        default_val = 0 if field_type == "integer" else 0.0

            if minimum is not None and default_val < minimum:
                default_val = minimum
            if maximum is not None and default_val > maximum:
                default_val = maximum

            if minimum is not None and maximum is not None:
                res_val = st.slider(
                    label,
                    min_value=minimum,
                    max_value=maximum,
                    value=default_val,
                    step=1 if field_type == "integer" else 0.1,
                    key=f"{key_prefix}{field_name}",
                    help=field_info.get("description")
                )
            else:
                res_val = st.number_input(
                    label,
                    min_value=minimum,
                    max_value=maximum,
                    value=default_val,
                    step=1 if field_type == "integer" else 0.1,
                    key=f"{key_prefix}{field_name}",
                    help=field_info.get("description")
                )
            data_dict[field_name] = res_val
        elif field_type == "array":
            item_schema = field_info.get("items", {})
            item_schema = resolve_ref(item_schema)
            item_properties = item_schema.get("properties", {})
            
            is_array_flat_mappable = True
            if item_schema.get("type") == "object" or item_properties:
                for prop_name, prop_info in item_properties.items():
                    prop_info = resolve_ref(prop_info)
                    p_type = prop_info.get("type")
                    if not p_type and "properties" in prop_info:
                        p_type = "object"
                    elif not p_type and "items" in prop_info:
                        p_type = "array"
                    if p_type in ("object", "array"):
                        is_array_flat_mappable = False
                        break
            else:
                is_array_flat_mappable = True

            if is_array_flat_mappable:
                st.write(f"**{label}**")
                is_object_item = (item_schema.get("type") == "object" or bool(item_properties))
                raw_val = data_dict.get(field_name, [])
                if not isinstance(raw_val, list):
                    raw_val = []

                if is_object_item:
                    columns = list(item_properties.keys())
                    if raw_val:
                        df = pd.DataFrame(raw_val)
                        for col in columns:
                            if col not in df.columns:
                                df[col] = None
                        df = df[columns]
                    else:
                        df = pd.DataFrame(columns=columns)
                    
                    edited_df = st.data_editor(
                        df,
                        num_rows="dynamic",
                        key=f"{key_prefix}{field_name}_array_editor",
                        use_container_width=True
                    )
                    boolean_cols = [k for k, prop in item_properties.items() if resolve_ref(prop).get("type") == "boolean"]
                    sanitized_records = sanitize_dataframe_records(edited_df, boolean_cols=boolean_cols)
                    
                    def is_empty_row(row):
                        for k, v in row.items():
                            if v is not None and not pd.isna(v):
                                if isinstance(v, str) and v.strip() == "":
                                    continue
                                return False
                        return True
                    
                    res_val = [row for row in sanitized_records if not is_empty_row(row)]
                    data_dict[field_name] = res_val
                else:
                    if raw_val:
                        df = pd.DataFrame([{"Value": x} for x in raw_val])
                    else:
                        df = pd.DataFrame(columns=["Value"])
                    
                    edited_df = st.data_editor(
                        df,
                        num_rows="dynamic",
                        key=f"{key_prefix}{field_name}_array_editor",
                        use_container_width=True
                    )
                    records = edited_df.to_dict("records")
                    res_val = []
                    for row in records:
                        v = row.get("Value")
                        if v is not None and not pd.isna(v) and str(v).strip() != "":
                            item_type = item_schema.get("type", "string")
                            if item_type == "integer":
                                try:
                                    res_val.append(int(v))
                                except ValueError:
                                    pass
                            elif item_type == "number":
                                try:
                                    res_val.append(float(v))
                                except ValueError:
                                    pass
                            elif item_type == "boolean":
                                res_val.append(str(v).lower() in ("true", "1", "yes"))
                            else:
                                res_val.append(str(v))
                    data_dict[field_name] = res_val
            else:
                st.write(f"**{label} (YAML)**")
                raw_val = data_dict.get(field_name)
                try:
                    yaml_str = yaml.safe_dump(raw_val, default_flow_style=False, sort_keys=False) if raw_val is not None else ""
                except Exception:
                    yaml_str = ""
                    
                edited_yaml = st.text_area(
                    f"Enter YAML for {label}",
                    value=yaml_str,
                    key=f"{key_prefix}{field_name}_yaml_textarea",
                    height=200
                )
                if edited_yaml.strip():
                    try:
                        data_dict[field_name] = yaml.safe_load(edited_yaml)
                    except Exception as e:
                        st.error(f"Invalid YAML syntax in {label}: {e}")
                else:
                    data_dict[field_name] = None
        elif field_type == "object":
            properties = field_info.get("properties", {})
            is_obj_flat_mappable = True
            if properties:
                for prop_name, prop_info in properties.items():
                    prop_info = resolve_ref(prop_info)
                    p_type = prop_info.get("type")
                    if not p_type and "properties" in prop_info:
                        p_type = "object"
                    elif not p_type and "items" in prop_info:
                        p_type = "array"
                    if p_type in ("object", "array"):
                        is_obj_flat_mappable = False
                        break
            else:
                is_obj_flat_mappable = False

            if is_obj_flat_mappable:
                st.write(f"**{label}**")
                raw_val = data_dict.get(field_name, {}) or {}
                if not isinstance(raw_val, dict):
                    raw_val = {}
                flat_list = []
                for prop_name, prop_info in properties.items():
                    prop_info = resolve_ref(prop_info)
                    p_val = raw_val.get(prop_name)
                    if p_val is None:
                        p_val = prop_info.get("default", "")
                    flat_list.append({
                        "Parameter": prop_name,
                        "Value": str(p_val) if p_val is not None else ""
                    })
                df = pd.DataFrame(flat_list)
                edited_df = st.data_editor(
                    df,
                    num_rows="fixed",
                    key=f"{key_prefix}{field_name}_object_editor",
                    use_container_width=True
                )
                records = edited_df.to_dict("records")
                new_val = {}
                for row in records:
                    k = row.get("Parameter")
                    v = row.get("Value")
                    if k:
                        k = str(k).strip()
                        prop_info = resolve_ref(properties.get(k, {}))
                        p_type = prop_info.get("type")
                        if v is None or str(v).strip() == "":
                            new_val[k] = None
                        elif p_type == "integer":
                            try:
                                new_val[k] = int(v)
                            except ValueError:
                                new_val[k] = None
                        elif p_type == "number":
                            try:
                                new_val[k] = float(v)
                            except ValueError:
                                new_val[k] = None
                        elif p_type == "boolean":
                            new_val[k] = str(v).lower() in ("true", "1", "yes")
                        else:
                            new_val[k] = str(v)
                data_dict[field_name] = new_val
            else:
                st.write(f"**{label} (YAML)**")
                raw_val = data_dict.get(field_name)
                try:
                    yaml_str = yaml.safe_dump(raw_val, default_flow_style=False, sort_keys=False) if raw_val is not None else ""
                except Exception:
                    yaml_str = ""
                edited_yaml = st.text_area(
                    f"Enter YAML for {label}",
                    value=yaml_str,
                    key=f"{key_prefix}{field_name}_yaml_textarea",
                    height=200
                )
                if edited_yaml.strip():
                    try:
                        data_dict[field_name] = yaml.safe_load(edited_yaml)
                    except Exception as e:
                        st.error(f"Invalid YAML syntax in {label}: {e}")
                else:
                    data_dict[field_name] = None

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
        else:  # collapsible / expanders
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
    """
    Loads and returns YAML data. Standardizes error displays.
    """
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
    success_message: str = None,
) -> bool:
    """
    Validates data against the Pydantic schema_class.
    If valid, saves/serializes YAML to disk, or runs the custom save_callback (if any).
    Displays success/error notifications to the user in a consistent Streamlit banner style.
    """
    # 1. Path safety and traversal checks before any disk/folder operations
    base_dir = str(ROOT)
    if has_path_traversal(file_path):
        st.error(
            "Path validation failed: directory traversal segments ('..') are not allowed."
        )
        return False

    if not is_safe_path(base_dir, file_path):
        st.error(
            "Path validation failed: target path is outside the allowed workspace boundaries."
        )
        return False

    # 2. Safe directory creation AFTER successful path validation
    try:
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        st.error(f"Failed to create parent directory: {e}")
        return False

    try:
        # Validate using Pydantic model instantiation
        schema_class(**data)

        # Save operation
        if save_callback:
            save_callback(file_path, data)
        else:
            save_yaml(file_path, data)

        msg = (
            success_message
            or f"Successfully saved and validated {os.path.basename(file_path)}!"
        )
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


def _get_all_matching_templates(
    indices: List[int], key_patterns: List[str]
) -> List[str]:
    """
    Finds all key templates currently present in session state for any of the given indices.
    """
    templates = set()
    for idx in indices:
        for key in list(st.session_state.keys()):
            for pattern in key_patterns:
                if "{}" in pattern:
                    prefix_part, suffix_part = pattern.split("{}", 1)
                    if key.startswith(prefix_part):
                        expected_prefix = prefix_part + str(idx)
                        if key.startswith(expected_prefix):
                            dynamic_suffix = key[len(expected_prefix) :]
                            # Make sure the dynamic suffix matches suffix_part if there is one
                            if suffix_part == "" or dynamic_suffix.startswith(
                                suffix_part
                            ):
                                templates.add(prefix_part + "{}" + dynamic_suffix)
                else:
                    # Pattern is a simple prefix
                    if key.startswith(f"{pattern}{idx}_") or key == f"{pattern}{idx}":
                        suffix = key[len(f"{pattern}{idx}") :]
                        templates.add(f"{pattern}{{}}{suffix}")
    return list(templates)


def _swap_session_keys(i: int, j: int, key_patterns: List[str]):
    """
    Swaps keys in st.session_state matching format patterns for indices i and j.
    """
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
    """
    Shifts keys matching format patterns down when item at index i is deleted.
    """
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
    col_widths: List[float] = [8.5, 1.5],
    show_reorder: bool = True,
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
            st.write("")  # creates slight top alignment spacing

            if show_reorder:
                up_disabled = i == 0
                down_disabled = i == len(items) - 1

                # Action buttons use unified, consistent plain-text labels and secondary button styles
                if st.button(
                    "⬆️ Move Up",
                    key=f"move_up_{session_state_key}_{i}",
                    disabled=up_disabled,
                    use_container_width=True,
                ):
                    items[i], items[i - 1] = items[i - 1], items[i]
                    _swap_session_keys(i, i - 1, key_patterns)
                    st.rerun()

                if st.button(
                    "⬇️ Move Down",
                    key=f"move_down_{session_state_key}_{i}",
                    disabled=down_disabled,
                    use_container_width=True,
                ):
                    items[i], items[i + 1] = items[i + 1], items[i]
                    _swap_session_keys(i, i + 1, key_patterns)
                    st.rerun()

            if st.button(
                "🗑️ Delete",
                key=f"delete_{session_state_key}_{i}",
                use_container_width=True,
            ):
                items.pop(i)
                _delete_session_keys(i, len(items) + 1, key_patterns)
                st.rerun()


def sanitize_dataframe_records(
    data: Union[pd.DataFrame, List[Dict[str, Any]]], boolean_cols: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Sanitizes UI dataframes or list of dicts before validation and saving.
    - Converts NaN/pd.NA and empty or whitespace-only strings to None.
    - Converts empty or unset checkbox fields (in boolean_cols) to False instead of NaN.
    """
    if isinstance(data, pd.DataFrame):
        records = data.to_dict("records")
    elif isinstance(data, list):
        # Shallow copy to avoid mutation
        records = [dict(r) for r in data]
    else:
        return data

    if boolean_cols is None:
        boolean_cols = ["required"]

    sanitized = []
    for row in records:
        clean_row = {}
        for k, v in row.items():
            is_null = pd.isna(v) if not isinstance(v, (list, dict, str)) else False

            if k in boolean_cols:
                if (
                    is_null
                    or v is None
                    or v == ""
                    or (isinstance(v, str) and v.strip() == "")
                ):
                    clean_row[k] = False
                else:
                    clean_row[k] = bool(v)
            else:
                if is_null or v is None:
                    clean_row[k] = None
                elif isinstance(v, str) and v.strip() == "":
                    clean_row[k] = None
                else:
                    clean_row[k] = v
        sanitized.append(clean_row)
    return sanitized


def has_path_traversal(path_str: str) -> bool:
    r"""
    Checks if a path contains directory traversal sequences like '..', '../', '..\\'.
    """
    normalized = path_str.replace("\\", "/")
    segments = normalized.split("/")
    if ".." in segments:
        return True
    if ".." in path_str:
        return True
    return False


def is_safe_path(base_dir: str, path: str, follow_symlinks: bool = True) -> bool:
    """
    Validates that the path resolves to a location strictly inside base_dir.
    """
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    real_base = os.path.realpath(base_dir)
    return matchpath.startswith(real_base)


def get_existing_subfolders(asset_root_dir: str) -> List[str]:
    """
    Finds all existing directories under asset_root_dir, returning them as relative paths.
    Always includes '.' as the first option.
    """
    subfolders = []
    if os.path.exists(asset_root_dir):
        for root, dirs, _ in os.walk(asset_root_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
            for d in dirs:
                full_path = os.path.join(root, d)
                rel_path = os.path.relpath(full_path, asset_root_dir)
                if rel_path and rel_path != ".":
                    subfolders.append(rel_path)
    return ["."] + sorted(list(set(subfolders)))
