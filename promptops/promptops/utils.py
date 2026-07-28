"""Module docstring."""
import re
import os
import hashlib
from pathlib import Path
import yaml
import pathspec
from typing import Iterator, Dict, Any, List, Optional, Set, Union, Tuple

from jinja2 import Undefined, meta, Environment

class KeepUndefined(Undefined):
    """Missing docstring."""
    def __getattr__(self, name):
        return KeepUndefined(name=f"{self._undefined_name}.{name}")
        
    def __getitem__(self, key):
        return KeepUndefined(name=f"{self._undefined_name}['{key}']")
        
    def __str__(self):
        return f"{{{{ {self._undefined_name} }}}}"

# Centralized Path Registry
def _find_root() -> Path:
    """Missing docstring."""
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / "prompts").exists() and (current / "workflows").exists():
            return current
        current = current.parent
    # Fallback to file-relative if running in an editable install but not from repo
    fallback = Path(__file__).resolve().parents[2]
    if (fallback / "prompts").exists():
        return fallback
    return Path.cwd().resolve()

ROOT: Path = _find_root()
PROMPTS_DIR: Path = ROOT / "prompts"
WORKFLOWS_DIR: Path = ROOT / "workflows"
OVERVIEW_NAME: str = "overview.md"
DOMAIN_TAG_PREFIX: str = "domain:"

_IGNORE_SPEC: Optional[pathspec.PathSpec] = None

def _get_ignore_spec() -> pathspec.PathSpec:
    """Missing docstring."""
    global _IGNORE_SPEC
    if _IGNORE_SPEC is not None:
        return _IGNORE_SPEC

    ignore_file = ROOT / ".promptignore"
    lines = []
    if ignore_file.exists():
        try:
            lines = ignore_file.read_text(encoding='utf-8').splitlines()
        except Exception:
            pass
    _IGNORE_SPEC = pathspec.PathSpec.from_lines('gitignore', lines)
    return _IGNORE_SPEC

def walk_workspace(root_path: Union[str, Path]) -> Iterator[Tuple[str, List[str], List[str]]]:
    """
    A generator that behaves like os.walk but prunes ignored directories 
    and files according to .promptignore and common exclusion rules.
    """
    spec = _get_ignore_spec()
    root_path_obj = Path(root_path)
    
    for root, dirs, files in os.walk(root_path_obj):
        current_dir = Path(root)
        
        # Prune dirs
        valid_dirs = []
        for d in dirs:
            if d.startswith("._") or d in (".git", ".github", "site", "docs_build", ".venv", "venv", "__pycache__", ".tox", ".pytest_cache", "build", "dist"):
                continue
            dir_path = current_dir / d
            try:
                rel_dir = dir_path.relative_to(ROOT).as_posix() + "/"
            except ValueError:
                rel_dir = dir_path.relative_to(root_path_obj).as_posix() + "/"
                
            if not spec.match_file(rel_dir) and not spec.match_file(rel_dir.rstrip('/')):
                valid_dirs.append(d)
                
        dirs[:] = valid_dirs
        
        valid_files = []
        for f in files:
            if f.startswith("._") or f == ".DS_Store":
                continue
                
            file_path = current_dir / f
            try:
                rel_file = file_path.relative_to(ROOT).as_posix()
            except ValueError:
                rel_file = file_path.relative_to(root_path_obj).as_posix()
                
            if not spec.match_file(rel_file):
                valid_files.append(f)
                
        yield root, dirs, valid_files

def _iter_files_with_ignore(root_path: Path, extensions: Tuple[str, ...]) -> Iterator[Path]:
    """Missing docstring."""
    for root, _, files in walk_workspace(root_path):
        current_dir = Path(root)
        for f in files:
            if not any(f.endswith(ext.lstrip("*")) for ext in extensions):
                continue
            yield current_dir / f

