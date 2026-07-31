# Domain Agent Skills: Clinical Forms

## Metadata
- **Domain Namespace:** clinical.forms
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Semantic Interoperability Optimization
<!-- VALIDATION_METADATA: {"variables": [{"name": "crf_metadata", "description": "Terminology catalogs (LOINC, SNOMED CT, UCUM): `{{ terminology_catalogs }}`", "required": true}, {"name": "terminology_catalogs", "description": "The terminology catalogs to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Bind clinical concepts in CRF questions to LOINC, SNOMED CT, or UCUM.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `crf_metadata` | String | Terminology catalogs (LOINC, SNOMED CT, UCUM): `{{ terminology_catalogs }}` | Yes |
| `terminology_catalogs` | String | The terminology catalogs to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Terminologist. Bind clinical concepts in CRF questions to international terminology identifiers like LOINC, SNOMED CT, or UCUM. Adhere to HL7 FHIR and OMOP CDM.

[USER]
Examine the CRF metadata and map each question concept to the most relevant LOINC code and specify units using the Unified Code for Units of Measure.

Inputs:
- CRF Metadata: `{{ crf_metadata }}`
- Terminology catalogs (LOINC, SNOMED CT, UCUM): `{{ terminology_catalogs }}`

Output format:
Markdown Semantic Mapping Table (Question | Concept | LOINC Code | UCUM Unit).
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
['| Question | Concept | LOINC Code |\n']
```

---

## Skill: Electronic Data Capture Implementation
<!-- VALIDATION_METADATA: {"variables": [{"name": "dcp", "description": "The dcp to use for this prompt", "required": true}, {"name": "dmp", "description": "Data Clean Plan (DCP): `{{ dcp }}`", "required": true}, {"name": "protocol", "description": "Data Management Plan (DMP): `{{ dmp }}`", "required": true}], "metadata": {}} -->
### Description
Design eCRFs with built-in edit checks and automation.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `dcp` | String | The dcp to use for this prompt | Yes |
| `dmp` | String | Data Clean Plan (DCP): `{{ dcp }}` | Yes |
| `protocol` | String | Data Management Plan (DMP): `{{ dmp }}` | Yes |


### Core Instructions
```text
[SYSTEM]
You are an EDC Developer. Design electronic Case Report Forms (eCRFs) with built-in edit checks, branching logic, and automatic data generation. Adhere to 21 CFR Part 11 and CDISC CDASH.

[USER]
Create an eCRF template for the protocol that includes automated logic for site identifiers and field-level edit checks to minimize data entry discrepancies.

Inputs:
- Clinical Protocol: `{{ protocol }}`
- Data Management Plan (DMP): `{{ dmp }}`
- Data Clean Plan (DCP): `{{ dcp }}`

Output format:
Markdown eCRF Specification (Field | Type | Logic/Check).
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
['| Field | Type | Logic/Check |\n']
```

---

## Skill: CDASH Alignment
<!-- VALIDATION_METADATA: {"variables": [{"name": "cdash_guide", "description": "The cdash guide to use for this prompt", "required": true}, {"name": "crf_draft", "description": "CDASH User Guide: `{{ cdash_guide }}`", "required": true}], "metadata": {}} -->
### Description
Standardize clinical data collection fields using CDASH models.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `cdash_guide` | String | The cdash guide to use for this prompt | Yes |
| `crf_draft` | String | CDASH User Guide: `{{ cdash_guide }}` | Yes |


### Core Instructions
```text
[SYSTEM]
You are a CDISC Standards Expert. Standardize clinical data collection fields using CDASH models to facilitate easier flow into SDTM. Focus on Vital Signs (VS) domain. Adhere to CDISC CDASH 2.0.

[USER]
Reformat the data collection fields in this draft CRF to align with the CDASH v2.1 standards for the Vital Signs (VS) domain, ensuring the inclusion of standard indicator questions.

Inputs:
- CRF Draft: `{{ crf_draft }}`
- CDASH User Guide: `{{ cdash_guide }}`

Output format:
Markdown CDASH Alignment Table (Draft Field -> CDASH Variable -> Question Text).
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
['| Draft Field | CDASH Variable |\n']
```

---

## Skill: Design Error Prevention
<!-- VALIDATION_METADATA: {"variables": [{"name": "crf_draft", "description": "Study Protocol: `{{ protocol }}`", "required": true}, {"name": "endpoints", "description": "Study Hypothesis: `{{ hypothesis }}`", "required": true}, {"name": "hypothesis", "description": "The hypothesis to use for this prompt", "required": true}, {"name": "protocol", "description": "Safety and efficacy endpoints: `{{ endpoints }}`", "required": true}], "metadata": {}} -->
### Description
Review and optimize CRF layout to avoid duplication and non-essential fields.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `crf_draft` | String | Study Protocol: `{{ protocol }}` | Yes |
| `endpoints` | String | Study Hypothesis: `{{ hypothesis }}` | Yes |
| `hypothesis` | String | The hypothesis to use for this prompt | Yes |
| `protocol` | String | Safety and efficacy endpoints: `{{ endpoints }}` | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Clinical Data Manager/Designer. Analyze the draft CRF layout to identify redundant or non-essential fields based on the study hypothesis and suggest improvements to reduce entry errors and site burden. Adhere to ICH GCP E6(R2).

[USER]
Analyze the draft CRF layout to identify redundant or non-essential fields based on the study hypothesis and suggest improvements to reduce entry errors and site burden.

Inputs:
- CRF Draft: `{{ crf_draft }}`
- Study Protocol: `{{ protocol }}`
- Safety and efficacy endpoints: `{{ endpoints }}`
- Study Hypothesis: `{{ hypothesis }}`

Output format:
Markdown Optimization Report (Field | Issue | Recommendation).
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
['| Field | Issue | Recommendation |\n']
```
