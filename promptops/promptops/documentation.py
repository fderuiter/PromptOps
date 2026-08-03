"""Module docstring."""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
from promptops.utils import load_yaml, derive_category, iter_prompt_files, iter_workflow_files, derive_title

@dataclass(frozen=True)
class DocItem:
    """Missing docstring."""
    title: str
    path: Path
    category: str
    item_type: str
    description: str = ""
    graph_mermaid: Optional[str] = None



from promptops.sync import DirectoryReconciler
from promptops.skill_export import process_skills, detect_skill

def generate_docs(prompts_dir: str, output_dir: str, repo_url: str, branch: str = "main", check: bool = False) -> bool:
    """Missing docstring."""
    prompts_dir = os.environ.get('PROMPTOPS_REGISTRY', prompts_dir)
    prompts_path = Path(prompts_dir)
    docs_path = Path(output_dir)
    sync_ok = True
    
    if not prompts_path.exists():
        print(f"Directory {prompts_dir} does not exist.")
        return False

    prompts_reconciler = DirectoryReconciler(docs_path / "prompts", dry_run=check)
    workflows_reconciler = DirectoryReconciler(docs_path / "workflows", dry_run=check)
    js_reconciler = DirectoryReconciler(docs_path / "js", dry_run=check)

    def write_root_file(path: Path, content: str) -> bool:
        """Missing docstring."""
        path = path.resolve()
        would_write = True
        if path.exists():
            if path.read_text(encoding='utf-8') == content:
                would_write = False
        if not check and would_write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        return would_write

    items = []
    
    if not check:
        docs_path.mkdir(parents=True, exist_ok=True)
        out_prompts_dir = docs_path / "prompts"
        out_prompts_dir.mkdir(parents=True, exist_ok=True)
        out_workflows_dir = docs_path / "workflows"
        out_workflows_dir.mkdir(parents=True, exist_ok=True)
        
        process_skills(prompts_path, docs_path)
    else:
        out_prompts_dir = docs_path / "prompts"
        out_workflows_dir = docs_path / "workflows"
    
    for path in iter_prompt_files(str(prompts_path)):
        try:
            raw_content = path.read_text(encoding='utf-8')
        except Exception as e:
            raw_content = f"# Error reading source file: {e}"
        
        data = load_yaml(str(path))
        if data is None:
            continue
            
        if data.get('metadata', {}).get('status') == 'draft':
            continue
            
        if detect_skill(raw_content, data):
            if check:
                print(f"Drift detected: Unconsolidated skill file found: {path}")
                sync_ok = False
            continue

        title = derive_title(path, data)
        desc = data.get('description', 'No description provided.')
        
        try:
            rel_to_prompts = path.relative_to(prompts_path / "prompts")
        except ValueError:
            rel_to_prompts = path.relative_to(prompts_path)
            
        output_file = out_prompts_dir / rel_to_prompts.with_suffix(".md")
        
        if not check:
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if repo_url:
            github_url = f"{repo_url}/blob/{branch}/{path.relative_to(prompts_path.parent)}"
            link_md = f"[View Source YAML]({github_url})"
        else:
            link_md = ""
            
        content = f"---\ntitle: {title}\n---\n\n# {title}\n\n{desc}\n\n{link_md}\n\n```yaml\n{raw_content}\n```\n"
        
        would_write = prompts_reconciler.write_file(output_file, content)
        if check and would_write:
            print(f"Drift detected: Content mismatch or missing file {output_file}")
            sync_ok = False
        
        items.append(DocItem(
            title=title,
            path=output_file,
            category=derive_category(path, prompts_path, data),
            item_type='prompt'
        ))
        
    workflows_path = prompts_path.parent / "workflows"
    if workflows_path.exists():
        for path in iter_workflow_files(str(workflows_path)):
            data = load_yaml(str(path))
            if data is None:
                continue
                
            if data.get('metadata', {}).get('status') == 'draft':
                continue
                
            title = derive_title(path, data)
            desc = data.get('description', 'No description provided.')
            
            try:
                from promptops.validation import WorkflowSchema
                from promptops.visualization import MermaidGrapher
                wf = WorkflowSchema(**data)
                mermaid = MermaidGrapher.generate(wf)
            except Exception as e:
                print(f"Error parsing {path} for mermaid generation: {e}")
                mermaid = ""
                if check:
                    print(f"Drift detected: Workflow schema validation failed for {path}: {e}")
                    sync_ok = False

            
            filename = path.stem.replace('.workflow', '') + ".md"
            output_file = out_workflows_dir / filename
            
            if not check:
                output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if repo_url:
                github_url = f"{repo_url}/blob/{branch}/{path.relative_to(workflows_path.parent)}"
                link_md = f"[View Source YAML]({github_url})"
            else:
                link_md = ""
                
            mermaid_block = f"## Workflow Diagram\n\n```mermaid\n{mermaid}\n```\n" if mermaid else ""
            
            content = f"---\ntitle: {title}\n---\n\n# {title}\n\n{desc}\n\n{mermaid_block}\n{link_md}\n"
            
            would_write = workflows_reconciler.write_file(output_file, content)
            if check and would_write:
                print(f"Drift detected: Content mismatch or missing workflow {output_file}")
                sync_ok = False
            
            category = derive_category(path, workflows_path, data)
                
            items.append(DocItem(
                title=title,
                path=output_file,
                category=category,
                item_type='workflow'
            ))
        
    registry: Dict[str, Dict[str, List[DocItem]]] = {}
    for item in items:
        if item.category not in registry:
            registry[item.category] = {'prompt': [], 'workflow': []}
        registry[item.category][item.item_type].append(item)
        if item.item_type == 'workflow':
            if "Workflows" not in registry:
                registry["Workflows"] = {'prompt': [], 'workflow': []}
            registry["Workflows"]['workflow'].append(item)
        
    for category, types in registry.items():
        if not any(types.values()):
            continue
            
        filename = category.lower().replace(" ", "_") + ".md"
        out_path = docs_path / filename
        
        md = [f"---\ntitle: {category}\n---\n\n# {category}\n"]
        
        if types['prompt'] and category != "Workflows":
            md.append("## Prompts")
            for p in sorted(types['prompt'], key=lambda x: x.title.lower()):
                rel_path = os.path.relpath(p.path, docs_path)
                md.append(f"- [{p.title}]({rel_path})")
                
        if types['workflow']:
            if category != "Workflows":
                md.append("\n## Workflows")
            for w in sorted(types['workflow'], key=lambda x: x.title.lower()):
                rel_path = os.path.relpath(w.path, docs_path)
                md.append(f"- [{w.title}]({rel_path})")
                
        content = "\n".join(md)
        would_write = write_root_file(out_path, content)
        if check and would_write:
            print(f"Drift detected: Content mismatch or missing category {out_path}")
            sync_ok = False
        

    js_dir = docs_path / 'js'
    js_reconciler.touched_files.add((js_dir / "fix-accessibility.js").resolve())
    # --- GENERATE EXPLORER CATALOG ---
    if not check:
        import json
        import sys
        sys.path.insert(0, os.environ.get('PROMPTOPS_ROOT', os.getcwd()))
        from mcp_server import handle_list_tools
        import asyncio
        
        # We need to run handle_list_tools to get all tools. 
        # But handle_list_tools is async.
        loop = asyncio.get_event_loop()
        tools_list = loop.run_until_complete(handle_list_tools())
        
        catalog = []
        for t in tools_list:
            catalog.append({
                "name": t.name,
                "description": t.description,
                "inputSchema": t.inputSchema
            })
            
        catalog.sort(key=lambda x: x["name"])
        js_dir.mkdir(parents=True, exist_ok=True)
        js_reconciler.write_file(js_dir / "tools_catalog.json", json.dumps(catalog, indent=2))
        
        # Write explorer.js
        explorer_js = '''
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("tool-explorer");
    if (!container) return;
    
    // Create UI
    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Search tools by name or description...";
    searchInput.style.width = "100%";
    searchInput.style.padding = "8px";
    searchInput.style.marginBottom = "16px";
    
    const listContainer = document.createElement("div");
    
    container.appendChild(searchInput);
    container.appendChild(listContainer);
    
    let allTools = [];
    
    function renderTree(obj) {
        if (!obj || typeof obj !== "object") return String(obj);
        const ul = document.createElement("ul");
        for (const [key, value] of Object.entries(obj)) {
            const li = document.createElement("li");
            if (typeof value === "object" && value !== null) {
                const details = document.createElement("details");
                const summary = document.createElement("summary");
                summary.innerHTML = "<strong>" + key + "</strong>";
                details.appendChild(summary);
                details.appendChild(renderTree(value));
                li.appendChild(details);
            } else {
                li.innerHTML = "<strong>" + key + ":</strong> " + value;
            }
            ul.appendChild(li);
        }
        return ul;
    }
    
    function renderTools(tools) {
        listContainer.innerHTML = "";
        tools.forEach(t => {
            const card = document.createElement("div");
            card.style.border = "1px solid #ccc";
            card.style.padding = "16px";
            card.style.marginBottom = "16px";
            card.style.borderRadius = "4px";
            
            const title = document.createElement("h3");
            title.textContent = t.name;
            title.style.marginTop = "0";
            
            const desc = document.createElement("p");
            desc.textContent = t.description;
            
            const schemaTitle = document.createElement("h4");
            schemaTitle.textContent = "Input Schema";
            
            card.appendChild(title);
            card.appendChild(desc);
            card.appendChild(schemaTitle);
            card.appendChild(renderTree(t.inputSchema));
            
            listContainer.appendChild(card);
        });
    }
    
    // Determine path prefix based on the script location to support multi-level static folders
    const currentScript = document.currentScript || document.querySelector('script[src*="explorer.js"]');
    let basePath = "./";
    if (currentScript) {
        const src = currentScript.getAttribute("src");
        const index = src.indexOf("js/explorer.js");
        if (index !== -1) {
            basePath = src.substring(0, index);
        }
    }
    
    fetch(`${basePath}js/tools_catalog.json`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            allTools = data;
            renderTools(allTools);
        })
        .catch(e => {
            console.error("Failed to load catalog", e);
            listContainer.innerHTML = "<p>Failed to load tool schemas.</p>";
        });
    
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allTools.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.description.toLowerCase().includes(query)
        );
        renderTools(filtered);
    });
});
'''
        js_reconciler.write_file(js_dir / "explorer.js", explorer_js)

        # Write fix-accessibility.js
        fix_accessibility_js = '''
const disableHiddenPaletteInputs = () => {
  document.querySelectorAll('input.md-option[aria-hidden="true"]').forEach((el) => {
    el.disabled = true;
    el.tabIndex = -1;
  });
};
document.addEventListener("DOMContentLoaded", disableHiddenPaletteInputs);
document.addEventListener("pjax:complete", disableHiddenPaletteInputs);
'''
        js_reconciler.write_file(js_dir / "fix-accessibility.js", fix_accessibility_js)

    else:
        # Register JS files as touched in check mode, since they are generated externally
        js_reconciler.touched_files.add((js_dir / "tools_catalog.json").resolve())
        js_reconciler.touched_files.add((js_dir / "explorer.js").resolve())
        js_reconciler.touched_files.add((js_dir / "fix-accessibility.js").resolve())

    # Generate index.md
    index_path = docs_path / "index.md"
    index_md = [
        "---",
        "title: Knowledge Base Home",
        "---",
        "",
        "# Proompts Knowledge Base",
        "",
        "Welcome to the Proompts documentation. Select a category below:",
        ""
    ]
    
    for category in sorted(registry.keys()):
        if not any(registry[category].values()):
            continue
        filename = category.lower().replace(" ", "_") + ".md"
        index_md.append(f"- [{category}]({filename})")
        
    content = "\n".join(index_md)
    would_write = write_root_file(index_path, content)
    if check and would_write:
        print(f"Drift detected: Content mismatch or missing index {index_path}")
        sync_ok = False

    stale_count = 0
    stale_count += prompts_reconciler.reconcile()
    stale_count += workflows_reconciler.reconcile()
    stale_count += js_reconciler.reconcile()
    if check and stale_count > 0:
        print(f"Drift detected: {stale_count} stale files or directories found.")
        sync_ok = False

    if check:
        if sync_ok:
            print("Documentation is up to date.")
        else:
            print("Documentation drift detected.")
    else:
        print(f"Generated index.md at {index_path}")
        print(f"Documentation generated at {output_dir}")
        
    return sync_ok

