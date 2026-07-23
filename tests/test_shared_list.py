import streamlit as st
from studio.helpers import (
    _get_all_matching_templates,
    _swap_session_keys,
    _delete_session_keys
)

def test_get_all_matching_templates():
    st.session_state.clear()
    st.session_state["role_0"] = "system"
    st.session_state["role_1"] = "user"
    st.session_state["map_1_var"] = "inputs.test"
    st.session_state["map_0_var"] = "inputs.foo"
    st.session_state["unrelated"] = "bar"
    
    key_patterns = ["role_{}", "map_{}_"]
    
    # Let's get matching templates
    templates = _get_all_matching_templates([0, 1], key_patterns)
    assert len(templates) == 2
    assert "role_{}" in templates
    assert "map_{}_var" in templates

def test_swap_session_keys():
    st.session_state.clear()
    st.session_state["role_0"] = "system"
    st.session_state["role_1"] = "user"
    st.session_state["content_0"] = "Hello System"
    st.session_state["content_1"] = "Hello User"
    st.session_state["map_0_var"] = "inputs.foo"
    st.session_state["map_1_var"] = "inputs.bar"
    
    key_patterns = ["role_{}", "content_{}", "map_{}_"]
    
    _swap_session_keys(0, 1, key_patterns)
    
    assert st.session_state["role_0"] == "user"
    assert st.session_state["role_1"] == "system"
    assert st.session_state["content_0"] == "Hello User"
    assert st.session_state["content_1"] == "Hello System"
    assert st.session_state["map_0_var"] == "inputs.bar"
    assert st.session_state["map_1_var"] == "inputs.foo"

def test_delete_session_keys():
    st.session_state.clear()
    st.session_state["role_0"] = "system"
    st.session_state["role_1"] = "user"
    st.session_state["role_2"] = "assistant"
    st.session_state["map_0_var"] = "inputs.foo"
    st.session_state["map_1_var"] = "inputs.bar"
    st.session_state["map_2_var"] = "inputs.baz"
    
    key_patterns = ["role_{}", "map_{}_"]
    
    # Delete index 1 (original length 3)
    _delete_session_keys(1, 3, key_patterns)
    
    # After deleting index 1, index 0 is unaffected, index 1 gets value from old index 2, and old index 2 is deleted
    assert st.session_state["role_0"] == "system"
    assert st.session_state["role_1"] == "assistant"
    assert "role_2" not in st.session_state
    
    assert st.session_state["map_0_var"] == "inputs.foo"
    assert st.session_state["map_1_var"] == "inputs.baz"
    assert "map_2_var" not in st.session_state
