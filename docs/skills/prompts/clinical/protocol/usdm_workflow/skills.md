# Domain Agent Skills: Clinical Protocol Usdm workflow

## Metadata
- **Domain Namespace:** clinical.protocol.usdm_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Protocol to USDM Stage 5 - Assembly
<!-- VALIDATION_METADATA: {"variables": [{"name": "metadata_json", "description": "Output from Stage 1.", "required": true}, {"name": "rationale_json", "description": "Output from Stage 2.", "required": true}, {"name": "workflow_json", "description": "Output from Stage 3.", "required": true}, {"name": "concepts_json", "description": "Output from Stage 4.", "required": true}], "metadata": {}} -->
### Description
Assemble the final USDM JSON from previous stages.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `metadata_json` | String | Output from Stage 1. | Yes |
| `rationale_json` | String | Output from Stage 2. | Yes |
| `workflow_json` | String | Output from Stage 3. | Yes |
| `concepts_json` | String | Output from Stage 4. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a JSON Systems Integrator.

# Task
Merge these four JSON snippets into a single, valid CDISC USDM v3.0 JSON object.
- Place `study_meta` at the root.
- Place `criteria` under the `study.criteria` array.
- Construct the `workflow` section using the `encounters`, `activities`, and `workflow_matrix`.
- Ensure all ID references (e.g., `activityId` inside `workflow`) remain consistent.

# Output Requirement
Produce **only** the final JSON object. Do not add conversational text.

[USER]
# Inputs
1. Metadata:
<metadata_json>
{{ metadata_json }}
</metadata_json>

2. Rationale:
<rationale_json>
{{ rationale_json }}
</rationale_json>

3. Workflow:
<workflow_json>
{{ workflow_json }}
</workflow_json>

4. Concepts:
<concepts_json>
{{ concepts_json }}
</concepts_json>
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
['{\n  ']
```

---

## Skill: Protocol to USDM Stage 1 - Metadata
<!-- VALIDATION_METADATA: {"variables": [{"name": "protocol_text", "description": "The full text or synopsis of the protocol.", "required": true}], "metadata": {}} -->
### Description
Extract Study Level Metadata and Design from Protocol.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `protocol_text` | String | The full text or synopsis of the protocol. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Data Architect.

# Task
Analyze the text to extract Study Level Metadata and Study Design.
1. Identify the Protocol Title, ID, Phase, and Medical Condition.
2. Identify the Study Design (e.g., Parallel, Crossover).
3. Identify all Study Arms (e.g., Placebo, Experimental 10mg).

# Output Requirement
Return a JSON snippet with the following structure. **Assign a unique ID (e.g., ARM_01) to each Arm.**

{
  "study_meta": {
    "title": "String",
    "id": "String",
    "phase": "String",
    "condition": "String"
  },
  "study_design": {
    "type": "String",
    "arms": [
      { "id": "ARM_XX", "name": "String", "description": "String", "type": "String" }
    ]
  }
}

[USER]
# Input
<protocol_text>
{{ protocol_text }}
</protocol_text>
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
['{\n  ']
```

---

## Skill: Protocol to USDM Stage 2 - Rationale
<!-- VALIDATION_METADATA: {"variables": [{"name": "protocol_objectives_text", "description": "The Objectives, Endpoints, and Eligibility sections of the protocol.", "required": true}], "metadata": {}} -->
### Description
Extract Objectives, Endpoints, and Eligibility Criteria.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `protocol_objectives_text` | String | The Objectives, Endpoints, and Eligibility sections of the protocol. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Research Associate.

# Task
1. Extract Primary and Secondary Objectives.
2. Extract the specific Endpoint associated with each Objective.
3. Extract Inclusion and Exclusion criteria.

# Output Requirement
Return a JSON snippet. **Link Endpoints to their parent Objective using `objectiveId`.**

{
  "objectives": [
    { "id": "OBJ_01", "level": "Primary", "description": "String" }
  ],
  "endpoints": [
    { "id": "END_01", "objectiveId": "OBJ_01", "description": "String" }
  ],
  "criteria": [
    { "id": "CRI_01", "type": "Inclusion", "text": "String" },
    { "id": "CRI_02", "type": "Exclusion", "text": "String" }
  ]
}

[USER]
# Input
<protocol_objectives_text>
{{ protocol_objectives_text }}
</protocol_objectives_text>
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
['{\n  ']
```

---

## Skill: Protocol to USDM Stage 3 - Workflow
<!-- VALIDATION_METADATA: {"variables": [{"name": "protocol_soa_text", "description": "The Schedule of Activities table or text.", "required": true}], "metadata": {}} -->
### Description
Extract Encounters and Activities from Schedule of Activities.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `protocol_soa_text` | String | The Schedule of Activities table or text. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a CDISC Standards Specialist.

# Task
Deconstruct the Schedule of Activities into two lists: `Encounters` (Visits) and `Activities` (Procedures).
1. **Encounters:** List every unique visit/time-point. Assign a unique ID (e.g., ENC_01). Note the timing (e.g., "Day 1").
2. **Activities:** List every unique procedure (e.g., "Informed Consent", "Vital Signs"). Assign a unique ID (e.g., ACT_01).
3. **Matrix:** Create a mapping list that shows which `activityId` happens at which `encounterId`.

# Output Requirement
Return a JSON snippet:

{
  "encounters": [
    { "id": "ENC_01", "name": "Screening", "timing": "-28 Days" }
  ],
  "activities": [
    { "id": "ACT_01", "name": "Informed Consent" },
    { "id": "ACT_02", "name": "Vital Signs" }
  ],
  "workflow_matrix": [
    { "encounterId": "ENC_01", "activityIds": ["ACT_01", "ACT_02"] }
  ]
}

[USER]
# Input
<protocol_soa_text>
{{ protocol_soa_text }}
</protocol_soa_text>
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
['{\n  ']
```

---

## Skill: Protocol to USDM Stage 4 - Concepts
<!-- VALIDATION_METADATA: {"variables": [{"name": "activities_json", "description": "The JSON list of Activities from Stage 3.", "required": true}], "metadata": {}} -->
### Description
Map Activities to Biomedical Concepts.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `activities_json` | String | The JSON list of Activities from Stage 3. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Data Standards Mapper.

# Task
For each Activity identified in the input:
1. Determine the appropriate Biomedical Concept (BC).
2. If the activity is a composite (e.g., "Vitals"), break it down into its components (Systolic BP, Diastolic BP, Heart Rate).
3. Assign a `bcId` to each.

# Output Requirement
Return a JSON snippet linking Activity IDs to Biomedical Concept definitions:

{
  "biomedicalConcepts": [
    {
      "activityId": "ACT_02",
      "conceptName": "Systolic Blood Pressure",
      "ncitCode": "C25298" // Optional: If you can infer NCI Thesaurus codes
    }
  ]
}

[USER]
# Input
<activities_json>
{{ activities_json }}
</activities_json>
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
['{\n  ']
```
