# Domain Agent Skills: Clinical Data management Data management etl workflow

## Metadata
- **Domain Namespace:** clinical.data_management.data_management_etl_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Clinical ETL Pipeline Review
<!-- VALIDATION_METADATA: {"variables": [{"name": "etl_qc_plan", "description": "The etl qc plan to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Review the clinical ETL pipeline for accuracy and efficiency.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `etl_qc_plan` | String | The etl qc plan to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a reviewer auditing clinical ETL pipelines for accuracy and
efficiency.

[USER]
Here is the ETL Quality Check plan:
{{ etl_qc_plan }}

Based on this QC plan, and the implied mapping specification, review the entire clinical ETL pipeline for accuracy, efficiency, and potential bottlenecks.
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
['Identifies slow transformations and load issues.']
```

---

## Skill: Clinical ETL Mapping Spec
<!-- VALIDATION_METADATA: {"variables": [{"name": "etl_requirements", "description": "The requirements or specifications", "required": true}], "metadata": {}} -->
### Description
Create an ETL mapping specification for clinical data.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `etl_requirements` | String | The requirements or specifications | Yes |


### Core Instructions
```text
[SYSTEM]
You are an ETL specialist defining mapping specifications for clinical trial
data pipelines.

[USER]
Here are the requirements for the ETL process:
{{ etl_requirements }}

Based on these requirements, create a detailed ETL mapping specification.
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
['Includes field-to-field mappings.']
```

---

## Skill: Clinical ETL Transformation QC
<!-- VALIDATION_METADATA: {"variables": [{"name": "etl_mapping_spec", "description": "The etl mapping spec to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Define quality checks for clinical ETL transformations.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `etl_mapping_spec` | String | The etl mapping spec to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a quality engineer establishing validation checks for clinical ETL
transformations.

[USER]
Here is the ETL mapping specification:
{{ etl_mapping_spec }}

Based on this specification, define a comprehensive set of quality checks for the clinical ETL transformations.
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
['Mentions range validations and format consistency.']
```