# Centralized Governance Paths
MANIFEST_DIR: Path = ROOT / "promptops" / "governance"
MANIFEST_FILE: Path = MANIFEST_DIR / "compliance_manifest.json"
GAP_REPORT_FILE: Path = MANIFEST_DIR / "gap_report.json"
KB_FILE: Path = ROOT / "promptops" / "regulatory_kb.yaml"


def deep_merge(base: Any, override: Any) -> Any:
    """Deep merge two dictionaries. override takes precedence."""
    if not isinstance(base, dict) or not isinstance(override, dict):
        return override
    merged = base.copy()
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged

def load_yaml(path: Union[str, Path], raw: bool = False) -> Dict[str, Any]:
    """Missing docstring."""
    path_obj = Path(path)
    try:
        text = path_obj.read_text(encoding="utf-8")
        
        inherited_config: Dict[str, Any] = {}
        macros_text = ""
        
        try:
            # Build hierarchy
            base_dir = None
            resolved_path = path_obj.resolve()
            if str(PROMPTS_DIR.resolve()) in str(resolved_path):
                base_dir = PROMPTS_DIR.resolve()
            elif str(WORKFLOWS_DIR.resolve()) in str(resolved_path):
                base_dir = WORKFLOWS_DIR.resolve()
                
            if base_dir:
                current = path_obj.parent.resolve()
                hierarchy = []
                while current != base_dir and base_dir in current.parents:
                    hierarchy.append(current)
                    current = current.parent
                hierarchy.append(base_dir)
                hierarchy.reverse()
                
                for d in hierarchy:
                    # Collect macros
                    for j2_file in sorted(d.glob("*.j2")):
                        if j2_file.is_file():
                            macros_text += j2_file.read_text(encoding="utf-8") + "\n"
                    for jinja_file in sorted(d.glob("*.jinja")):
                        if jinja_file.is_file():
                            macros_text += jinja_file.read_text(encoding="utf-8") + "\n"
                            
                    # Merge configuration
                    for cfg_name in ("config.yaml", "_config.yaml"):
                        cfg_path = d / cfg_name
                        if cfg_path.is_file():
                            try:
                                cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
                                inherited_config = deep_merge(inherited_config, cfg)
                            except Exception:
                                pass
        except Exception:
            pass

        if not raw:
            # To match identical validation and execution inheritance, we use PROMPTS_DIR as base
            # for prompts, or the file's parent for generic files.
            # But tools/scripts/utils.py used PROMPTS_DIR directly for all inheritance:
            # env = _get_jinja_env()  (which hardcodes PROMPTS_DIR)
            from promptops.engine import get_jinja_env
            env = get_jinja_env(base_dir=str(PROMPTS_DIR))
            full_text = macros_text + text if macros_text else text
            template = env.from_string(full_text)
            rendered_text = template.render()
        else:
            rendered_text = text
            
        if rendered_text is None:
            rendered_text = ""
            
        if isinstance(rendered_text, str):
            rendered_text = rendered_text.lstrip()
            if rendered_text.startswith("---"):
                parts = rendered_text.split("---", 2)
                if len(parts) >= 3:
                    data = yaml.safe_load(parts[1]) or {}
                    
                    if inherited_config:
                        data = deep_merge(inherited_config, data)
                        
                    content = parts[2]
                    
                    messages = data.get("messages", [])
                    blocks = re.split(r'^##\s+(.*)$', content, flags=re.MULTILINE | re.IGNORECASE)
                    for i in range(1, len(blocks), 2):
                        header = blocks[i].strip()
                        body = blocks[i+1].strip()
                        if not body:
                            continue
                            
                        role = header.lower()
                        if role == 'purpose':
                            role = 'system'
                        elif role == 'instructions':
                            role = 'user'
                            
                        messages.append({"role": role, "content": body})
                    data["messages"] = messages
                    return data
                    
            data = yaml.safe_load(rendered_text) or {}
            if isinstance(data, dict) and inherited_config:
                data = deep_merge(inherited_config, data)
            return data
        elif isinstance(rendered_text, dict):
            if inherited_config:
                return deep_merge(inherited_config, rendered_text)
            return rendered_text
        return {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def save_yaml(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Missing docstring."""
    import math
    import pandas as pd
    
    def _clean_nan(v: Any) -> Any:
        if isinstance(v, dict):
            return {k: _clean_nan(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [_clean_nan(val) for val in v]
        else:
            if v is None:
                return None
            if isinstance(v, float) and math.isnan(v):
                return None
            if v is pd.NA:
                return None
            return v

    data = _clean_nan(data)
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    if path_obj.name.endswith(".prompt.md") or path_obj.suffix == ".md":
        messages = data.get("messages", [])
        frontmatter_data = {k: v for k, v in data.items() if k != "messages"}
        
        frontmatter_str = yaml.dump(frontmatter_data, sort_keys=False, allow_unicode=True, default_flow_style=False)
        
        md_content = f"---\n{frontmatter_str}---\n\n"
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            header = "Purpose" if role == "system" else ("Instructions" if role == "user" else role.capitalize())
            md_content += f"## {header}\n{content}\n\n"
            
        with path_obj.open('w', encoding='utf-8') as f:
            f.write(md_content)
    else:
        with path_obj.open('w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

def _is_valid_file(p: Path) -> bool:
    """Missing docstring."""
    if p.name.startswith("._") or p.name == ".DS_Store":
        return False
    parts = p.parts
    if "site" in parts or "docs_build" in parts:
        return False
    return True

def iter_prompt_files(root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
    """Missing docstring."""
    root_path = Path(root) if root else PROMPTS_DIR
    yield from _iter_files_with_ignore(root_path, ("*.prompt.yaml", "*.prompt.yml", "*.prompt.md"))

def iter_workflow_files(root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
    """Missing docstring."""
    root_path = Path(root) if root else WORKFLOWS_DIR
    yield from _iter_files_with_ignore(root_path, ("*.workflow.yaml", "*.workflow.yml"))

def iter_markdown_files(root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
    """Iterate over all Markdown files recursively, skipping hidden/system files."""
    root_path = Path(root) if root else Path.cwd()
    yield from _iter_files_with_ignore(root_path, ("*.md",))


def _format_category(raw: str) -> str:
    """Missing docstring."""
    cleaned = raw.strip().replace("_", " ").replace("-", " ").replace("/", " ")
    return " ".join(word.capitalize() for word in cleaned.split())

def _domain_root(value: str) -> str:
    """Missing docstring."""
    return value.strip().split("/", 1)[0].strip()

def get_prompt_tags(content: Dict[str, Any]) -> List[str]:
    """Missing docstring."""
    from promptops.tags import extract_tags
    return extract_tags(content)

def derive_category(path: Path, root_dir: Path, content: Optional[Dict[str, Any]] = None) -> str:
    """Missing docstring."""
    data = content or {}
    for tag in get_prompt_tags(data):
        if tag.lower().startswith(DOMAIN_TAG_PREFIX):
            value = tag.split(":", 1)[1].strip()
            if value:
                return _format_category(_domain_root(value))

    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        domain = metadata.get("domain")
        if isinstance(domain, str) and domain.strip():
            return _format_category(_domain_root(domain))

    try:
        relative = path.relative_to(root_dir)
        if len(relative.parts) < 2:
            return "Uncategorized"
        return _format_category(relative.parts[0])
    except ValueError:
        return "Uncategorized"

def derive_title(path: Path, data: Dict[str, Any]) -> str:
    """Missing docstring."""
    if name := data.get('name') or data.get('title'):
        return str(name).strip()
    stem = path.stem.replace('.workflow', '').replace('.prompt', '')
    clean_name = re.sub(r'^\d+_', '', stem)
    return clean_name.replace('_', ' ').title()

def get_tool_name(path: Path, content: dict) -> Tuple[str, str]:
    """
    Returns (original_name, sanitized_name).
    Handles unified normalization and hashing for truncation.
    """
    name = content.get('name')
    if not name:
        name = path.name.replace(".workflow.yaml", "").replace(".prompt.yaml", "").replace(".prompt.yml", "").replace(".prompt.md", "")
        
    original_name = name

    # Find a root directory in the path's ancestry named "prompts" or "workflows"
    root_dir = PROMPTS_DIR
    for parent in path.parents:
        if parent.name in ("prompts", "workflows"):
            root_dir = parent
            break

    category = derive_category(path, root_dir, content)
    domain = category.lower().strip()
    domain = re.sub(r'[^a-z0-9_-]', '_', domain)
    domain = re.sub(r'_+', '_', domain)
    domain = domain.strip('_')

    # Replace double underscore with a sentinel to avoid being collapsed by collapsing regex
    sentinel = "DOUBLEUNDERSCORE"
    namespaced_name = f"{domain}{sentinel}{name}"
    
    namespaced_name = re.sub(r'[^a-zA-Z0-9_-]', '_', namespaced_name)
    namespaced_name = re.sub(r'_+', '_', namespaced_name)
    namespaced_name = namespaced_name.strip('_')
    
    # Restore double underscore
    namespaced_name = namespaced_name.replace(sentinel, "__")
    
    if len(namespaced_name) > 64:
        hash_input = f"{path}::{domain}__{original_name}"
        hash_suffix = hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:8]
        namespaced_name = f"{namespaced_name[:55]}_{hash_suffix}"
        
    return original_name, namespaced_name

def get_tool_name_mcp(path: Path, content: dict) -> str:
    """Wrapper that just returns the sanitized name for MCP server."""
    _, sanitized = get_tool_name(path, content)
    return sanitized

_JINJA_ENV = Environment()
_IGNORE_XML_TAGS = {"br", "p", "b", "i", "div", "span", "ul", "li", "ol", "html", "body", "head", "title", "table", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "a", "img", "strong", "em", "hr", "meta", "link", "script", "style", "svg", "path", "text", "aegis"}

def extract_vars_from_text(text: str) -> Set[str]:
    """Extracts Jinja and XML variables from a single text string."""
    found: Set[str] = set()
    
    try:
        ast = _JINJA_ENV.parse(text)
        vars_in_text = meta.find_undeclared_variables(ast)
        found.update(vars_in_text)
    except Exception as e:
        raise ValueError(f"Failed to parse template for variables: {e}")
    
    # Extract variables wrapped in XML tags
    xml_tags = re.findall(r'<([a-zA-Z0-9_]+)>', text)
    for tag in xml_tags:
        if tag.lower() not in _IGNORE_XML_TAGS:
            found.add(tag)
            
    return found

def extract_template_vars(content: Dict[str, Any]) -> List[str]:
    """Missing docstring."""
    found: Set[str] = set()
    for msg in content.get("messages", []):
        text = msg.get("content", "")
        if isinstance(text, str):
            found.update(extract_vars_from_text(text))
    return sorted(list(found))

def iter_skill_manifests(root: Optional[Union[str, Path]] = None) -> Iterator[Path]:
    """Missing docstring."""
    root_path = Path(root) if root else PROMPTS_DIR
    for p in root_path.rglob("skills.md"):
        if _is_valid_file(p):
            yield p

def parse_skill_manifest(path: Path) -> Dict[str, Any]:
    """Missing docstring."""
    import json
    text = path.read_text(encoding='utf-8')
    metadata: Dict[str, Any] = {}
    content = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1]) or {}
                content = parts[2]
            except:
                pass
    skills = []
    import re
    # Match skills and metadata
    skill_blocks = re.split(r'## Skill: ', content)[1:]
    for block in skill_blocks:
        lines = block.splitlines()
        name = lines[0].strip()
        body = "\n".join(lines[1:])

        # Extract metadata
        meta_match = re.search(r'<!-- VALIDATION_METADATA: (.*?) -->', body)
        vars_data = []
        skill_metadata = {}
        if meta_match:
            try:
                parsed_meta = json.loads(meta_match.group(1))
                if isinstance(parsed_meta, list):
                    vars_data = parsed_meta
                elif isinstance(parsed_meta, dict):
                    vars_data = parsed_meta.get("variables", [])
                    skill_metadata = parsed_meta.get("metadata", {})
            except:
                pass

        # Extract core instructions
        # Use non-greedy match for the content to ensure we get the full code block until the final ``` that precedes the next ### heading.
        instr_match = re.search(r'### Core Instructions\s*```[a-zA-Z0-9_-]*\n(.*?)\n```\n+(?:###|$)', body, re.DOTALL)
        instructions = instr_match.group(1).strip() if instr_match else ""

        # Render instructions using jinja to evaluate any macros (like load_yaml does)
        try:
            from promptops.engine import get_jinja_env
            env = get_jinja_env(base_dir=str(PROMPTS_DIR))
            if 'macros.' in instructions and not '{% import' in instructions:
                instructions = '{% import "common/macros.j2" as macros %}\n' + instructions
            template = env.from_string(instructions)
            instructions = template.render()
        except Exception:
            pass

        # Split instructions into messages
        messages = []
        import re
        blocks = re.split(r'^\[(system|user|assistant|tool_call|tool_result|tool)\][\r\n]+', instructions, flags=re.MULTILINE | re.IGNORECASE)
        if len(blocks) > 1:
            for i in range(1, len(blocks), 2):
                role = blocks[i].lower()
                content = blocks[i+1].strip()
                if content:
                    messages.append({"role": role, "content": content})
        else:
            if instructions.strip():
                messages.append({"role": "system", "content": instructions.strip()})

        # Extract description
        desc_match = re.search(r'### Description\n(.*?)(?=\n### |$)', body, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract Few-Shot Assertions / testData
        test_data = []
        few_shot_match = re.search(r'### Few-Shot Assertions\n(.*)', body, re.DOTALL)
        if few_shot_match:
            few_shots_text = few_shot_match.group(1).strip()
            # Try new format with code blocks first
            blocks = re.findall(r'\*\*Input Context:\*\*\n```yaml\n(.*?)\n```\n\*\*Asserted Output:\*\*\n```text\n(.*?)\n```', few_shots_text, re.DOTALL)
            if not blocks:
                # Fallback for old format
                blocks = re.findall(r'Input Context:\s*"(.*?)"\nAsserted Output:\s*"(.*?)"', few_shots_text, re.DOTALL)
            for inp_str, out_str in blocks:
                try:
                    inp_dict = yaml.safe_load(inp_str)
                    if not isinstance(inp_dict, dict):
                        inp_dict = {"input": inp_str}
                except:
                    inp_dict = {"input": inp_str}
                test_data.append({"inputs": inp_dict, "expected": [out_str]})

        skill_dict = {
            "name": name,
            "description": description,
            "variables": vars_data,
            "metadata": skill_metadata,
            "messages": messages,
            "instructions": instructions,
            "testData": test_data,
            "path": path
        }
        
        # Trigger strict schema validation for the skill section
        from promptops.validation import PromptSchema
        from typing import cast, Any
        try:
            # Inject defaults for fields required by PromptSchema but not normally present in skills.md
            val_dict = cast(dict[str, Any], skill_dict.copy())
            val_dict.setdefault("model", "default")
            val_dict.setdefault("modelParameters", {"temperature": 0.0})
            val_dict.setdefault("evaluators", [])
            
            # Inject required metadata if missing
            if not val_dict.get("metadata"):
                val_dict["metadata"] = {}
            val_dict["metadata"].setdefault("domain", "unknown")
            val_dict["metadata"].setdefault("complexity", "low")
            
            # Inject a dummy user message if only one message is present
            if "messages" in val_dict and len(val_dict["messages"]) == 1:
                val_dict["messages"].append({"role": "user", "content": "Execute."})
            
            # Remove 'path' before passing to PromptSchema if it is not a schema field
            if "path" in val_dict:
                del val_dict["path"]
            
            PromptSchema(**val_dict)
            
            # Restore 'path' for downstream compatibility
            val_dict["path"] = skill_dict.get("path")
        except Exception as e:
            raise ValueError(f"Schema validation failed for skill '{name}' in {path}: {e}")

        skills.append(skill_dict)
    return {"metadata": metadata, "skills": skills, "path": path}

def _get_words(text: str) -> set:
    """Missing docstring."""
    words = set()
    for w in re.findall(r'[a-z]+|[0-9]+', text.lower()):
        if w.isdigit():
            words.add(str(int(w)))
        else:
            words.add(w)
    return words

def resolve_skill_from_path(path: Path, skills_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Heuristically (fuzzy) resolve a skill from a prompt file path.
    """
    stem = path.name
    for ext in ['.prompt.yaml', '.prompt.yml', '.prompt.md', '.yaml', '.py']:
        if stem.endswith(ext):
            stem = stem[:-len(ext)]
            break
            
    stem_clean = re.sub(r'^\d+_', '', stem).lower()
    stem_words = _get_words(stem_clean)
    
    best_match = None
    best_score = 0
    best_skill_len = float('inf')
    
    for skill in skills_list:
        skill_name_clean = skill.get("name", "").lower()
        skill_words = _get_words(skill_name_clean)
        
        score = len(stem_words & skill_words)
        if score > best_score or (score > 0 and score == best_score and len(skill_words) < best_skill_len):
            best_score = score
            best_match = skill
            best_skill_len = len(skill_words)
            
    if not best_match or best_score == 0:
        m = re.match(r'^(\d+)_', stem)
        if m:
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(skills_list):
                best_match = skills_list[idx]
                best_score = 1
                
    if best_match and best_score > 0:
        return best_match
    return None

def resolve_fallback_prompt(path_obj: Path) -> Optional[Dict[str, Any]]:
    """
    Resolves a missing prompt file by searching for and extracting skills from a central markdown manifest.
    Preserves multi-role message arrays when building the fallback prompt.
    """
    skills_md = path_obj.parent / "skills.md"
    if skills_md.exists():
        manifest = parse_skill_manifest(skills_md)
        best_match = resolve_skill_from_path(path_obj, manifest.get("skills", []))
        if best_match:
            messages = best_match.get("messages")
            if not messages:
                messages = [{"role": "system", "content": best_match.get("instructions", "")}]
            return {
                "name": best_match["name"],
                "description": best_match.get("description", ""),
                "variables": best_match.get("variables", []),
                "messages": messages,
                "testData": best_match.get("testData", [])
            }
    return None

def optimize_prompt(text: str) -> str:
    """
    Simulates the Prompt Optimizer locally without network calls.
    Returns an optimized version of the input text.
    """
    if not text:
        return text
    optimized = text.strip()
    return f"{optimized}\n\n# Note: Optimized for clarity and instruction following."

def sanitize_prompt(text: str) -> str:
    """
    Simulates the Prompt Sanitiser locally without network calls.
    Removes sensitive placeholders and formatting issues.
    """
    if not text:
        return text
    text = re.sub(r'https?://[^\s]+', '[REDACTED_URL]', text)
    text = re.sub(r'(?i)(api[_-]?key)\s*[:=]\s*[A-Za-z0-9_-]+', r'\1=[REDACTED_SECRET]', text)
    text = re.sub(r'(?i)(password)\s*[:=]\s*[A-Za-z0-9_-]+', r'\1=[REDACTED_SECRET]', text)
    text = re.sub(r'\[\d+\]', '', text)
    return text.strip()
