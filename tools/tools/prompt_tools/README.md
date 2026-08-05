# Prompt Engineering Utilities 🛠️

This directory contains **Meta-Prompts**, agent scripts, and specialized utilities for maintaining, refining, and standardizing the prompt library.

> [!NOTE]
> Unlike the core meta-prompts located in `prompts/meta/` (which are production-ready YAML files), this folder serves as a "workshop" for experimental tools, maintenance scripts, and long-form agent instructions.

## Table of Contents

- [Why this directory exists?](#why-this-directory-exists)
- [Tool Descriptions](#tool-descriptions)
  - [Architecture Review Pipeline](#architecture-review-pipeline)
  - [Prompt Optimizer](#prompt-optimizer)
  - [Refactor & Re-index Agent](#refactor--re-index-agent)
  - [Standardize Prompt Files](#standardize-prompt-files)
  - [Prompt Sanitiser](#prompt-sanitiser)
- [Usage Guide](#usage-guide)
  - [Prerequisites](#prerequisites)
  - [Using Markdown Tools (`.md`)](#using-markdown-tools-md)
  - [Using YAML Prompts (`.prompt.yaml`)](#using-yaml-prompts-promptyaml)
- [Contribution](#contribution)

---

## Why this directory exists?

This directory exists as the **"Engine Room"** for Proompts developers. While `prompts/meta/` contains user-facing tools for general meta-prompting tasks, `tools/prompt_tools/` is specifically built to maintain and elevate the quality of *this* repository itself.

It houses the instructions and scripts used by LLMs to enforce our strict YAML schema, refactor directories, and systematically optimize our core product: the prompts.

---

## Tool Descriptions

### Architecture Review Pipeline
**File:** [`01_architecture_review_pipeline.md`](./01_architecture_review_pipeline.md)

A comprehensive 7-stage pipeline designed to analyze a codebase's architecture. It includes prompts for:
1. High-Level Overview
2. Component & Dependency Mapping
3. Quality & Maintainability Assessment
4. Performance, Scalability & Security Review
5. Documentation Generation
6. Improvement Roadmap
7. Unified Architecture Review (Master Prompt)

### Prompt Optimizer
**File:** [`skills.md`](./skills.md)

A recursive meta-prompt that iteratively improves a given instruction set. It drafts a version, critiques it, rewrites it, and repeats the process until a quality score is met. This skill is consolidated within the package's skills manifest.

### Refactor & Re-index Agent
**File:** [`L5_refactor-reindex-prompts.md`](./L5_refactor-reindex-prompts.md)

An autonomous agent script ("Mission") for splitting large prompts into smaller parts and updating the documentation index. It defines operational constraints, success criteria, and a step-by-step plan for an AI agent to execute.

### Standardize Prompt Files
**File:** [`L5_standardize-prompt-files.md`](./L5_standardize-prompt-files.md)

A guide and agent persona for migrating prompt files to a standard YAML schema. It enforces consistent front-matter, header structures, and formatting conventions across the repository.

### Prompt Sanitiser
**File:** [`L5_prompt_sanitiser.md`](./L5_prompt_sanitiser.md)

A system prompt that acts as a filter to clean "raw" prompts. It removes source artifacts (footnotes, citations) and reformats the text into a clean, imperative style suitable for the repository.

---

## Usage Guide

Most tools in this directory are designed to be used with an LLM (like ChatGPT or Claude) to perform meta-tasks on the repository itself.

### Prerequisites

> [!WARNING]
> Before running any Python-based workflow scripts (like `promptops workflow`), ensure you are at the root of the repository and have installed the required dependencies:
> ```bash
> pip install -r requirements.txt
> ```

### Using Markdown Tools (`.md`)
1. Open the file (e.g., `L5_prompt_sanitiser.md`).
2. Copy the entire content.
3. Paste it into your LLM chat interface as the "System" or first "User" message.
4. Provide the target content (e.g., the raw prompt you want to sanitize) as the next message.

### Using YAML Prompts (`.prompt.yaml`)
These files follow the repository's standard schema and can be executed using the workflow engine as a standalone simulation.

**Example: Running the Prompt Optimizer**

```bash
# Provide the task variable via the -i flag
promptops workflow tools/prompt_tools/L5_prompt_optimizer.prompt.yaml -i task="Write a Python script to scrape a website"
```

**Example: Running with Verbose Output**

To see the exact inputs being passed into the prompt messages during the simulation:

```bash
promptops workflow tools/prompt_tools/L5_prompt_optimizer.prompt.yaml -i task="Draft a project brief" -v
```

---

## Contribution

### Naming Conventions

- **`L5_`**: Denotes "Level 5" or highly autonomous/meta-level tools. These are often complex instructions for agents to act on the repository itself.
- **`01_`**: Standard sequential numbering for pipelines or series.

### Adding a New Tool
1. Create a clear, descriptive filename.
2. If it's a prompt, use `.prompt.yaml`.
3. If it's a guide or agent script, use `.md`.
4. Update this `README.md` with a description.
