# Standardize Prompt Files

id: migration-standardize-prompts
title: "Standardize Prompt Files"
category: maintenance
author: "\<YOUR_NAME\>"
created: 2025-07-18
last_modified: 2025-07-18
tested_model: gpt-4o
temperature: 0.2
tags: [maintenance, prompts, formatting]
-----------------------------------------

## Objective

Standardize all prompt Markdown files in the **proompts** repository so they follow a single, maintainable schema that aligns with the latest prompt‑engineering best practices.

## Target Schema

> Every prompt file **must** contain the following elements, as specified in
> `docs/template_prompt.prompt.yaml`.

### YAML front‑matter (required)

```yaml
id: <kebab-case-unique-id>
title: <Concise descriptive title>
category: <folder/topic>
author: <original author or maintainer>
created: <YYYY-MM-DD>
last_modified: <YYYY-MM-DD>
tested_model: <model name/version>
temperature: <0‑2>
tags: [tag1, tag2, ...]
```

### Body sections (each an H2 heading)

## Purpose

A one‑sentence statement of the prompt’s goal.

## Context

Essential background and assumptions the model needs.

## Instructions

Step‑by‑step directives phrased imperatively.

## Inputs

Bullet list of `{{placeholders}}` with a short description or type.

## Output Format

Description (or example) of the expected result, including any delimiters.

## Additional Notes

Tips, constraints, edge cases, or token budget remarks.

## Example Usage *(optional)*

Copy‑pasteable demonstration: caller input ➜ expected model output.

## References *(optional)*

Links or relative paths to supporting docs/resources.

## Migration Workflow

1. **Clone** the repo and create a new branch (default: `feat/standardize-prompt-format`).
1. **Iterate** through every `*.prompt.yaml` file inside prompt directories:

   * Verify all required fields match `docs/template_prompt.prompt.yaml`.
   * Add missing metadata values (preserve original dates unless instructed otherwise).
   * Move any unmapped text under **Additional Notes**.
1. **Run** `./scripts/validate_prompts.sh` to ensure YAML linting passes.
1. **Validate** prompt schema with `uv run promptops validate`.
1. **Commit** changes in logical chunks and push the branch.
1. **Open** a PR and request review from repository maintainers.

## Interaction Checklist

Before executing, ask the caller to confirm:

* Branch name (press **Enter** to use default).
* Whether to overwrite `created` / `last_modified` dates.
* Any folders or files to exclude from migration.

Await confirmation before proceeding.
