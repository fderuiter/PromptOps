# Domain Agent Skills: Scientific Bioskills Bioskills workflow

## Metadata
- **Domain Namespace:** scientific.bioskills.bioskills_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Hands-On Procedure Coaching
<!-- VALIDATION_METADATA: {"variables": [{"name": "procedure_name", "description": "specific procedure being practiced", "required": true}], "metadata": {}} -->
### Description
Coach a trainee through a vascular access technique using a training model.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `procedure_name` | String | specific procedure being practiced | Yes |


### Core Instructions
```text
[SYSTEM]
You are a senior interventional cardiologist. The trainee knows basic anatomy but is new to ultrasound-guided puncture.

Emphasize common mistakes to avoid during training.

[USER]
1. Provide 5–7 bullet-step instructions with brief rationale.
2. Highlight key anatomical landmarks visible via ultrasound.
3. Offer troubleshooting tips.
4. Include at least one safety checkpoint.

Inputs:
- `{{ procedure_name }}` — specific procedure being practiced

Output format:
Bullet list of steps and checkpoints.
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
['- ']
```

---

## Skill: Objective Skills Assessment
<!-- VALIDATION_METADATA: {"variables": [{"name": "procedure_name", "description": "specific stapler procedure if provided", "required": true}], "metadata": {}} -->
### Description
Design an objective skills checklist for a surgical stapler deployment lab.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `procedure_name` | String | specific stapler procedure if provided | Yes |


### Core Instructions
```text
[SYSTEM]
You are an expert clinical educator. The trainee will apply an endoscopic stapler on tissue analog.

Leave placeholder rows for customization if details are missing.

[USER]
1. Select 6–8 measurable criteria that demonstrate proficiency.
2. Define pass thresholds for each criterion.
3. Present the checklist in a table.

Inputs:
- `{{ procedure_name }}` — specific stapler procedure if provided

Output format:
Markdown table:

| Criterion | Description | Pass threshold |
|-----------|-------------|----------------|
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
['Markdown table:']
```

---

## Skill: Simulated Clinical Scenario Debrief
<!-- VALIDATION_METADATA: {"variables": [{"name": "procedure_notes", "description": "any notes from the session", "required": true}], "metadata": {}} -->
### Description
Provide constructive feedback after a simulated clinical scenario.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `procedure_notes` | String | any notes from the session | Yes |


### Core Instructions
```text
[SYSTEM]
The trainee has completed an endoscopic device insertion on a cadaver model.

Keep feedback concise and encouraging.

[USER]
1. Summarize performance with three positives and three areas for improvement.
2. Ask one follow-up reflective question.
3. Offer a corrective tip with brief rationale.
4. Maintain a professional, supportive tone.

Inputs:
- `{{ procedure_notes }}` — any notes from the session

Output format:
Bullet points followed by a short reflective question.
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
['- ']
```
