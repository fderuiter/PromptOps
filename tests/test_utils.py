from pathlib import Path
from promptops.utils import (
    KeepUndefined,
    _find_root,
    walk_workspace,
    iter_prompt_files,
    iter_workflow_files,
    iter_markdown_files,
    iter_skill_manifests,
    deep_merge,
    load_yaml,
    save_yaml,
    _format_category,
    _domain_root,
    get_prompt_tags,
    derive_category,
    derive_title,
    get_tool_name,
    get_tool_name_mcp,
    extract_vars_from_text,
    extract_template_vars,
    parse_skill_manifest,
    resolve_skill_from_path,
    resolve_fallback_prompt
)

def test_keep_undefined():
    undef = KeepUndefined(name="test")
    assert str(undef) == "{{ test }}"
    
    attr = undef.my_attr
    assert str(attr) == "{{ test.my_attr }}"
    
    item = undef['my_key']
    assert str(item) == "{{ test['my_key'] }}"

def test_deep_merge():
    base = {"a": 1, "b": {"x": 10, "y": 20}}
    override = {"b": {"y": 30, "z": 40}, "c": 3}
    merged = deep_merge(base, override)
    assert merged == {"a": 1, "b": {"x": 10, "y": 30, "z": 40}, "c": 3}
    
    # Non-dict cases
    assert deep_merge(base, "string") == "string"
    assert deep_merge("string", override) == override

def test_path_discovery(tmp_path):
    root = _find_root()
    assert isinstance(root, Path)

def test_walk_workspace(tmp_path):
    # Setup a small fake workspace
    d1 = tmp_path / "valid_dir"
    d1.mkdir()
    f1 = d1 / "file.txt"
    f1.touch()
    
    d2 = tmp_path / ".git"
    d2.mkdir()
    
    results = list(walk_workspace(tmp_path))
    dirs_found = [p[0] for p in results]
    assert any("valid_dir" in p for p in dirs_found)
    assert not any(".git" in p for p in dirs_found)

def test_yaml_operations(tmp_path):
    p = tmp_path / "test.yaml"
    data = {"key": "value", "list": [1, 2, 3]}
    save_yaml(p, data)
    assert p.exists()
    
    loaded = load_yaml(p, raw=True)
    assert loaded == data

def test_classification():
    assert _format_category("My-Category_Name") == "My Category Name"
    assert _domain_root("domain:sales") == "domain:sales"
    assert _domain_root("sales") == "sales"
    
    content = {"tags": ["tag1", "domain:test"], "tag": "single_tag"}
    assert set(get_prompt_tags(content)) == {"tag1", "domain:test"}

def test_derive_category_and_title(tmp_path):
    root = tmp_path / "prompts"
    sub = root / "sales" / "emails"
    sub.mkdir(parents=True)
    p = sub / "cold_email.yaml"
    
    cat = derive_category(p, root)
    assert cat == "Sales"
    
    # with prompt
    cat2 = derive_category(p, root, {"metadata": {"domain": "Override"}})
    assert cat2 == "Override"
    
    title = derive_title(p, {"name": "Explicit Name"})
    assert title == "Explicit Name"
    
    title2 = derive_title(p, {})
    assert title2 == "Cold Email"

def test_tool_names():
    p = Path("/app/prompts/sales/emails/cold_email.yaml")
    name, ns = get_tool_name(p, {})
    assert name == "cold_email.yaml"
    assert ns == "sales__cold_email_yaml"
    
    mcp = get_tool_name_mcp(p, {})
    assert mcp == "sales__cold_email_yaml"

def test_namespaced_tool_registry_and_truncation():
    # 1. Base case
    p = Path("/app/prompts/clinical/trial_execution/breast_cancer_trial.prompt.yaml")
    name, ns = get_tool_name(p, {})
    assert name == "breast_cancer_trial"
    assert ns == "clinical__breast_cancer_trial"
    
    # 2. Exceeding 64 characters
    p_long = Path("/app/prompts/clinical/trial_execution/a_very_long_name_that_will_definitely_exceed_sixty_four_characters_when_prefixed.prompt.yaml")
    _, ns_long = get_tool_name(p_long, {})
    assert len(ns_long) == 64
    assert ns_long.startswith("clinical__")
    
    # 3. Duplicate base names in different domains
    p_clinical = Path("/app/prompts/clinical/data_validation.prompt.yaml")
    p_business = Path("/app/prompts/business/data_validation.prompt.yaml")
    _, ns_clinical = get_tool_name(p_clinical, {})
    _, ns_business = get_tool_name(p_business, {})
    assert ns_clinical == "clinical__data_validation"
    assert ns_business == "business__data_validation"
    
    # 4. Explicit domain metadata override
    p_override = Path("/app/prompts/unknown/tool.prompt.yaml")
    _, ns_override = get_tool_name(p_override, {"metadata": {"domain": "Override Scientific"}})
    assert ns_override == "override_scientific__tool"

def test_extract_vars():
    text = "Hello {{ name }}, welcome to {{ place.name }}."
    vars = extract_vars_from_text(text)
    assert vars == {"name", "place"}
    
    content = {
        "messages": [
            {"content": "{{ var1 }}"}
        ]
    }
    extracted = extract_template_vars(content)
    assert set(extracted) == {"var1"}

def test_iterators():
    # Just checking they can run without crashing and return generators
    assert iter_prompt_files()
    assert iter_workflow_files()
    assert iter_markdown_files()
    assert iter_skill_manifests()

def test_parse_skill_manifest(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text('{"name": "my_skill"}', encoding='utf-8')
    res = parse_skill_manifest(p)
    assert "metadata" in res
    assert "skills" in res
    assert res["skills"] == []
    
def test_resolve_skill_from_path():
    path = Path("/some/path/my_skill.yaml")
    skills = [
        {"name": "other_skill", "tags": []},
        {"name": "my_skill", "tags": ["tag1"]}
    ]
    resolved = resolve_skill_from_path(path, skills)
    assert resolved == {"name": "my_skill", "tags": ["tag1"]}
    
    # Fallback to fuzzy match
    path2 = Path("/some/path/my_skill_advanced.yaml")
    resolved2 = resolve_skill_from_path(path2, skills)
    # the words are "my", "skill", "advanced" -> matches "my_skill" which has "my", "skill"
    assert resolved2 == {"name": "my_skill", "tags": ["tag1"]}

def test_resolve_fallback_prompt(tmp_path, monkeypatch):
    from promptops import utils
    # Setup simple mock yaml
    p = tmp_path / "test.yaml"
    skills_md = tmp_path / "skills.md"
    skills_md.write_text("## Skill: test\n", encoding='utf-8')
    
    def mock_parse(path):
        return {
            "skills": [{
                "name": "test",
                "instructions": "instruction",
                "tags": []
            }]
        }
    monkeypatch.setattr(utils, "parse_skill_manifest", mock_parse)
    
    res = resolve_fallback_prompt(p)
    assert res is not None
    assert res["name"] == "test"
    assert res["messages"] == [{"role": "system", "content": "instruction"}]
