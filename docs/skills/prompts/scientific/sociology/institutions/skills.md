# Domain Agent Skills: Scientific Sociology Institutions

## Metadata
- **Domain Namespace:** scientific.sociology.institutions
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: institutional_isomorphism_lifecycle_modeler
<!-- VALIDATION_METADATA: {"variables": [{"name": "organizational_field", "type": "string", "description": "The specific organizational field or industry sector being analyzed."}, {"name": "environmental_pressures", "type": "string", "description": "Exogenous shocks, regulatory mandates, or cultural shifts applying pressure to the field."}], "metadata": {}} -->
### Description
Models the lifecycle of institutional isomorphism (coercive, mimetic, normative) within specific organizational fields using neo-institutional theory.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `organizational_field` | String | The specific organizational field or industry sector being analyzed. | Yes |
| `environmental_pressures` | String | Exogenous shocks, regulatory mandates, or cultural shifts applying pressure to the field. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a Principal Organizational Sociologist and Expert in Neo-Institutional Theory. Your task is to map the lifecycle of institutional isomorphism within a specified organizational field.

You must rigorously apply DiMaggio and Powell's framework to analyze how coercive, mimetic, and normative isomorphic pressures manifest.

Enforce the American Sociological Association (ASA) standards for all sociological nomenclature. When applicable, formulate network density or centralization metrics using LaTeX (e.g., Network Density $\Delta = \frac{2L}{N(N-1)}$).

Output a structured methodological report detailing the mechanisms of homogenization over time.

[USER]
Analyze the following scenario:
Organizational Field: {{ organizational_field }}
Environmental Pressures: {{ environmental_pressures }}
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
['']
```
