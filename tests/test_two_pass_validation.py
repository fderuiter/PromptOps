import pytest
from promptops.utils import parse_skill_manifest

def test_undeclared_variable_fails_validation(tmp_path):
    """
    Verifies that if a skill manifest has an undeclared template variable (e.g., {{ undeclared_var }}),
    Pass 1 catches it and raises a ValueError, even if Jinja rendering would normally pre-render it
    to an empty string.
    """
    skills_md = tmp_path / "skills.md"
    content = """## Skill: Test Undeclared Variable
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Test skill with undeclared variable

### Core Instructions
```text
[SYSTEM]
This is a test core instructions.
The variable {{ undeclared_var }} is not declared in VALIDATION_METADATA.
```

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
[]
```
"""
    skills_md.write_text(content, encoding='utf-8')
    
    with pytest.raises(ValueError) as exc_info:
        parse_skill_manifest(skills_md)
    
    assert "Schema validation failed" in str(exc_info.value)
    assert "undeclared_var" in str(exc_info.value)


def test_declared_variables_pass_validation(tmp_path):
    """
    Verifies that a valid manifest with declared variables passes validation and renders cleanly.
    """
    skills_md = tmp_path / "skills.md"
    content = """## Skill: Test Declared Variables
<!-- VALIDATION_METADATA: {"variables": [{"name": "declared_var", "description": "A declared variable", "required": true}], "metadata": {}} -->
### Description
Test skill with declared variable

### Core Instructions
```text
[SYSTEM]
This is a test core instructions with {{ declared_var }}.
```

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
[]
```
"""
    skills_md.write_text(content, encoding='utf-8')
    
    res = parse_skill_manifest(skills_md)
    assert len(res["skills"]) == 1
    skill = res["skills"][0]
    assert skill["name"] == "Test Declared Variables"
    assert skill["variables"] == [{"name": "declared_var", "description": "A declared variable", "required": True}]


def test_jinja_syntax_error_fails(tmp_path):
    """
    Verifies that invalid Jinja syntax raises a ValueError.
    """
    skills_md = tmp_path / "skills.md"
    content = """## Skill: Test Invalid Jinja
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Test skill with invalid Jinja

### Core Instructions
```text
[SYSTEM]
This is bad jinja: {{ unclosed_variable
```

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
[]
```
"""
    skills_md.write_text(content, encoding='utf-8')
    
    with pytest.raises(ValueError) as exc_info:
        parse_skill_manifest(skills_md)
        
    assert "Schema validation failed" in str(exc_info.value) or "Failed to parse template" in str(exc_info.value)


def test_html_and_non_templated_brackets_ignored(tmp_path):
    """
    Verifies that standard HTML tags and non-templated bracket syntax are ignored
    and do not cause validation failures.
    """
    skills_md = tmp_path / "skills.md"
    content = """## Skill: Test Non Templated
<!-- VALIDATION_METADATA: {"variables": [], "metadata": {}} -->
### Description
Test skill with html and brackets

### Core Instructions
```text
[SYSTEM]
This has standard HTML tags: <br> and <p>Paragraph</p>.
Also bracket syntax like [system] and [link](http://example.com) that are not templated.
```

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
[]
```
"""
    skills_md.write_text(content, encoding='utf-8')
    
    res = parse_skill_manifest(skills_md)
    assert len(res["skills"]) == 1
    skill = res["skills"][0]
    assert skill["name"] == "Test Non Templated"
