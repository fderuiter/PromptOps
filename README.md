# proompts

[![Deploy MkDocs site](https://github.com/fderuiter/proompts/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/fderuiter/proompts/actions/workflows/deploy-pages.yml)
[![YAML Validation](https://github.com/fderuiter/proompts/actions/workflows/yaml-validation.yml/badge.svg)](https://github.com/fderuiter/proompts/actions/workflows/yaml-validation.yml)
[![Repository Checks](https://github.com/fderuiter/proompts/actions/workflows/repo-checks.yml/badge.svg)](https://github.com/fderuiter/proompts/actions/workflows/repo-checks.yml)

A curated set of prompts in YAML for AI-assisted product development, regulatory workflows, and general operations. Prompts are organized by topic: ranging from code reviews to market research. You can mix and match them in your own agentic workflows!

## 🗺️ Directory Map

| Path | Description | Key Contents |
| :--- | :--- | :--- |
| **[`prompts/`](prompts/)** | **The Core Library.** <br> YAML-based prompts organized by domain. | `business/`, `clinical/`, `technical/` |
| **[`workflows/`](workflows/)** | **Chained Sequences.** <br> Multi-step prompt chains for complex tasks. | `technical/software_engineering/paw_workflow.workflow.yaml` |
| **[`tools/`](tools/README.md)** | **The Engine Room.** <br> Utilities for maintenance and development. | [`scripts/`](tools/tools/scripts/README.md) (Python), [`prompt_tools/`](tools/tools/prompt_tools/README.md) (Meta-prompts) |
| **[`scripts/`](scripts/)** | **Shell Wrappers.** <br> Convenience scripts for common tasks. | `validate_prompts.sh` |
| **[`docs/`](docs/)** | **Knowledge Base.** <br> Guides, usage instructions, and generated docs. | `USAGE.md`, `BEST_PRACTICES.md` |



### System Architecture

```mermaid
graph TD
    %% Define Nodes
    A[Developers / Contributors] -->|Commit Changes| B(GitHub Repository)

    subgraph "Core Data"
        C1["prompts/<br>(.prompt.yaml)"]
        C2["workflows/<br>(.workflow.yaml)"]
        C1 -.->|Chained by| C2
    end
    B -->|Contains| C1
    B -->|Contains| C2

    subgraph "The Engine Room (scripts/)"
        D1(validate_prompts.sh)
    end

    %% Flow of Validation
    C1 -->|Validated by| D1
    C2 -->|Validated by| D1

    subgraph "Output Artifacts"
        E1["docs/<br>(Markdown site)"]
    end

    D1 -->|Builds| E1

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef highlight fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class C1,C2 highlight;
```

## Integrations

- **[Model Context Protocol (MCP)](docs/mcp_integration.md)** – Learn how to expose the local prompt library as tools for Claude Desktop and other MCP-compatible AI agents.

## Docs

- **[🚀 Quickstart: 5-Minute Onboarding](docs/QUICKSTART.md)** – Start here! Learn how to run your first simulation.
- **[Full Table of Contents](docs/overview.md)** – Browse all prompts by category
- **[Usage Guide](docs/USAGE.md)** – Learn how to use and integrate prompts
- **[Developer Scripts](tools/tools/scripts/README.md)** – Tools for validating and maintaining the repo
- **[IDE JSON Schemas](docs/schemas/README.md)** – Configure your IDE for prompt and workflow validation

## Setup

To run validation scripts and tools locally, you need Python 3 and the required dependencies.

1.  Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the validation script to verify everything is set up correctly:
    ```bash
    ./scripts/validate_prompts.sh
    ```

## Prompt Schema

Prompts are stored as `.prompt.yaml` or `.prompt.yml` files. Each prompt file
contains two sections:

- **Runtime information** – ordered `messages` with `role`/`content` pairs that
  form the actual prompt. Use `{{variable}}` placeholders for user-provided
  values.
- **Development information** – optional metadata that describes the prompt and
  how to test it.

Top-level fields available in a prompt file include:

- `name` – short human-readable title
- `description` – concise summary of what the prompt does
- `model` – model identifier
- `modelParameters` – optional model parameters such as `temperature`
- `messages` – list of system and user messages
- `testData` – example inputs with their expected outputs
- `evaluators` – rules for verifying model responses

See `docs/template_prompt.prompt.md` for a filled-out Markdown example, and `docs/schemas/prompt.schema.json` for the strict JSON schema definitions.

## Prompt Workflows

In addition to individual prompts, this repository supports **Prompt Workflows**,
which chain multiple prompts together to perform complex, multi-step tasks.
Workflows are defined in `.workflow.yaml` files and call prompts located in dedicated
workflow subfolders (e.g., `prompts/clinical/protocol/protocol_workflow/`).
included runner script.

To learn more, see the [Prompt Workflows Documentation](docs/workflow_guide.md).

## Validation

To run all validation checks (YAML linting, schema validation, documentation index verification) locally, use the provided script:

```bash
./scripts/validate_prompts.sh
```

This script runs the following checks:
- `promptops validate`: Enforces strict schemas, naming conventions, and updates modification timestamps.
- `yamllint`: Lints YAML syntax and formatting.
- `pytest`: Runs the Python unit test suite.
- `ruff`: Checks Python script styles and boundaries.
- `check_broken_links`: Scans for broken internal links in documentation.
- Doc drift, dead code, and snippet simulation checks.

It is recommended to run this script before committing changes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on how to contribute.

1. Create prompts as `.prompt.yaml` or `.prompt.md` files that follow [`docs/schemas/prompt.schema.json`](docs/schemas/prompt.schema.json) and place them in the appropriate folder.
2. Review the [Best Practices Guide](docs/BEST_PRACTICES.md) for detailed guidance on creating high-quality prompts.
3. Ensure your prompt includes:
   - Meaningful `testData` with realistic examples (at least 1-2 test cases)
   - `evaluators` to validate output quality
   - Clear instructions and expected output format
4. Before committing, run validation:
   ```bash
   ./scripts/validate_prompts.sh
   ```
5. If you create a new directory, an `overview.md` will be generated automatically by the workflow.

The same validation runs in CI, but running checks locally helps catch issues early.

## License

This project is licensed under the [Proompts Personal Use License](LICENSE.md).
Individuals may freely use, modify, and distribute the prompts for personal,
non-commercial purposes. Commercial entities must obtain written permission
from Frederick de Ruiter before using the material.
