# System Architecture

## Overview

Proompts is a "Prompts as Code" repository. It treats prompts as software artifacts with versioning, testing, and automated documentation. This approach ensures that prompts are reproducible, testable, and maintainable, just like traditional code.

### Architecture Map

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

    subgraph "The Engine Room (promptops)"
        D1(promptops validate)
        D2(promptops workflow)
    end

    %% Flow of Validation
    C1 -->|Validated by| D1
    C2 -->|Simulated by| D2

    subgraph "Output Artifacts"
        E1["docs/<br>(Markdown site)"]
        E2[Simulation Logs]
    end

    D2 -->|Outputs| E2

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef highlight fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    class C1,C2 highlight;
```

## Core Concepts

### 1. Prompts as Code
Prompts are defined in YAML files (`.prompt.yaml`) following a strict schema. This allows for:
- **Structured Metadata**: Fields like `name`, `description`, `model`, and `parameters` provide clear context.
- **Tag Taxonomy**: Namespaced tags (for example `domain:*`, `topic:*`, `capability:*`) power discovery without relying on deep folder hierarchies.
- **Templating**: Jinja2 syntax (`{{variable}}`) enables dynamic content injection.
- **Test Data**: Embedded test cases (`testData`) with expected outputs allow for deterministic validation.
- **Evaluators**: Rules for validating model outputs (e.g., regex checks, python scripts) ensure quality.

### 2. Workflows (The Orchestrator)
Workflows chain multiple prompts together to achieve complex, multi-step goals. They are defined in `.workflow.yaml` files.
- **Steps**: Define a sequential execution of prompts.
- **State Management**: Outputs from one step can be passed as inputs to subsequent steps using `{{steps.step_id.output}}`.
- **Visualizations**: Workflow diagrams are automatically generated to visualize the flow of data.

### 3. The Simulation Engine (`promptops workflow`)
A unique feature of this repository is the ability to **simulate** workflow execution without incurring LLM costs or requiring API keys.
- **Deterministic Replay**: The engine uses the `testData` field in prompt files to mock LLM responses.
- **Validation**: This allows developers to verify variable mapping, conditional logic, and overall workflow integrity before deploying to a live model.
- **Usage**: `promptops workflow path/to/workflow.workflow.yaml`

### 4. The Validation Pipeline (`validate_prompts.sh`)
A comprehensive suite of scripts ensures repository health and consistency.
- **`promptops validate`**: Enforces strict schemas and naming conventions on prompt files, and manages modification timestamps.
- **`yamllint`**: Checks for YAML syntax errors and formatting consistency.
- **`check_broken_links.py`**: Scans documentation for broken internal links.

### 5. Documentation Generation
Documentation is treated as a first-class build artifact, automatically generated from the source code.
- **`promptops docs`**: Regenerates the main `docs/index.md` based on current prompt metadata.
- **Workflow Diagrams**: Integrated into the documentation generation process, visualizing `.workflow.yaml` files using Mermaid.js.

### 6. Hybrid CD & Release Pipeline
The repository leverages GitHub Actions to completely automate build, packaging, deployment, and container release processes.
- **SDK Package Publishing**: When a release tag (`v*`) is pushed, the `promptops` core package is built into a wheel/sdist and automatically published to PyPI using encrypted repository secrets.
- **Visual Editor (Managed PaaS)**: Merges to the `main` branch trigger continuous deployment of the Streamlit-based visual editor UI to Streamlit Cloud.
- **Protocol Server (GHCR)**: On every tagged release, a lightweight, highly optimized Docker container for the `mcp_server.py` daemon is built and published directly to the GitHub Container Registry (GHCR).
- **Quality & Safety Guardrails**: All packaging and deployment workflows are strictly dependent on pre-flight checks (`verify` tests & schemas and `vibe-audit` vibe monitors) passing completely.

## Directory Structure

- **`prompts/`**: The source of truth for all prompt definitions, with discovery driven by metadata tags rather than deep directory nesting.
- **`workflows/`**: Workflow definitions that orchestrate prompts.
- **`tools/tools/scripts/`**: The build, validation, and maintenance toolchain.
- **`docs/`**: The generated documentation site (MkDocs-ready).
