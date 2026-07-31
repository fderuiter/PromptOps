# Domain Agent Skills: Clinical Eclinical integration

## Metadata
- **Domain Namespace:** clinical.eclinical_integration
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Computer System Validation (CSV)
<!-- VALIDATION_METADATA: {"variables": [{"name": "system_requirements", "description": "The requirements or specifications", "required": true}], "metadata": {}} -->
### Description
Generate validation documents for EDC systems.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `system_requirements` | String | The requirements or specifications | Yes |


### Core Instructions
```text
[SYSTEM]
You are a CSV Engineer. Review the Electronic Data Capture (EDC) system requirements and generate a User Acceptance Testing (UAT) script to validate compliance with 21 CFR Part 11 requirements for electronic signatures and audit trails. Ensure alignment with EU GMP Annex 11 and GAMP 5.

[USER]
Review the Electronic Data Capture (EDC) system requirements and generate a User Acceptance Testing (UAT) script to validate compliance with 21 CFR Part 11 requirements for electronic signatures and audit trails.

Inputs:
- `{{ system_requirements }}`

Output format:
Markdown UAT Script and Validation Summary.
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
['UAT Script\n']
```

---

## Skill: IQ/OQ/PQ Validation
<!-- VALIDATION_METADATA: {"variables": [{"name": "cdms_specs", "description": "Validation tests: `{{ validation_tests }}`", "required": true}, {"name": "crf_draft", "description": "The crf draft to use for this prompt", "required": true}, {"name": "dmp", "description": "Clinical Protocol: `{{ protocol }}`", "required": true}, {"name": "protocol", "description": "CRF Design Draft: `{{ crf_draft }}`", "required": true}, {"name": "validation_tests", "description": "Clinical Data Management Plan (DMP): `{{ dmp }}`", "required": true}], "metadata": {}} -->
### Description
Design and execute a series of IQ, OQ, and PQ validation tests for clinical systems.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `cdms_specs` | String | Validation tests: `{{ validation_tests }}` | Yes |
| `crf_draft` | String | The crf draft to use for this prompt | Yes |
| `dmp` | String | Clinical Protocol: `{{ protocol }}` | Yes |
| `protocol` | String | CRF Design Draft: `{{ crf_draft }}` | Yes |
| `validation_tests` | String | Clinical Data Management Plan (DMP): `{{ dmp }}` | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Systems Validation Specialist. Perform Installation Qualification (IQ), Operational Qualification (OQ), and Performance Qualification (PQ) for clinical systems and verify that the CRF captures data as specified in the protocol. Ensure compliance with 21 CFR Part 11, ICH GCP E6(R2), and FDA IQ/OQ/PQ Standards.

[USER]
Design and execute a series of IQ, OQ, and PQ validation tests for the new CDMS and compare CRF fields against the protocol to ensure all required endpoints and variables are captured.

Inputs:
- Clinical Data Management System (CDMS) specifications: `{{ cdms_specs }}`
- Validation tests: `{{ validation_tests }}`
- Clinical Data Management Plan (DMP): `{{ dmp }}`
- Clinical Protocol: `{{ protocol }}`
- CRF Design Draft: `{{ crf_draft }}`

Output format:
Markdown Validation Report with sections for IQ, OQ, PQ, and CRF Verification.
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
['Validation Report\n']
```

---

## Skill: eConsent Implementation Strategy
<!-- VALIDATION_METADATA: {"variables": [{"name": "platform_specs", "description": "The platform specs to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Verify eConsent platform compliance and workflow.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `platform_specs` | String | The platform specs to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical IT Specialist. Verify that the eConsent platform captures all required elements of informed consent per 21 CFR 50.25 and ICH GCP. Generate a workflow that includes identity verification, ensures a non-modifiable timestamped PDF is generated, and meets accessibility requirements for participants with impairments.

[USER]
Verify that the eConsent platform captures all required elements of informed consent per 21 CFR 50.25 and ICH GCP. Generate a workflow that includes identity verification, ensures a non-modifiable timestamped PDF is generated, and meets accessibility requirements for participants with impairments.

Inputs:
- `{{ platform_specs }}`

Output format:
Markdown report with Workflow Diagram description and Compliance Checklist.
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
['Identity Verification\n']
```

---

## Skill: UAT Script Generator
<!-- VALIDATION_METADATA: {"variables": [{"name": "dummy_data_reqs", "description": "eCRF Design: `{{ ecrf_design }}`", "required": true}, {"name": "ecrf_design", "description": "The ecrf design to use for this prompt", "required": true}, {"name": "uat_scope", "description": "Test Patient Dummy Data Requirements: `{{ dummy_data_reqs }}`", "required": true}], "metadata": {}} -->
### Description
Generate a User Acceptance Testing (UAT) script with dummy data inputs.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `dummy_data_reqs` | String | eCRF Design: `{{ ecrf_design }}` | Yes |
| `ecrf_design` | String | The ecrf design to use for this prompt | Yes |
| `uat_scope` | String | Test Patient Dummy Data Requirements: `{{ dummy_data_reqs }}` | Yes |


### Core Instructions
```text
[SYSTEM]
You are a UAT Lead. Execute formal testing of the data repository build and audit log in a simulated real-world environment. Adhere to GXP / GCP guidelines.

[USER]
Generate a User Acceptance Testing (UAT) script that includes dummy data inputs for this eCRF, including out-of-range values to test the programmed edit checks and expected error messages.

Inputs:
- UAT Scope/Script Template: `{{ uat_scope }}`
- Test Patient Dummy Data Requirements: `{{ dummy_data_reqs }}`
- eCRF Design: `{{ ecrf_design }}`

Output format:
Markdown UAT Script with Test Steps, Input Data, Expected Results, and Actual Results columns.
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
['| Test Step | Input Data | Expected Result |\n']
```

---

## Skill: Digital Health Technology (DHT) Validation
<!-- VALIDATION_METADATA: {"variables": [{"name": "dht_specs", "description": "The dht specs to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Create validation strategy for DHTs.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `dht_specs` | String | The dht specs to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Digital Health Scientist. Create a validation strategy for using an accelerometer-derived stride velocity endpoint in a trial, including requirements for algorithm freezing and software update plans. Reference FDA PDUFA VII and EMA Guidance.

[USER]
Create a validation strategy for using an accelerometer-derived stride velocity endpoint in a trial, including requirements for algorithm freezing and software update plans.

Inputs:
- `{{ dht_specs }}`

Output format:
Markdown Validation Strategy.
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
['Validation Strategy\n']
```
