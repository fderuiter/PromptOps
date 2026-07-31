# Domain Agent Skills: Technical Software engineering Lifecycle Agentic coding workflow

## Metadata
- **Domain Namespace:** technical.software_engineering.lifecycle.agentic_coding_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Project Brief for Epic
<!-- VALIDATION_METADATA: {"variables": [{"name": "business_rules", "description": "domain logic", "required": true}, {"name": "data_models", "description": "entities and types", "required": true}, {"name": "key_features", "description": "features or milestones", "required": true}, {"name": "project_description", "description": "summary of the epic", "required": true}, {"name": "success_metrics", "description": "measurements of success", "required": true}], "metadata": {}} -->
### Description
Summarize a project epic with key features, rules, and success metrics.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `business_rules` | String | domain logic | Yes |
| `data_models` | String | entities and types | Yes |
| `key_features` | String | features or milestones | Yes |
| `project_description` | String | summary of the epic | Yes |
| `success_metrics` | String | measurements of success | Yes |


### Core Instructions
```text
[SYSTEM]
Use this brief to capture the high-level scope of a significant project milestone or epic.

Keep each list concise and focused on actionable information.

[USER]
1. Describe the overall project goal.
1. List key features or milestones to achieve.
1. Outline important data models and entities.
1. Specify critical business rules or logic.
1. Define success metrics for performance or engagement.
1. Add any additional technical details or constraints.
Inputs:
- `{{ project_description }}` – summary of the epic
- `{{ key_features }}` – features or milestones
- `{{ data_models }}` – entities and types
- `{{ business_rules }}` – domain logic
- `{{ success_metrics }}` – measurements of success
Output format:
Markdown sections titled **Project Description**, **Key Features**, **Technical Entities & Data Models**, **Business Rules & Logic**, **Success Metrics**, and **Additional Implementation Details**.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['Markdown sections titled **Project Description**, **Key Features**, **Technical Entities & Data Models**, **Business Rules & Logic**, **Success Metrics**, and **Additional Implementation Details**.']
```

---

## Skill: Product Brief Template
<!-- VALIDATION_METADATA: {"variables": [{"name": "architecture", "description": "overview of proposed architecture", "required": true}, {"name": "context_notes", "description": "constraints or risks", "required": true}, {"name": "features", "description": "feature list organised by phase", "required": true}, {"name": "vision", "description": "short statement of the desired end state", "required": true}], "metadata": {}} -->
### Description
Outline the high-level vision, features, and architecture for a new software project.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `architecture` | String | overview of proposed architecture | Yes |
| `context_notes` | String | constraints or risks | Yes |
| `features` | String | feature list organised by phase | Yes |
| `vision` | String | short statement of the desired end state | Yes |


### Core Instructions
```text
[SYSTEM]
Use this brief when kicking off a new application or clarifying scope with collaborators.

This template helps align teams before development begins.

[USER]
1. Describe the overall product vision.
1. List key features with associated phases or milestones.
1. Summarize the chosen architectural style and component interactions.
1. Capture additional context, constraints, or stakeholder expectations.
Inputs:
- `{{ vision }}` – short statement of the desired end state
- `{{ features }}` – feature list organised by phase
- `{{ architecture }}` – overview of proposed architecture
- `{{ context_notes }}` – constraints or risks
Output format:
Markdown sections titled **Vision**, **Key Features and Roadmap**, **Overall Architecture**, and **Additional Context**.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['Markdown sections titled **Vision**, **Key Features and Roadmap**, **Overall Architecture**, and **Additional Context**.']
```
