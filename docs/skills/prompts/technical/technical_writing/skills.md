# Domain Agent Skills: Technical Technical writing

## Metadata
- **Domain Namespace:** technical.technical_writing
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Technical White Paper for Clinical Methodologies
<!-- VALIDATION_METADATA: {"variables": [{"name": "paper_title", "description": "The title of the white paper.", "required": true, "default": "De-Risking Clinical Development: The Methodology of In Silico Trials"}, {"name": "context_description", "description": "Context about the purpose and audience of the paper.", "required": true, "default": "We need to prove to our clients that our \"In Silico\" simulations are scientifically valid and not just a \"black box.\" I am providing you with the core pillars of our offering.\n"}, {"name": "source_material", "description": "The core concepts or pillars to cover in the paper.", "required": true, "default": "* **Concept 1 (SCA):** Constructing \"synthetic\" arms using historical clinical trial data and RWE.\n* **Concept 2 (Simulation):** Agent-based modeling to simulate protocol feasibility (predicting dropouts, site burden).\n* **Concept 3 (Digital Twins):** Virtual physiological models for biomarker efficacy prediction.\n"}, {"name": "specific_requirements", "description": "Specific requirements for the body of the white paper.", "required": true, "default": "2. **Methodology Section - Synthetic Control Arms:**\n* Explain the statistical techniques used to match real-world data to trial patients (e.g., Propensity Score Matching, exact matching).\n* Discuss how we handle data heterogeneity and bias.\n\n3. **Methodology Section - Agent-Based Modeling:**\n* Describe how \"Agents\" (patients/sites) are programmed. What variables define an agent? (e.g., compliance probability, distance to clinic, symptom severity).\n* Explain how the simulation runs \"Monte Carlo\" style iterations to predict failure points.\n\n4. **Methodology Section - Mechanistic Digital Twins:**\n* Explain the difference between statistical modeling and physiological/mechanistic modeling.\n* Case Study Example: Create a hypothetical scenario where a Digital Twin identifies that a drug only works on patients with a specific renal profile.\n"}], "metadata": {}} -->
### Description
Generates a deep technical white paper or educational document for clinical methodologies, focusing on scientific validity and regulatory context.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `paper_title` | String | The title of the white paper. | Yes |
| `context_description` | String | Context about the purpose and audience of the paper. | Yes |
| `source_material` | String | The core concepts or pillars to cover in the paper. | Yes |
| `specific_requirements` | String | Specific requirements for the body of the white paper. | Yes |


### Core Instructions
```text
[SYSTEM]
You are a dual expert in Clinical Data Science and Regulatory Affairs. Your tone should be academic, authoritative, detailed, and technically precise. Use LaTeX formatting for any necessary mathematical concepts.

[USER]
**Context:**
{{ context_description }}

**Source Material:**
{{ source_material }}

**Task:**
Write a **Technical White Paper** titled *"{{ paper_title }}"*. The paper must cover:

1. **Introduction:** Define the core subject and the current regulatory appetite for them (reference FDA guidance or EMA opinion papers if applicable).

{{ specific_requirements }}

**Conclusion:** A summary of how these technologies converge to ensure protocol integrity.
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
['Introduction\nMethodology\nConclusion\n']
```
