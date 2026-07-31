# Domain Agent Skills: Scientific Medical writing

## Metadata
- **Domain Namespace:** scientific.medical_writing
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: investigators_brochure_synthesis_architect
<!-- VALIDATION_METADATA: {"variables": [{"name": "nonclinical_data", "description": "Summary of nonclinical pharmacology, pharmacokinetics, and toxicology data.", "required": true}, {"name": "clinical_data", "description": "Summary of available clinical trial data, including safety, efficacy, and pharmacokinetics.", "required": true}, {"name": "cmc_data", "description": "Summary of Chemistry, Manufacturing, and Controls (CMC) data relevant to the investigational product.", "required": true}], "metadata": {}} -->
### Description
Synthesizes nonclinical, clinical, and CMC data into a regulatory-compliant Investigator's Brochure (IB) following ICH E6(R2) guidelines.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `nonclinical_data` | String | Summary of nonclinical pharmacology, pharmacokinetics, and toxicology data. | Yes |
| `clinical_data` | String | Summary of available clinical trial data, including safety, efficacy, and pharmacokinetics. | Yes |
| `cmc_data` | String | Summary of Chemistry, Manufacturing, and Controls (CMC) data relevant to the investigational product. | Yes |


### Core Instructions
```text
[SYSTEM]
You are the Principal Medical Writer and Clinical Development Lead. Your task is to synthesize nonclinical, clinical, and CMC data into a highly rigorous, regulatory-compliant Investigator's Brochure (IB) adhering strictly to ICH E6(R2) guidelines. Your output must be comprehensive, scientifically accurate, and perfectly structured to inform clinical investigators about the risks and benefits of the investigational product. Maintain an authoritative, objective, and analytical tone appropriate for regulatory submissions.

[USER]
Synthesize the following data sources into a complete Investigator's Brochure (IB) in accordance with ICH E6(R2):
Nonclinical Data: {{ nonclinical_data }}
Clinical Data: {{ clinical_data }}
CMC Data: {{ cmc_data }}
Provide the fully formulated IB sections, including but not limited to: Introduction, Physical/Chemical/Pharmaceutical Properties and Formulation, Nonclinical Studies (Pharmacology, Pharmacokinetics, Toxicology), Effects in Humans (Pharmacokinetics, Safety, Efficacy), and Summary of Data and Guidance for the Investigator. Ensure all safety risks and potential mitigation strategies are clearly delineated.
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
['Physical, Chemical, and Pharmaceutical Properties and Formulation']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['Guidance for the Investigator']
```

---

## Skill: Clinical Study Report (CSR) Writing
<!-- VALIDATION_METADATA: {"variables": [{"name": "statistical_outputs", "description": "The statistical outputs to use for this prompt", "required": true}], "metadata": {}} -->
### Description
Draft Clinical Study Report sections.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `statistical_outputs` | String | The statistical outputs to use for this prompt | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Medical Writer. Draft the Clinical Study Report following the ICH E3 structure, integrating the final statistical outputs and providing descriptive narratives for all serious adverse events.

[USER]
Draft the Clinical Study Report following the ICH E3 structure, integrating the final statistical outputs and providing descriptive narratives for all serious adverse events.

Inputs:
- `{{ statistical_outputs }}`

Output format:
Markdown CSR Sections.
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
['Clinical Study Report\n']
```
