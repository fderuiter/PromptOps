#!/usr/bin/env python3
"""
Broken Link Checker

## What is this?
Scans Markdown files for broken internal links and missing anchors across the documentation and prompt directories.

## Why use it?
- **Maintains Documentation Quality:** Ensures users don't encounter dead ends while navigating the repository.
- **Automated Validation:** Catches broken links during CI/CD or local testing before they are merged.

## How to use it?
Run this script from the root of the repository:
```bash
python3 tools/tools/scripts/check_broken_links.py
```
"""

import re
import sys
import urllib.parse
from pathlib import Path
from typing import List, Tuple, Set

from promptops.utils import iter_markdown_files, ROOT, PROMPTS_DIR, WORKFLOWS_DIR, walk_workspace

# Configuration
DOCS_DIR = ROOT / "docs"
ROOT_DIR = ROOT
TOOLS_DIR = ROOT / "tools"

# Regex to find links: [text](url)
# This is a simple regex and might miss some edge cases, but covers standard markdown links
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Regex to catch empty parentheses links: [text]() or [text]( )
EMPTY_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(\s*\)')

# Regex to catch ellipsis in link targets: [text](https://.../something)
ELLIPSIS_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\([^)]*\.\.\.[^)]*\)')

# Regex to catch unclosed brackets in links: [text](url without closing parenthesis
UNCLOSED_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\([^)\s]+[\s]*$')

# Static blocklist of known incorrect or hallucinated domain paths
BLOCKED_DOMAINS = [
    "www.claude.com/blog",
    "docs.anthropic.com/docs/en",
    "platform.claude.com/cookbook"
]

def normalize_anchor(anchor: str) -> str:
    """Normalize anchors using simplified GitHub-style formatting."""
    anchor = anchor.strip().lower().replace(' ', '-')
    return re.sub(r'[^\w\-]', '', anchor)

def get_all_markdown_files() -> List[Path]:
    """Return a list of all markdown files to scan."""
    files = []
    if DOCS_DIR.exists():
        files.extend(list(iter_markdown_files(DOCS_DIR)))
    if PROMPTS_DIR.exists():
        files.extend(list(iter_markdown_files(PROMPTS_DIR)))
    if WORKFLOWS_DIR.exists():
        files.extend(list(iter_markdown_files(WORKFLOWS_DIR)))
    if TOOLS_DIR.exists():
        files.extend(list(iter_markdown_files(TOOLS_DIR)))
    # Also check root files like README.md, CONTRIBUTING.md
    for root, dirs, filenames in walk_workspace(ROOT_DIR):
        if Path(root).resolve() == ROOT_DIR.resolve():
            for f in filenames:
                if f.endswith(".md"):
                    files.append(ROOT_DIR / f)
            break
    return files

def get_anchors_in_file(path: Path) -> Set[str]:
    """Extracts all anchors (headers and id attributes) from a file."""
    anchors: set[str] = set()
    try:
        content = path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"⚠️ Warning: Could not read {path}: {e}")
        return anchors

    # GitHub-style header anchors:
    # # Header Name -> #header-name
    # This is an approximation. GitHub's algorithm is complex (handling special chars, etc.)
    # We will use a simplified version: lowercase, replace spaces with dashes, remove non-alphanumeric
    for line in content.splitlines():
        if line.strip().startswith('#'):
            # Remove leading #'s and whitespace
            header = line.lstrip('#').strip()
            # Generate ID
            anchor = normalize_anchor(header)
            anchors.add(anchor)
    
    # HTML anchors: <a name="foo"> or <div id="foo">
    # Matches id="foo" or name="foo"
    for match in re.findall(r'(?:id|name)=["\']([^"\']+)["\']', content):
        anchors.add(normalize_anchor(match))
        
    return anchors

def check_link(source_file: Path, link: str, target_anchors_cache: dict) -> Tuple[bool, str]:
    """
    Validates a single link.
    Returns (is_valid, error_message).
    """
    # Ignore external links
    if link.startswith(('http://', 'https://', 'mailto:', '#')):
        # We ignore pure anchor links (#section) for now to keep it simple, 
        # or we could resolve them against source_file.
        # Let's check pure anchors too.
        if link.startswith('#'):
            target_file = source_file
            anchor = link[1:]
        else:
            return True, ""
    else:
        # Parse URL (handle query params, though rare in file links)
        parsed = urllib.parse.urlparse(link)
        path_part = parsed.path
        anchor = parsed.fragment
        
        # Absolute path relative to repo root (starts with /)
        if path_part.startswith('/'):
            target_file = ROOT_DIR / path_part.lstrip('/')
        else:
            # Relative path
            target_file = (source_file.parent / path_part).resolve()

    # Check if file exists
    if not target_file.exists():
        return False, f"File not found: {link}"
    
    # If it's a directory, it's valid for file browsing
    if target_file.is_dir():
         return True, ""

    # Check anchor if present
    if anchor:
        anchor = normalize_anchor(anchor)
        if str(target_file) not in target_anchors_cache:
            target_anchors_cache[str(target_file)] = get_anchors_in_file(target_file)
        
        known_anchors = target_anchors_cache[str(target_file)]
        if anchor not in known_anchors:
            # Fallback: maybe the manual anchor definition was different?
            # It's hard to be perfect here. We'll report it as a warning or error.
            # For strictness, let's report error.
            return False, f"Anchor #{anchor} not found in {target_file.name}"

    return True, ""

def main():
    """Missing docstring."""
    print("🔗 Checking for broken links...")
    markdown_files = get_all_markdown_files()
    broken_links_count = 0
    target_anchors_cache = {}

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            # Check for empty parentheses
            for match in EMPTY_LINK_PATTERN.finditer(line):
                print(f"❌ {file_path}:{line_no}\n   [{match.group(1)}]() -> Placeholder link with empty parentheses")
                broken_links_count += 1
                
            # Check for ellipsis in links
            for match in ELLIPSIS_LINK_PATTERN.finditer(line):
                print(f"❌ {file_path}:{line_no}\n   [{match.group(1)}](...) -> Placeholder link with ellipsis")
                broken_links_count += 1
                
            # Check for unclosed brackets
            for match in UNCLOSED_LINK_PATTERN.finditer(line):
                print(f"❌ {file_path}:{line_no}\n   [{match.group(1)}](... -> Malformed link with unclosed brackets")
                broken_links_count += 1

            for match in LINK_PATTERN.finditer(line):
                text = match.group(1)
                link = match.group(2)
                
                # Check against blocklist
                is_blocked = False
                for domain in BLOCKED_DOMAINS:
                    if domain in link:
                        print(f"❌ {file_path}:{line_no}\n   [{text}]({link}) -> Blocked domain or path ({domain})")
                        broken_links_count += 1
                        is_blocked = True
                        break
                        
                if is_blocked:
                    continue

                is_valid, error = check_link(file_path, link, target_anchors_cache)
                if not is_valid:
                    print(
                        f"❌ {file_path}:{line_no}\n"
                        f"   [{text}]({link}) -> {error}"
                    )
                    broken_links_count += 1

    if broken_links_count > 0:
        print(f"\nFound {broken_links_count} broken links.")
        sys.exit(1)
    else:
        print("\n✅ All internal links verified.")
        sys.exit(0)

if __name__ == "__main__":
    main()
