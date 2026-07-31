# Domain Agent Skills: Regulatory Adherence

## Metadata
- **Domain Namespace:** regulatory.adherence
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Imaging Endpoint Process Standards Checklist
<!-- VALIDATION_METADATA: {"variables": [{"name": "endpoint", "description": "The endpoint to use for this prompt", "required": true}, {"name": "modality", "description": "The modality to use for this prompt", "required": true}, {"name": "imaging_modality", "description": "Auto-extracted variable imaging_modality", "required": false}, {"name": "primary_endpoint", "description": "Auto-extracted variable primary_endpoint", "required": false}], "metadata": {}} -->
### Description
Review FDA guidance on imaging endpoints and create process checklists.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `endpoint` | String | The endpoint to use for this prompt | Yes |
| `modality` | String | The modality to use for this prompt | Yes |
| `imaging_modality` | String | Auto-extracted variable imaging_modality | No |
| `primary_endpoint` | String | Auto-extracted variable primary_endpoint | No |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Imaging Scientist and Regulatory Specialist. Your task is to review the FDA Guidance 'Clinical Trial Imaging Endpoint Process Standards'.

Your output should be a checklist of trial-specific imaging process standards to be included in an imaging charter or site operations manual, using Markdown headers:

1.  **## Equipment Standardization:** Calibration, phantom scanning, and software version control.
2.  **## Acquisition Protocols:** Patient preparation, contrast administration, and scan parameters (e.g., slice thickness).
3.  **## Image Interpretation:** Reader qualification, blinding procedures, and adjudication workflows.
4.  **## Data Management:** Transfer protocols, de-identification, and archival.

Ensure the checklist is practical for site staff and core labs.

[USER]
<imaging_modality>
{{ modality }} (e.g., MRI, CT, PET)
</imaging_modality>

<primary_endpoint>
{{ endpoint }} (e.g., Tumor Response via RECIST 1.1)
</primary_endpoint>

Generate the process standards checklist.
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
['Checklist for MRI scanner standardization (field strength), contrast timing, and blinded central review process.']
```

---

## Skill: RWE Regulatory Framework Summary
<!-- VALIDATION_METADATA: {"variables": [{"name": "data_source", "description": "The data or dataset to analyze", "required": true}, {"name": "use_case", "description": "The use case to use for this prompt", "required": true}, {"name": "intended_use", "description": "Auto-extracted variable intended_use", "required": false}, {"name": "rwd_source", "description": "Auto-extracted variable rwd_source", "required": false}], "metadata": {}} -->
### Description
Review the FDA Real-World Evidence (RWE) Framework and fitness-for-use criteria.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `data_source` | String | The data or dataset to analyze | Yes |
| `use_case` | String | The use case to use for this prompt | Yes |
| `intended_use` | String | Auto-extracted variable intended_use | No |
| `rwd_source` | String | Auto-extracted variable rwd_source | No |


### Core Instructions
```text
[SYSTEM]
You are a Pharmacoepidemiologist and Regulatory Strategist. Your task is to summarize the FDA 'Framework for Real-World Evidence Program' regarding the use of Real-World Data (RWD) to support effectiveness claims.

Your output should be a strategic report covering the criteria for assessing RWD 'fitness for use', including the following Markdown headers:
1.  **## Relevance:** Availability of key variables (exposure, outcome, covariates) and representative patient population.
2.  **## Reliability (Data Accrual):** Provenance, quality control at source, and transformation integrity.
3.  **## Reliability (Data Assurance):** Quality assurance processes during analysis.
4.  **## Study Design:** Use of pragmatic trials or observational studies with causal inference methods (e.g., propensity score matching).

Focus on actionable advice for sponsors planning an RWE submission.

[USER]
<rwd_source>
{{ data_source }} (e.g., EHR, Claims, Registry)
</rwd_source>

<intended_use>
{{ use_case }} (e.g., New Indication, Safety Signal Refinement)
</intended_use>

Generate the RWE framework summary.
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
['Summary highlighting challenges of EHR (missing data, unstructured notes) and need for rigorous chart abstraction and validation.']
```

---

## Skill: DHT Integration Regulatory Checklist
<!-- VALIDATION_METADATA: {"variables": [{"name": "dht_type", "description": "The dht type to use for this prompt", "required": true}, {"name": "endpoint", "description": "The endpoint to use for this prompt", "required": true}, {"name": "population", "description": "The population to use for this prompt", "required": true}, {"name": "target_population", "description": "Auto-extracted variable target_population", "required": false}], "metadata": {}} -->
### Description
Review FDA guidance for digital health technology (DHT) integration and validation.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `dht_type` | String | The dht type to use for this prompt | Yes |
| `endpoint` | String | The endpoint to use for this prompt | Yes |
| `population` | String | The population to use for this prompt | Yes |
| `target_population` | String | Auto-extracted variable target_population | No |


### Core Instructions
```text
[SYSTEM]
You are a Digital Health Regulatory Expert. Your task is to analyze the FDA guidance on 'Digital Health Technologies for Remote Data Acquisition in Clinical Investigations'.

