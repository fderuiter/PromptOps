#!/usr/bin/env python3
"""
Enrich Prompt Files - Automation Script

## What is this?
This script scans prompt YAML files and automatically enriches them with missing
metadata (such as `domain`, `complexity`, `tags`, and `requires_context`) and
inferential descriptions for variables declared in the `messages` block.

## Why use it?
- **Reduces Cognitive Load:** Manually writing descriptions for every variable
  in a complex prompt chain is tedious. This script uses heuristics to do it for you.
- **Maintains Consistency:** Ensures all prompts have the necessary metadata
  for categorization and search functionality across the repository.

> [!NOTE]
> This script uses a heuristic approach based on the file path, variable names,
> and surrounding context. It does **not** use an LLM API to infer descriptions.

## How to use it?

### Usage Examples

1. **Dry Run** (Preview changes without modifying files):
   ```bash
   python3 tools/tools/scripts/enrich_prompts.py --dry-run
   ```

2. **Enrich a Specific File**:
   ```bash
   python3 tools/tools/scripts/enrich_prompts.py --file prompts/my_prompt.prompt.yaml
   ```

3. **Enrich All Prompts**:
   ```bash
   python3 tools/tools/scripts/enrich_prompts.py
   ```
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


# Configure yaml to use block scalars for multiline strings
def str_presenter(dumper, data):
    """Missing docstring."""
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

from promptops.utils import ROOT, extract_template_vars, iter_prompt_files, load_yaml

PROMPTS_DIR = ROOT / "prompts"

# ────────────────────────────────────────────────────────────────────────────
# 1.  Domain & tag inference from directory path
# ────────────────────────────────────────────────────────────────────────────

DOMAIN_MAP: dict[str, str] = {
    "business":      "business",
    "clinical":      "clinical",
    "communication": "communication",
    "management":    "management",
    "meta":          "meta",
    "regulatory":    "regulatory",
    "scientific":    "scientific",
    "technical":     "technical",
}

# Human-friendly labels for sub-directories used as tags
TAG_LABELS: dict[str, str] = {
    "cfo":                    "finance",
    "cx":                     "customer-experience",
    "hr_finance":             "hr-finance",
    "market_research":        "market-research",
    "vp_tech_innovation":     "tech-innovation",
    "data_management":        "data-management",
    "data":                   "data",
    "eclinical_integration":  "eclinical-integration",
    "epro":                   "epro",
    "imaging":                "medical-imaging",
    "medical_writing":        "medical-writing",
    "monitoring":             "monitoring",
    "protocol":               "protocol-design",
    "rtsm":                   "rtsm",
    "safety":                 "safety",
    "site_acquisition":       "site-acquisition",
    "trial_execution":        "trial-execution",
    "adjudication":           "adjudication",
    "cra":                    "cra",
    "forms":                  "forms",
    "clinical_research_manager": "clinical-research-management",
    "executive":              "executive",
    "innovation":             "innovation",
    "leadership":             "leadership",
    "medical_director":       "medical-director",
    "operations":             "operations",
    "personal_effectiveness": "personal-effectiveness",
    "project_management":     "project-management",
    "study_director":         "study-director",
    "training":               "training",
    "vp_statistics":          "statistics",
    "adherence":              "regulatory-adherence",
    "administrative":         "regulatory-admin",
    "compliance":             "compliance",
    "device_specifics":       "medical-devices",
    "food_safety":            "food-safety",
    "quality":                "quality",
    "strategy":               "regulatory-strategy",
    "submissions":            "submissions",
    "biosafety":              "biosafety",
    "bioskills":              "skill",
    "biostatistics":          "biostatistics",
    "chemical_characterization": "chemical-characterization",
    "coa":                    "clinical-outcome-assessment",
    "microbiology":           "microbiology",
    "pathology":              "pathology",
    "sterility":              "sterility",
    "architecture":           "architecture",
    "design":                 "design",
    "devops":                 "devops",
    "documentation":          "documentation",
    "languages":              "programming-languages",
    "repository_refactoring": "repository-refactoring",
    "security":               "security",
    "software_engineering":   "software-engineering",
    "technical_writing":      "technical-writing",
    "testing":                "testing",
    "development":            "business-development",
    "payment":                "payment",
    "selenium_automation":    "selenium",
    "lifecycle":              "sdlc",
    "tasks":                  "engineering-tasks",
    "python":                 "python",
    "rust":                   "rust",
    "typescript":             "typescript",
}


def _path_parts(file_path: Path) -> list[str]:
    """Return path parts relative to prompts dir."""
    try:
        rel = file_path.resolve().relative_to(PROMPTS_DIR.resolve())
    except ValueError:
        return []
    return list(rel.parts[:-1])  # exclude filename


def infer_domain(parts: list[str]) -> str:
    """Missing docstring."""
    if parts:
        return DOMAIN_MAP.get(parts[0], parts[0])
    return "general"


def infer_tags(parts: list[str], name: str) -> list[str]:
    """Produce a short list of tags from path parts and prompt name."""
    tags: list[str] = []
    for p in parts[1:]:  # skip the domain itself
        label = TAG_LABELS.get(p, p.replace("_", "-"))
        if label not in tags:
            tags.append(label)
    # Split prompt name into individual words for tags
    # Handle CamelCase, hyphens, underscores, and special chars
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', ' ', name)
    # Split CamelCase
    cleaned = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned)
    name_words = cleaned.lower().split()
    stop = {"a", "an", "the", "of", "for", "and", "to", "in", "is", "with",
            "from", "by", "on", "my", "your", "i", "its", "it", "or", "as",
            "be", "at", "im", "that", "this", "are", "eli5", "like", "up",
            "how", "you", "me", "we", "so", "do", "can", "not", "no", "has",
            "should", "would", "based", "s", "ii", "iii", "iv", "v"}
    for w in name_words:
        if len(w) > 2 and w not in stop and w not in tags:
            tags.append(w)
            if len(tags) >= 5:
                break
    return tags[:5]


# ────────────────────────────────────────────────────────────────────────────
# 2.  Complexity heuristic
# ────────────────────────────────────────────────────────────────────────────

def infer_complexity(content: dict) -> str:
    """low / medium / high based on variable count and message length."""
    num_vars = len(content.get("variables", []))
    total_msg_len = sum(len(m.get("content", "")) for m in content.get("messages", []))
    if num_vars >= 4 or total_msg_len > 1500:
        return "high"
    elif num_vars >= 2 or total_msg_len > 600:
        return "medium"
    return "low"


# ────────────────────────────────────────────────────────────────────────────
# 3.  requires_context heuristic
# ────────────────────────────────────────────────────────────────────────────

CONTEXT_KEYWORDS = {
    "document", "documents", "pdf", "file", "files", "attachment",
    "uploaded", "context", "source", "reference", "corpus",
    "database", "knowledge_base", "knowledge-base", "retrieval",
    "rag", "external", "uploaded_file", "report",
}


def infer_requires_context(content: dict) -> bool:
    """True if prompt likely needs external documents."""
    all_text = " ".join(
        m.get("content", "") for m in content.get("messages", [])
    ).lower()
    var_names = {v.get("name", "") for v in content.get("variables", [])}
    if var_names & CONTEXT_KEYWORDS:
        return True
    hits = sum(1 for kw in CONTEXT_KEYWORDS if kw in all_text)
    return hits >= 2


# ────────────────────────────────────────────────────────────────────────────
# 4.  Variable description inference
# ────────────────────────────────────────────────────────────────────────────

def _extract_surrounding_context(text: str, var_name: str, window: int = 120) -> str:
    """Return snippet of text surrounding {{var_name}} or <var_name>."""
    pattern = r'(?:\{\{|<)' + re.escape(var_name) + r'(?:\}\}|>)'
    m = re.search(pattern, text)
    if not m:
        return ""
    start = max(0, m.start() - window)
    end = min(len(text), m.end() + window)
    return text[start:end]


def _infer_description_from_inline_label(text: str, var_name: str) -> str | None:
    """Try to extract `{{var}} – description` or ``{{var}}`` – description patterns."""
    patterns = [
        # `{{var}}` – description  or  `{{var}}` — description or `<var>` - description
        r'`?(?:\{\{|<)' + re.escape(var_name) + r'(?:\}\}|>)`?\s*[–—\-]+\s*(.+?)(?:\n|$|;|\.|\\n)',
        # var_name: description (as in inline documentation)
        r'(?:^|\n)\s*[-*]?\s*' + re.escape(var_name) + r'\s*[:=]\s*(.+?)(?:\n|$)',
        # Label: {{var}} (reverse mapping)
        r'(?:^|\n)\s*[-*]?\s*(.+?)\s*[:=]\s*`?(?:\{\{|<)' + re.escape(var_name) + r'(?:\}\}|>)`?',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            desc = m.group(1).strip().rstrip('.')
            # Clean trailing punctuation and excess
            if len(desc) > 5:  # Allow slightly shorter labels like "Context"
                return desc[:150]
    return None


# Common variable name → fallback description mapping
COMMON_VAR_DESCRIPTIONS: dict[str, str] = {
    "input":               "The primary input or query text for the prompt",
    "user_query":          "The exact natural language query provided by the user",
    "user_input":          "The primary input provided by the user",
    "system_context":      "The background rules or operational context for the AI system",
    "system_prompt":       "The system prompt or background instructions for the model",
    "topic":               "The subject or topic to address",
    "text":                "The text content to process",
    "context":             "Background context or supporting information",
    "query":               "The user's question or request",
    "task":                "The task or objective to accomplish",
    "question":            "The question to answer",
    "data":                "The data or dataset to analyze",
    "content":             "The content to work with",
    "output_format":       "The desired output format",
    "language":            "The programming or natural language to use",
    "code":                "The source code to analyze or modify",
    "url":                 "The URL to process or reference",
    "name":                "The name or identifier",
    "description":         "A description of the subject",
    "requirements":        "The requirements or specifications",
    "constraints":         "Any constraints or limitations to consider",
    "audience":            "The target audience for the output",
    "tone":                "The desired tone or style of the output",
    "style":               "The writing or communication style to use",
    "domain":              "The domain or field of expertise",
    "goal":                "The goal or desired outcome",
    "summary":             "A summary of the key information",
    "feedback":            "Feedback or critique to incorporate",
    "examples":            "Example inputs or desired outputs",
    "notes":               "Additional notes, assumptions, or special considerations",
    "instructions":        "Specific instructions or guidelines",
    "role":                "The role or persona to adopt",
    "scenario":            "The scenario or situation to address",
    "policy_block":        "Policy and style guide text for guardrails",
    "end_task":            "The final objective or end goal to accomplish",
    "product":             "The product or offering being discussed",
    "company":             "The company or organization name",
    "industry":            "The industry or sector",
    "stakeholders":        "Key stakeholders involved",
    "timeline":            "The project timeline or schedule",
    "budget":              "Budget details or financial constraints",
    "risks":               "Known risks or potential issues",
    "assumptions":         "Key assumptions underlying the analysis",
    "criteria":            "Evaluation or decision criteria",
    "metrics":             "Key performance indicators or metrics",
    "region":              "Geographic region or market",
    "competitor":          "Competitor name or competitive landscape",
    "objectives":          "Strategic or project objectives",
}


def suggest_variable_description(var_name: str, context: str) -> str:
    """Infer a human-readable description for a variable from context."""
    # 1. Try to extract description from message content (inline labels)
    inline = _infer_description_from_inline_label(context, var_name)
    if inline:
        return inline

    # 2. Try surrounding context
    ctx = _extract_surrounding_context(context, var_name)
    if ctx:
        inline2 = _infer_description_from_inline_label(ctx, var_name)
        if inline2:
            return inline2

    # 3. Check common variable names
    key = var_name.lower().strip()
    if key in COMMON_VAR_DESCRIPTIONS:
        return COMMON_VAR_DESCRIPTIONS[key]

    # 4. Partial match: check if variable name contains a known key
    # Check longer keys first to avoid partial matching on short substrings (e.g., 'text' matching 'system_context')
    for known_key, desc in sorted(COMMON_VAR_DESCRIPTIONS.items(), key=lambda item: len(item[0]), reverse=True):
        if known_key in key or key in known_key:
            return desc

    # 5. Generate from variable name itself
    readable_name = var_name.replace("_", " ").replace("-", " ").strip()
    return f"The {readable_name} to use for this prompt"


# ────────────────────────────────────────────────────────────────────────────
# 5.  Main enrichment logic
# ────────────────────────────────────────────────────────────────────────────

def enrich_file(file_path: Path, dry_run: bool = False) -> bool:
    """Enrich a single prompt file with descriptions and metadata.
    Returns True if the file was modified.
    """
    from promptops.validation import PromptSchema
    
    content = load_yaml(file_path)
    if not content:
        print(f"  SKIP (empty): {file_path}")
        return False

    try:
        PromptSchema(**content)
    except Exception as e:
        print(f"  SKIP (invalid schema or syntax): {file_path}\n  {e}")
        return False

    modified = False
    parts = _path_parts(file_path)

    # ── A. Fill in variable descriptions ────────────────────────────────
    current_vars = content.get("variables", [])
    vars_in_template = set(extract_template_vars(content))
    prompt_name = content.get("name", "")
    content.get("description", "")

    # Extract prompt content for context
    messages = content.get("messages", [])
    system_prompt = next((m.get("content", "") for m in messages if m.get("role") == "system"), "")
    user_prompt = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    combined_context = f"{system_prompt}\n{user_prompt}"

    enriched_vars = []
    for var in current_vars:
        var_name = var.get("name")
        if var_name not in vars_in_template:
            modified = True
            continue

        if var.get("description") == "TODO" or not var.get("description"):
            print(f"  Suggesting description for variable '{var_name}'...")
            suggested_desc = suggest_variable_description(var_name, combined_context)
            if not suggested_desc.startswith("[Automated]"):
                suggested_desc = f"[Automated] {suggested_desc}"
            print(f"    Suggested: {suggested_desc}")

            # Create new var dict to preserve order and fields
            new_var = var.copy()
            new_var["description"] = suggested_desc
            enriched_vars.append(new_var)
            modified = True
        else:
            enriched_vars.append(var)

    # Add any missing variables from template that weren't in current_vars
    existing_names = {v.get("name") for v in enriched_vars}
    for v_name in vars_in_template:
        if v_name not in existing_names:
            print(f"  Adding missing variable '{v_name}' from template...")
            new_desc = suggest_variable_description(v_name, combined_context)
            if not new_desc.startswith("[Automated]"):
                new_desc = f"[Automated] {new_desc}"
            enriched_vars.append({
                "name": v_name,
                "description": new_desc,
                "required": True
            })
            modified = True

    if modified:
        content["variables"] = enriched_vars

    # ── B. Add or complete metadata ─────────────────────────────────────
    metadata = content.get("metadata")
    # Handle missing or null metadata block
    if metadata is None:
        metadata = {}
        content["metadata"] = metadata
        modified = True

    # Infer values if missing
    if "domain" not in metadata:
        metadata["domain"] = infer_domain(parts)
        modified = True
    if "complexity" not in metadata:
        metadata["complexity"] = infer_complexity(content)
        modified = True
    if "tags" not in metadata:
        metadata["tags"] = infer_tags(parts, prompt_name)
        modified = True
    if "requires_context" not in metadata:
        metadata["requires_context"] = infer_requires_context(content)
        modified = True

    if not modified:
        print(f"  OK (already enriched): {file_path}")
        return False

    if dry_run:
        print(f"  DRY-RUN would enrich: {file_path}")
        return True

    # ── Write back ──────────────────────────────────────────────────────
    # Reorder keys for readability: name, version, description, metadata,
    # variables, model, modelParameters, messages, testData, evaluators
    ordered: dict[str, Any] = {}
    key_order = [
        "name", "version", "description", "metadata", "variables",
        "model", "modelParameters", "messages", "testData", "evaluators",
        "last_modified",
    ]
    for k in key_order:
        if k in content:
            ordered[k] = content[k]
    # Any remaining keys not in the predefined order
    for k, v in content.items():
        if k not in ordered:
            ordered[k] = v

    yaml_text = yaml.dump(
        ordered,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    file_path.write_text("---\n" + yaml_text, encoding="utf-8")
    print(f"  ENRICHED: {file_path}")
    return True


def main() -> int:
    """Missing docstring."""
    import argparse
    parser = argparse.ArgumentParser(description="Enrich prompt files with descriptions and metadata")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--file", type=str, default=None,
                        help="Enrich a single file instead of all")
    args = parser.parse_args()

    if args.file:
        p = Path(args.file)
        enrich_file(p, dry_run=args.dry_run)
        return 0

    updated = 0
    total = 0
    for file_path in iter_prompt_files(ROOT):
        total += 1
        if enrich_file(file_path, dry_run=args.dry_run):
            updated += 1

    print(f"\n{'DRY-RUN: ' if args.dry_run else ''}Processed {total} files, "
          f"{updated} enriched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
