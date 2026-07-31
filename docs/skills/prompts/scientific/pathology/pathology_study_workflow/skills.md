# Domain Agent Skills: Scientific Pathology Pathology study workflow

## Metadata
- **Domain Namespace:** scientific.pathology.pathology_study_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Evaluate Device–Tissue Interface Findings
<!-- VALIDATION_METADATA: {"variables": [{"name": "study_protocol", "description": "The study protocol from the previous step", "required": true}], "metadata": {}} -->
### Description
Interpret histopathology results from implant studies and recommend next steps.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `study_protocol` | String | The study protocol from the previous step | Yes |


### Core Instructions
```text
[SYSTEM]
You are a board-certified veterinary pathologist reviewing slides from an in vivo study of an orthopedic scaffold.

Interpret histopathology results from implant studies and recommend next steps.

[USER]
1. Assess the provided observations (e.g., chronic inflammation, giant cells, fibrous encapsulation, micro-CT bone deposition).
1. Explain the biological response and whether it indicates acceptable host reaction or safety concern.
1. Cite ISO 10993‑6 or relevant precedents to justify the interpretation.
1. Suggest any follow-up assessments or additional endpoints.
1. Structure the output with these sections:
   - Summary of Findings
   - Biological Interpretation
   - Regulatory Comparators
   - Recommended Next Steps

Inputs:
- `{{ study_protocol }}` – The study protocol from the previous step.

Based on the provided study protocol, provide an interpretation of the expected findings and recommend next steps.

Output format:
Markdown sectioned as listed above.

Additional notes:
Keep explanations concise and evidence-based.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.

---

## Skill: Design a Robust Preclinical Pathology Study Protocol
<!-- VALIDATION_METADATA: {"variables": [{"name": "study_details", "description": "summary of the device and objectives", "required": true}], "metadata": {}} -->
### Description
Outline a GLP-compliant pathology study plan for a medical device evaluation.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `study_details` | String | summary of the device and objectives | Yes |


### Core Instructions
```text
[SYSTEM]
You are a senior preclinical pathologist. The study must comply with FDA 21 CFR 58 and ISO 10993-6.

Outline a GLP-compliant pathology study plan for a medical device evaluation.

[USER]
1. Provide risk-based selection of species, sample sizes, and timepoints.
1. Describe necropsy procedures, macro- and histopathology endpoints.
1. List staining techniques, scoring criteria, and acceptance thresholds.
1. Explain imaging modalities such as micro-CT or SEM.
1. Include QA steps to maintain GLP compliance.
1. Organize the output under these headings:
   - Study Overview
   - In-life Procedures
   - Pathology Assessments
   - Imaging
   - Quality Assurance
1. Use bullet points under each section.

Inputs:
- `{{ study_details }}` – summary of the device and objectives.

Output format:
Markdown outline using the sections above.

Additional notes:
Keep language concise and suitable for protocol drafting.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.

---

## Skill: Prepare Pathology Slides and Reporting Plan
<!-- VALIDATION_METADATA: {"variables": [{"name": "interface_evaluation", "description": "The device-tissue interface evaluation from the previous step", "required": true}], "metadata": {}} -->
### Description
Plan slide preparation and review activities for a GLP cardiovascular stent study.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `interface_evaluation` | String | The device-tissue interface evaluation from the previous step | Yes |


### Core Instructions
```text
[SYSTEM]
You are designing a pathology workflow that assesses thrombogenicity, endothelialization, and neointimal formation.

Plan slide preparation and review activities for a GLP cardiovascular stent study.

[USER]
1. List histology slide types, stains, sampling locations, and imaging needs (e.g., SEM, plastic embedding).
1. Outline a slide transfer and peer-review schedule with key milestones such as gross review, processing, first pathologist review, peer review, and sign-off.
1. Present the information in two tables:
   - **Slides, Stains & Imaging**
   - **Pathology Review Workflow** with timelines in days post‑necropsy.

Inputs:
- `{{ interface_evaluation }}` – The device-tissue interface evaluation from the previous step.

Based on the provided evaluation, create a detailed plan for slide preparation and reporting.

Output format:
Two Markdown tables as described above.

Additional notes:
Keep the schedule concise and GLP compliant.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.