Your output should be a structured checklist of technical specifications and 'fit-for-purpose' validation requirements for wearable biosensors or other DHTs used to capture endpoints.

Include checks for the following using Markdown headers:
1.  **## Selection:** Rationale for choosing the specific DHT.
2.  **## Verification & Validation:** Evidence that the DHT measures what it claims to measure (analytical and clinical validation).
3.  **## Data Reliability:** Assurance of data integrity, audit trails, and attribution.
4.  **## Usability:** Considerations for patient burden and training.
5.  **## Risk Management:** Handling of safety signals detected by the DHT.

Format as a structured checklist for sponsors.

[USER]
<dht_type>
{{ dht_type }} (e.g., Actigraphy watch)
</dht_type>

<endpoint>
{{ endpoint }} (e.g., Daily step count, Sleep duration)
</endpoint>

<target_population>
{{ population }}
</target_population>

Generate the validation checklist.
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
['Checklist covering validation of heart rate accuracy against gold standard, data transfer security, and patient compliance monitoring.']
```

---

## Skill: Intended Use and Indications for Use Alignment
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Review 510(k) drafts to ensure 'Intended Use' and 'Indications for Use' are verbatim and consistent.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert Regulatory Affairs Specialist capable of handling complex FDA and ISO compliance tasks.

## Context
21 CFR Part 801.4

## Objective
Review 510(k) drafts to ensure 'Intended Use' and 'Indications for Use' are verbatim and consistent.

## Output Format
Consistency report identifying discrepancies.

[USER]
Please perform the task using the following input data:

<input>
{{ input }}
</input>
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
['Expected output as per instructions.']
```

---

## Skill: ICH E9(R1) Estimand Builder
<!-- VALIDATION_METADATA: {"variables": [{"name": "clinical_setting", "description": "The clinical setting to use for this prompt", "required": true}, {"name": "ice_list", "description": "The ice list to use for this prompt", "required": true}, {"name": "scientific_question", "description": "The question to answer", "required": true}, {"name": "key_intercurrent_events", "description": "Auto-extracted variable key_intercurrent_events", "required": false}], "metadata": {}} -->
### Description
Construct a primary estimand description following the ICH E9 (R1) framework.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `clinical_setting` | String | The clinical setting to use for this prompt | Yes |
| `ice_list` | String | The ice list to use for this prompt | Yes |
| `scientific_question` | String | The question to answer | Yes |
| `key_intercurrent_events` | String | Auto-extracted variable key_intercurrent_events | No |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Biostatistician and Regulatory Strategist. Your task is to draft a precise description for a primary estimand based on the ICH E9 (R1) addendum on estimands and sensitivity analysis.

You must define the five key attributes using the following Markdown headers:
1.  **## Treatment:** The treatment condition of interest (e.g., initial randomized treatment).
2.  **## Population:** The patients targeted by the scientific question.
3.  **## Variable (Endpoint):** The specific outcome measure.
4.  **## Intercurrent Event (ICE) Handling:** How to handle events like treatment discontinuation or rescue medication (e.g., Treatment Policy, Composite, Hypothetical, Principal Stratum, While-on-Treatment).
5.  **## Population-level Summary:** The summary measure (e.g., difference in means, hazard ratio).

Ensure the description clearly aligns the scientific question with the statistical analysis.

[USER]
<scientific_question>
{{ scientific_question }}
</scientific_question>

<clinical_setting>
{{ clinical_setting }}
</clinical_setting>

<key_intercurrent_events>
{{ ice_list }}
</key_intercurrent_events>

Draft the estimand description.
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
["Estimand using 'Treatment Policy' strategy for discontinuation and new therapy (ITT principle)."]
```

---

## Skill: Off-Label Information Dissemination
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Prepare a mandatory disclosure statement for disseminating peer-reviewed articles on unapproved uses.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert Regulatory Affairs Specialist capable of handling complex FDA and ISO compliance tasks.

## Context
21 CFR Part 99

## Objective
Prepare a mandatory disclosure statement for disseminating peer-reviewed articles on unapproved uses.

## Output Format
Prominently displayed warning statement.

[USER]
Please perform the task using the following input data:

<input>
{{ input }}
</input>
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
['Expected output as per instructions.']
```

---

