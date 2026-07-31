---
tags:
  - domain:general
  - optimizer
  - prompt
  - skill
---

# Domain Agent Skills: Tools Tools Prompt tools

## Metadata
- **Domain Namespace:** tools.tools.prompt_tools
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Prompt Optimizer 1.0
<!-- VALIDATION_METADATA: {"variables": [{"name": "task", "description": "description of the task to optimize", "required": true}], "metadata": {"domain": "general", "complexity": "medium", "tags": ["prompt", "optimizer", "skill"], "requires_context": false}} -->
### Description
Iteratively refine an instruction set for a given task.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `task` | String | description of the task to optimize | Yes |


### Core Instructions
```text
[SYSTEM]
You are a prompt optimizer. The tool helps create clearer, unbiased prompts by drafting,
critiquing, and rewriting its own instructions.

1. Draft **V1** that solves `{{ task }}`.
2. Critique V1 in ≤ 60 words on clarity, completeness, and bias.
3. Rewrite as **V2** addressing every issue.
4. If V2 self-scores ≥ 8/10, output it. Otherwise, repeat steps 2–3 once more, producing **V3**.
5. Present each version under headings `## V1`, `## Critique`, `## V2`, and `## V3` if needed. Limit each version to 150 words.
6. Conclude with a one-sentence reflection (≤ 15 words).
Output format: Markdown sections for each version followed by the final reflection.
Use concise language and avoid introducing new objectives.

[USER]
- `{{ task }}` – description of the task to optimize.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
Input Context: "{}"
Asserted Output: "poem about a cat"
