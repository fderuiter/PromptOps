import math
import pandas as pd
import pytest
from studio.helpers import sanitize_dataframe_records
from promptops.utils import save_yaml, load_yaml
from pathlib import Path
import os

def test_sanitize_dataframe_records_basic():
    # Test dictionary input
    data = [
        {"name": "var1", "description": "  ", "required": None, "default": ""},
        {"name": "var2", "description": "desc2", "required": "True", "default": "nan"},
    ]
    sanitized = sanitize_dataframe_records(data, boolean_cols=["required"])
    
    assert sanitized[0]["name"] == "var1"
    assert sanitized[0]["description"] is None  # Whitespace-only string converted to None
    assert sanitized[0]["required"] is False   # None in boolean_cols converted to False
    assert sanitized[0]["default"] is None      # Empty string converted to None

    assert sanitized[1]["name"] == "var2"
    assert sanitized[1]["description"] == "desc2"
    assert sanitized[1]["required"] is True    # "True" converted to True
    assert sanitized[1]["default"] == "nan"    # Literal string "nan" is preserved!

def test_sanitize_dataframe_records_nan_and_na():
    df = pd.DataFrame({
        "name": ["a", "b", "c"],
        "required": [pd.NA, True, None],
        "default": [float("nan"), pd.NA, "real_value"]
    })
    sanitized = sanitize_dataframe_records(df, boolean_cols=["required"])
    
    assert sanitized[0]["name"] == "a"
    assert sanitized[0]["required"] is False
    assert sanitized[0]["default"] is None

    assert sanitized[1]["name"] == "b"
    assert sanitized[1]["required"] is True
    assert sanitized[1]["default"] is None

    assert sanitized[2]["name"] == "c"
    assert sanitized[2]["required"] is False
    assert sanitized[2]["default"] == "real_value"

def test_save_yaml_nan_removal_safeguard(tmp_path):
    # Test that save_yaml recursively cleans any float('nan') or pd.NA values
    test_file = tmp_path / "test_nan.yaml"
    
    data = {
        "name": "test_prompt",
        "description": "A description",
        "variables": [
            {"name": "var1", "required": False, "default": float("nan")},
            {"name": "var2", "required": True, "default": pd.NA}
        ]
    }
    
    save_yaml(test_file, data)
    
    # Reload and verify no nan
    reloaded = load_yaml(test_file, raw=True)
    assert reloaded["variables"][0]["default"] is None
    assert reloaded["variables"][1]["default"] is None

    # Check file content directly for ".nan" or "NaN"
    content = test_file.read_text(encoding="utf-8")
    assert ".nan" not in content
    assert "NaN" not in content
