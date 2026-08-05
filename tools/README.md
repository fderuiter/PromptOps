# 🛠️ Tools & Utilities

> [!NOTE]
> This directory is the "Engine Room" of the repository. It contains both traditional software scripts and AI-native prompt tools.

## 🗺️ Directory Map

| Directory | Type | Purpose |
| :--- | :--- | :--- |
| **[`scripts/`](tools/scripts/README.md)** | 🐍 Python | **Automation & Validation.** Executable code for CI/CD, linting, doc generation, and testing. <br> *Key tool: `validate_prompts.sh`* |
| **[`prompt_tools/`](tools/prompt_tools/README.md)** | 🧠 Prompts | **Meta-Prompting.** LLM-based tools for refining, sanitizing, and architecting other prompts. <br> *Key tool: `L5_prompt_optimizer`* |

## 🚀 Quick Start

### 1. Validate the Repository
Before submitting any changes, run the master validation script:

```bash
# Runs linting, schema checks, and link verification
./scripts/validate_prompts.sh
```

### 2. Optimize a Prompt
Use the **Prompt Optimizer** to improve your prompt's quality:

1. Copy content from [`tools/tools/prompt_tools/L5_prompt_optimizer.prompt.yaml`](tools/prompt_tools/L5_prompt_optimizer.prompt.yaml).
2. Paste into your LLM along with your draft prompt.

## 📚 Detailed Documentation

- **[Developer Scripts (Python)](tools/scripts/README.md)**: Full API reference for utility scripts like broken link checker, overview generator, etc.
- **[Prompt Engineering Tools](tools/prompt_tools/README.md)**: Guide for using the meta-prompts to maintain the repo.
