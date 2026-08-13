import os
import tempfile
import pytest
from streamlit.testing.v1 import AppTest
import pandas as pd
import yaml

APP_TEMPLATE = """
import streamlit as st
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from studio.helpers import render_schema_form

class ComplexItem(BaseModel):
    nested_list: List[str]
    name: str

class TestItem(BaseModel):
    val: str

class TestSchema(BaseModel):
    # Numeric fields (Requirement 1)
    bounded_int: int = Field(5, ge=0, le=10, description="An integer slider")
    unbounded_num: float = Field(2.5, description="An unbounded number input")
    
    # Array fields (Requirement 2)
    flat_array: List[str] = Field(default_factory=list)
    object_array: List[TestItem] = Field(default_factory=list)
    deep_nested_array: List[ComplexItem] = Field(default_factory=list)
    
    # Object fields (Requirement 3)
    flat_object: TestItem = Field(default_factory=lambda: TestItem(val="hello"))
    complex_object: ComplexItem = Field(default_factory=lambda: ComplexItem(nested_list=["a"], name="c"))

if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "bounded_int": 5,
        "unbounded_num": 2.5,
        "flat_array": ["a", "b"],
        "object_array": [{"val": "first"}],
        "deep_nested_array": [{"nested_list": ["foo"], "name": "bar"}],
        "flat_object": {"val": "hello"},
        "complex_object": {"nested_list": ["a"], "name": "c"}
    }

updated_data = render_schema_form(TestSchema, st.session_state.form_data)
st.session_state.form_data = updated_data
st.write("OUTPUT:", st.session_state.form_data)
"""

def test_dynamic_schema_form_rendering():
    # Write a temporary streamlit script
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(APP_TEMPLATE)
        temp_filename = f.name

    try:
        at = AppTest.from_file(temp_filename)
        at.run(timeout=15)
        assert not at.exception

        # 1. Assert slider and number_input rendering
        # bounded_int has ge/le bounds -> should render as st.slider
        assert len(at.slider) > 0
        slider_widget = at.slider[0]
        assert slider_widget.min == 0
        assert slider_widget.max == 10
        assert slider_widget.value == 5

        # unbounded_num has no bounds -> should render as st.number_input
        assert len(at.number_input) > 0
        num_input_widget = at.number_input[0]
        assert num_input_widget.value == 2.5

        # 2. Check the data_editor elements (Requirement 2 & 3)
        # We expect st.data_editor to render for flat_array, object_array, flat_object
        assert len(at.dataframe) >= 3

        # 3. Check text areas (for deep_nested_array fallback, and complex_object fallback)
        # Should render YAML serialization as text_area
        assert len(at.text_area) >= 2
        
        # Verify text areas contain yaml strings
        yaml_textarea_vals = [t.value for t in at.text_area]
        assert any("nested_list" in y and "name" in y for y in yaml_textarea_vals)

    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)
