#!/usr/bin/env python3
"""Module docstring."""
import ast
import os
import sys
from promptops.utils import walk_workspace

def check_file_docstrings(filepath):
    """Missing docstring."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return False
        
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return False

    errors = []
    
    if not ast.get_docstring(tree):
        errors.append((1, "Module missing docstring"))
        
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not ast.get_docstring(node):
                errors.append((node.lineno, f"Class '{node.name}' missing docstring"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            if not ast.get_docstring(node):
                errors.append((node.lineno, f"Function/Method '{node.name}' missing docstring"))
                
    if errors:
        for lineno, msg in sorted(errors):
            print(f"{filepath}:{lineno} - {msg}")
        return False
    return True

def main():
    """Missing docstring."""
    directories = [
        "promptops/promptops",
        "tools/tools/scripts"
    ]
    
    passed = True
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in walk_workspace(directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    filepath = os.path.join(root, file)
                    if not check_file_docstrings(filepath):
                        passed = False
                        
    if not passed:
        sys.exit(1)
        
if __name__ == "__main__":
    main()