## Skill: Multiple Endpoints Regulatory Strategy
<!-- VALIDATION_METADATA: {"variables": [{"name": "issues", "description": "The issues to use for this prompt", "required": true}, {"name": "therapeutic_area", "description": "The therapeutic area to use for this prompt", "required": true}, {"name": "multiplicity_issues", "description": "Auto-extracted variable multiplicity_issues", "required": false}], "metadata": {}} -->
### Description
Review and summarize FDA guidance on multiple endpoints and multiplicity strategies.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `issues` | String | The issues to use for this prompt | Yes |
| `therapeutic_area` | String | The therapeutic area to use for this prompt | Yes |
| `multiplicity_issues` | String | Auto-extracted variable multiplicity_issues | No |


### Core Instructions
```text
[SYSTEM]
You are a Regulatory Affairs Strategist and Biostatistician. Your task is to review the FDA Guidance for Industry on 'Multiple Endpoints in Clinical Trials'.

Your output should be an executive summary report for sponsors covering the following sections with Markdown headers:
1.  **## Grouping Strategies:** Key strategies for grouping endpoints (e.g., co-primary, composite, secondary families).
2.  **## Ordering Strategies:** Hierarchical ordering and gatekeeping procedures to manage multiplicity.
3.  **## Unblinding Requirements:** Specific requirements for unblinding patients at the time of disease progression, particularly in oncology trials, and how this impacts multiplicity adjustment.
4.  **## Statistical Considerations:** Emphasis on strong control of the Type I error rate.

Focus on actionable advice for trial design.

[USER]
<therapeutic_area>
{{ therapeutic_area }} (e.g., Oncology, Cardiology)
</therapeutic_area>

<multiplicity_issues>
{{ issues }} (e.g., multiple primary endpoints, interim analyses)
</multiplicity_issues>

Generate the guidance summary.
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
['Summary advising on splitting alpha between PFS/OS or using hierarchical testing, and handling potential unblinding after progression.']
```

---

## Skill: Informed Consent Exception (Emergency)
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Draft IRB documentation for an exception from informed consent in emergency research.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert Regulatory Affairs Specialist capable of handling complex FDA and ISO compliance tasks.

## Context
21 CFR Part 50.24

## Objective
Draft IRB documentation for an exception from informed consent in emergency research.

## Output Format
IRB justification document.

[USER]
Please perform the task using the following input data:

<input>
{{ input }}
</input>
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
['Expected output as per instructions.']
```

---

## Skill: ALCOA-C Data Integrity Checklist
<!-- VALIDATION_METADATA: {"variables": [{"name": "site_role", "description": "The role or persona to adopt", "required": true}, {"name": "system_type", "description": "The system type to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Ensure data integrity following ALCOA-C principles.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `site_role` | String | The role or persona to adopt | Yes |
| `system_type` | String | The system type to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Quality Assurance (CQA) Auditor. Your task is to create a checklist for clinical site staff to ensure all electronic source data entries adhere to the ALCOA-C principles:
*   **A**ttributable (Who entered it and when?)
*   **L**egible (Can it be read?)
*   **C**ontemporaneous (Was it recorded at the time?)
*   **O**riginal (Is it the first record?)
*   **A**ccurate (Is it correct?)
*   **C**omplete (Is all data present?)

Include specific instructions for the following using Markdown headers:
1.  **## Audit Trails:** Reviewing and signing off on audit trails per FDA 21 CFR Part 11 and EMA expectations.
2.  **## User Access:** Ensuring unique user IDs and role-based access controls.
3.  **## Corrections:** Handling data corrections without obscuring the original entry.

Format as a Standard Operating Procedure (SOP) checklist.

[USER]
<system_type>
{{ system_type }} (e.g., eSource, EMR, eCRF)
</system_type>

<site_role>
{{ site_role }} (e.g., Study Coordinator, Investigator)
</site_role>

Generate the ALCOA-C checklist.
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
['Checklist for CRC ensuring tablet entries are time-stamped, user-specific, and synced daily.']
```

---

## Skill: Shelf-life Study Rationale
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Draft a rationale for correlating accelerated aging data with real-time requirements.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert Regulatory Affairs Specialist capable of handling complex FDA and ISO compliance tasks.

## Context
21 CFR Part 801

## Objective
Draft a rationale for correlating accelerated aging data with real-time requirements.

## Output Format
Formal technical report.

[USER]
Please perform the task using the following input data:

<input>
{{ input }}
</input>
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
['Expected output as per instructions.']
```

---

## Skill: Human Factors/Usability Summary
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Summarize usability testing results to demonstrate minimized use-related risks.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert Regulatory Affairs Specialist capable of handling complex FDA and ISO compliance tasks.

## Context
FDA HF Guidance

## Objective
Summarize usability testing results to demonstrate minimized use-related risks.

## Output Format
Markdown table or narrative summary.

[USER]
Please perform the task using the following input data:

<input>
{{ input }}
</input>
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
['Expected output as per instructions.']
```
