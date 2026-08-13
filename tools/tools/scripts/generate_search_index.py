#!/usr/bin/env python3
"""
Generate Search Index Script

## What is this?
This script generates a `search.json` index file for the static documentation site.

## Why use it?
- **Enables Searchability:** Allows the documentation frontend to provide real-time search across prompts and workflows.
- **Aggregates Metadata:** Extracts titles, descriptions, and tags from YAML files into a single, optimized JSON payload.

## How to use it?
```bash
python3 tools/tools/scripts/generate_search_index.py
```
"""

import json
from pathlib import Path

from promptops.utils import ROOT, iter_prompt_files, iter_workflow_files, load_yaml, iter_skill_manifests, parse_skill_manifest


def extract_compliance(content: dict) -> list[str]:
    """Extract compliance requirements from the metadata block or top-level field."""
    reqs = None
    metadata = content.get("metadata", {})
    if isinstance(metadata, dict):
        reqs = metadata.get("requirements")
    if reqs is None:
        reqs = content.get("requirements")
    
    if reqs is None:
        return []
    if isinstance(reqs, list):
        return [str(r).strip() for r in reqs if r]
    if isinstance(reqs, str):
        if "," in reqs:
            return [r.strip() for r in reqs.split(",") if r.strip()]
        return [reqs.strip()]
    return []


def extract_complexity(content: dict) -> str:
    """Extract complexity from metadata or top-level complexity field."""
    metadata = content.get("metadata", {})
    val = None
    if isinstance(metadata, dict):
        val = metadata.get("complexity")
    if val is None:
        val = content.get("complexity")
    return str(val).strip() if val is not None else ""


def extract_maturity(content: dict) -> str:
    """Extract maturity from metadata or top-level maturity field."""
    metadata = content.get("metadata", {})
    val = None
    if isinstance(metadata, dict):
        val = metadata.get("maturity")
    if val is None:
        val = content.get("maturity")
    return str(val).strip() if val is not None else ""


def extract_audience(content: dict, is_clinical: bool = False) -> list[str]:
    """Dynamically scan variables checking name and description for pre-defined strategic target roles."""
    variables = content.get("variables", [])
    if not isinstance(variables, list):
        return []
        
    ignore_vars = {
        "temp", "api_key", "prompt", "model", "text", "input", 
        "output", "context", "data", "query", "guidelines", "instructions"
    }
    
    role_keywords = {
        "developer": ["developer", "software engineer", "programmer", "coder", "tech lead", "architect"],
        "financial_analyst": ["financial analyst", "analyst", "finance", "auditor", "portfolio manager", "investment"],
        "clinical_specialist": ["clinical", "clinician", "medical", "doctor", "nurse", "surgeon", "healthcare", "physician"],
        "compliance_officer": ["compliance officer", "compliance manager", "regulatory", "legal", "auditor", "compliance auditor"],
        "product_manager": ["product manager", "project manager", "product owner", "scrum master", "manager", "business analyst"]
    }
    
    matched_roles = set()
    
    for var in variables:
        if not isinstance(var, dict):
            continue
        var_name = var.get("name")
        if not isinstance(var_name, str):
            continue
        
        # Helper variables to ignore
        if var_name.lower() in ignore_vars:
            continue
            
        var_desc = var.get("description", "")
        if not isinstance(var_desc, str):
            var_desc = ""
            
        combined_text = f"{var_name} {var_desc}".lower().replace("_", " ")
        
        for role, keywords in role_keywords.items():
            for kw in keywords:
                if kw in combined_text:
                    matched_roles.add(role)
                    break
        
        # Special clinical reviewer case
        if "reviewer" in combined_text and is_clinical:
            matched_roles.add("clinical_specialist")
                
    return sorted(list(matched_roles))


