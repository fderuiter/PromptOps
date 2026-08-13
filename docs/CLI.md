# PromptOps CLI Reference

This document is auto-generated from the CLI definition. Do not edit manually.

## `promptops`

```text
usage: promptops [-h]
                 {init,verify,verify-audit,validate,simulate,docs,agent,vibe,workflow,search,export-schemas,generate-cli-docs}
                 ...

PromptOps Toolkit CLI

positional arguments:
  {init,verify,verify-audit,validate,simulate,docs,agent,vibe,workflow,search,export-schemas,generate-cli-docs}
    init                Initialize PromptOps in the current repository
    verify              Run the central verification script locally
    verify-audit        Verify cryptographically signed audit trails in
                        corporate workspace folders
    validate            Validate prompt files
    simulate            Simulate a prompt
    docs                Generate prompt documentation
    agent               Agent configuration and discovery
    vibe                Run full-fidelity vibe audit
    workflow            Simulate a workflow execution
    search              Search prompts by keyword
    export-schemas      Export JSON schemas for core validation models
    generate-cli-docs   Generate CLI documentation markdown

options:
  -h, --help            show this help message and exit

```

### `promptops init`

```text
usage: promptops init [-h]

options:
  -h, --help  show this help message and exit

```

### `promptops verify`

```text
usage: promptops verify [-h]

options:
  -h, --help  show this help message and exit

```

### `promptops verify-audit`

```text
usage: promptops verify-audit [-h] [--dir DIR]

options:
  -h, --help  show this help message and exit
  --dir DIR   Directory containing signed audit trails

```

### `promptops validate`

```text
usage: promptops validate [-h] [--dir DIR] [--strict] [--skip-semantic]
                          [files ...]

positional arguments:
  files            Specific files to validate and format (updates
                   last_modified)

options:
  -h, --help       show this help message and exit
  --dir DIR        Directory containing prompts
  --strict         Enable strict validation
  --skip-semantic  Skip semantic validation checks

```

### `promptops simulate`

```text
usage: promptops simulate [-h] [-f FILE_FLAG] -i DATA [--strict] [--chaos]
                          [-v] [--json] [--no-color]
                          [file]

positional arguments:
  file                  Path to prompt file

options:
  -h, --help            show this help message and exit
  -f FILE_FLAG, --file FILE_FLAG
                        Path to prompt file (alias)
  -i DATA, --data DATA  Path to JSON/YAML file with mock data
  --strict              Enable strict validation
  --chaos               Enable chaos mode
  -v, --verbose         Increase verbosity
  --json                Enable JSON output mode
  --no-color            Disable colored output

```

### `promptops docs`

```text
usage: promptops docs [-h] [--dir DIR] [--out OUT] [--repo-url REPO_URL]
                      [--branch BRANCH] [--check]

options:
  -h, --help           show this help message and exit
  --dir DIR            Directory containing prompts
  --out OUT            Output directory for documentation
  --repo-url REPO_URL  Base URL for source repository
  --branch BRANCH      Branch name for source repository links
  --check              Check for documentation drift without modifying files

```

### `promptops agent`

```text
usage: promptops agent [-h] {config,discovery} ...

positional arguments:
  {config,discovery}
    config            Generate MCP configuration for agent clients
    discovery         Show tool discovery and override report

options:
  -h, --help          show this help message and exit

```

#### `promptops agent config`

```text
usage: promptops agent config [-h] [--dir DIR]

options:
  -h, --help  show this help message and exit
  --dir DIR   Directory containing prompts

```

#### `promptops agent discovery`

```text
usage: promptops agent discovery [-h] [--dir DIR]

options:
  -h, --help  show this help message and exit
  --dir DIR   Directory containing prompts

```

### `promptops vibe`

```text
usage: promptops vibe [-h] [--budget-cap BUDGET_CAP] [--coverage COVERAGE]

options:
  -h, --help            show this help message and exit
  --budget-cap BUDGET_CAP
                        Maximum budget for LLM API calls
  --coverage COVERAGE   Coverage mode

```

### `promptops workflow`

```text
usage: promptops workflow [-h] [-i INPUT] [-f INPUTS_FILE] [-v] [--strict]
                          [--chaos] [--no-color] [--json]
                          workflow_file

positional arguments:
  workflow_file         Path to the .workflow.yaml file.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Set a workflow input, e.g., -i name='value'
  -f INPUTS_FILE, --inputs-file INPUTS_FILE
                        Path to a JSON or YAML file containing workflow inputs
  -v, --verbose         Increase output verbosity
  --strict              Run in strict mode
  --chaos               Enable Chaos Mode
  --no-color            Disable color output
  --json                Output Fidelity Report as JSON only

```

### `promptops search`

```text
usage: promptops search [-h] [-v] query

positional arguments:
  query          Keyword to search for

options:
  -h, --help     show this help message and exit
  -v, --verbose  Show description

```

### `promptops export-schemas`

```text
usage: promptops export-schemas [-h] [--out-dir OUT_DIR]

options:
  -h, --help         show this help message and exit
  --out-dir OUT_DIR  Output directory for JSON schemas

```
