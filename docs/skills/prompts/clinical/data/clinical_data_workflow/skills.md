# Domain Agent Skills: Clinical Data Clinical data workflow

## Metadata
- **Domain Namespace:** clinical.data.clinical_data_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Draft a Data Management Plan Section
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Act as a Clinical Data Management subject-matter expert.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
**Objective**: Draft the "Data Validation & Cleaning" section for the DMP of a global, randomized, double-blind Phase II study (Protocol YY456) using Medidata Rave.

[USER]
{{ input }}
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
['Data Validation & Cleaning includes automated edit checks in Medidata Rave to flag out-of-range lab values.']
```

---

## Skill: Discrepancy Detection & Query Log Generator
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}, {"name": "csv", "description": "Auto-extracted variable csv", "required": false}], "metadata": {}} -->
### Description
Examine a CSV dataset to detect discrepancies and generate a query log.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |
| `csv` | String | Auto-extracted variable csv | No |


### Core Instructions
```text
[SYSTEM]
You are a Senior Clinical Data Specialist at a top CRO for a Phase III oncology trial (Protocol XX123).
**Task**: Examine the de-identified CSV dataset enclosed in the `<csv>` XML tags.
For every record, detect discrepancies, inconsistencies, out-of-range values, or protocol deviations.

1. Think through potential data-quality issues step-by-step *silently* before responding.
2. Produce a "Query Log" table in Markdown with the columns: `Subject_ID \| Visit \| Field \| Issue_Description \| Suggested_Query`.
3. Limit output to a maximum of 25 highest-priority issues.
4. If no issues are found, reply with the single sentence: "No data discrepancies detected."
Output format: Markdown table

[USER]
<csv>
{{ input }}
</csv>
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
['No data discrepancies detected.']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['| 003 | Baseline | Age |']
```

---

## Skill: Edit-Check Specification Builder for New eCRF Fields
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Create edit-check specifications for the new Concomitant Medication module in Medidata Rave.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Data Specialist configuring Medidata Rave.  
**Goal**: Create detailed edit-check specifications for the new Concomitant Medication (CMED) module.

[USER]
{{ input }}
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
['IF CMENDTC < CMSTDTC THEN raise query ']
```