def build_search_entry(title: str, description: str, base_tags: list, url: str, entry_type: str, content: dict, path: Path) -> dict:
    """Build the search entry with standard and new high-level fields, plus prefixed tags."""
    # Determine if clinical domain
    is_clinical = False
    if "clinical" in str(path).lower():
        is_clinical = True
    metadata = content.get("metadata", {})
    if isinstance(metadata, dict) and metadata.get("domain", "").lower() == "clinical":
        is_clinical = True
    if any("clinical" in t.lower() for t in base_tags):
        is_clinical = True
        
    compliance = extract_compliance(content)
    complexity = extract_complexity(content)
    maturity = extract_maturity(content)
    audience = extract_audience(content, is_clinical)
    
    # Inject prefixed tags
    tags_list = list(base_tags)
    if complexity:
        tags_list.append(f"complexity:{complexity}")
    if maturity:
        tags_list.append(f"maturity:{maturity}")
    for comp in compliance:
        tags_list.append(f"compliance:{comp}")
    for aud in audience:
        tags_list.append(f"audience:{aud}")
        
    # Deduplicate tags
    seen_tags = set()
    unique_tags = []
    for t in tags_list:
        t_clean = t.strip()
        if t_clean and t_clean not in seen_tags:
            seen_tags.add(t_clean)
            unique_tags.append(t_clean)
            
    tags_str = ", ".join(unique_tags)
    
    return {
        "title": title,
        "description": description,
        "tags": tags_str,
        "url": url,
        "type": entry_type,
        "compliance": compliance,
        "complexity": complexity,
        "maturity": maturity,
        "audience": audience
    }


def generate_index(output_path: str = "search.json"):
    """Generate search index of skills, standalone prompts, and workflows."""
    search_data = []
    manifested_dirs = set()
    prompts_dir = ROOT / "prompts"

    # Iterate through all skill manifest files
    for path in iter_skill_manifests(prompts_dir):
        try:
            manifest = parse_skill_manifest(path)
            rel_path = path.relative_to(ROOT)
            manifested_dirs.add(path.parent)

            manifest_metadata = manifest.get("metadata") or {}
            
            # Skip draft manifests
            if manifest_metadata.get("status") == "draft":
                continue

            for skill in manifest.get("skills", []):
                skill_metadata = skill.get("metadata") or {}
                
                # Skip draft skills
                if skill_metadata.get("status") == "draft":
                    continue

                # Merge metadata: skill overrides manifest metadata
                merged_metadata = {**manifest_metadata, **skill_metadata}

                skill_content = {
                    "metadata": merged_metadata,
                    "variables": skill.get("variables", []),
                    "requirements": skill.get("requirements") or merged_metadata.get("requirements")
                }

                from promptops.tags import extract_tags
                tags = extract_tags(skill_content)

                entry = build_search_entry(
                    title=skill["name"],
                    description=skill.get("description", ""),
                    base_tags=tags,
                    url=f"{rel_path}#skill-{skill['name'].lower().replace(' ', '-')}",
                    entry_type="skill",
                    content=skill_content,
                    path=path
                )
                search_data.append(entry)
        except Exception as e:
            print(f"Error indexing manifest {path}: {e}")

    # Iterate through all prompt files using the utility
    for path in iter_prompt_files(prompts_dir):
        # Skip prompts that are covered by skill manifests
        if path.parent in manifested_dirs:
            continue

        content = load_yaml(path)
        if content.get('metadata', {}).get('status') == 'draft' or content.get('status') == 'draft':
            continue

        # Calculate the web-accessible path relative to the repository root
        try:
            rel_path = path.relative_to(ROOT)
        except ValueError:
            # Should not happen if iter_prompt_files uses ROOT/prompts
            continue

        from promptops.tags import extract_tags
        tags = extract_tags(content)
                
        entry = build_search_entry(
            title=content.get('name', str(rel_path)),
            description=content.get('description', ''),
            base_tags=tags,
            url=str(rel_path),
            entry_type="prompt",
            content=content,
            path=path
        )
        search_data.append(entry)

    # Iterate through all workflow files
    workflows_dir = ROOT / "workflows"
    if workflows_dir.exists():
        for path in iter_workflow_files(workflows_dir):
            content = load_yaml(path)
            if content.get('metadata', {}).get('status') == 'draft' or content.get('status') == 'draft':
                continue
            try:
                rel_path = path.relative_to(ROOT)
            except ValueError:
                continue

            from promptops.tags import extract_tags
            tags = extract_tags(content)

            entry = build_search_entry(
                title=content.get('name', str(rel_path)),
                description=content.get('description', ''),
                base_tags=tags,
                url=str(rel_path),
                entry_type="workflow",
                content=content,
                path=path
            )
            search_data.append(entry)

    # Output to the specified path (defaults to repo root if just filename)
    out_file = ROOT / output_path
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2)

    print(f"Generated {out_file} with {len(search_data)} entries.")


if __name__ == "__main__":
    generate_index("search.json")
