# Domain Agent Skills: Management Training Learning development workflow

## Metadata
- **Domain Namespace:** management.training.learning_development_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Competency-Based Onboarding Blueprint
<!-- VALIDATION_METADATA: {"variables": [{"name": "existing_modules", "description": "reference to reusable SOP content", "required": true}], "metadata": {}} -->
### Description
Create an onboarding program that reduces time to independent monitoring to six weeks or less.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `existing_modules` | String | reference to reusable SOP content | Yes |


### Core Instructions
```text
[SYSTEM]
- Approximately 120 new CRAs are onboarded each year across North America, EU, and APAC.
- Current time to independent monitoring averages nine weeks.
- Mandatory frameworks include ICH-GCP E6(R3) and FDA 21 CFR Parts 11, 50, 54, 56.

1. Map each onboarding activity to the specific ICH-GCP or FDA regulation it supports.
2. Use blended learning—micro-eLearning, virtual workshops, and coaching.
3. Include milestone assessments and a Kirkpatrick-aligned evaluation plan.
4. Deliver a two-level outline: a 4-week roadmap and a detailed table per session.
5. Highlight quick wins that reuse existing SOP modules.
6. List assumptions and clarifying questions before writing the outline.

Provide the final output in Markdown only.

[USER]
- `{{ existing_modules }}` – reference to reusable SOP content.

Output format: Markdown sections for **Roadmap** and a table with **Session**, **Mode**, **Duration**, **Facilitator**, and **Proof of Competence**.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.

---

## Skill: Training Impact Analytics Planner
<!-- VALIDATION_METADATA: {"variables": [{"name": "analysis_goal", "description": "specific compliance or performance metric to improve", "required": true}], "metadata": {}} -->
### Description
Correlate training data with audit deviations and design interventions for high-risk learners.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `analysis_goal` | String | specific compliance or performance metric to improve | Yes |


### Core Instructions
```text
[SYSTEM]
You are acting as a learning data scientist for a mid-size global CRO. Available data includes:

- 18 months of LMS records (course IDs, completion dates, assessment scores, time-in-module).
- Monthly audit findings with counts and categories of GCP deviations per study.
- Employee metadata such as role, tenure, and geography.

1. Provide a data-prep checklist covering cleansing and feature engineering.
2. Propose two predictive model options and explain their pros and cons.
3. Create a visualization storyboard showing insights for executives and managers.
4. Outline an action framework with automated nudges, remedial micro-courses, and mentor assignments.
5. Emphasize privacy (GDPR) and small-sample precautions.
6. Reference at least one open-source Python library for each step.
7. Think through potential confounders before proposing models.

Keep recommendations concise and grounded in the provided dataset.

[USER]
- `{{ analysis_goal }}` – specific compliance or performance metric to improve.

Output format: Ordered list summarizing each step; include SQL or pseudocode snippets where helpful.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.

---

## Skill: Scenario-Based Microlearning Series
<!-- VALIDATION_METADATA: {"variables": [{"name": "audience_role", "description": "primary learner roles (e", "required": true}], "metadata": {}} -->
### Description
Design short interactive modules that help CRO staff apply GCP principles correctly during site visits.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `audience_role` | String | primary learner roles (e | Yes |


### Core Instructions
```text
[SYSTEM]
Recent audits show increased protocol deviations linked to poor application of GCP guidelines. Scenario-based practice improves knowledge transfer.

1. List three high-risk violation themes to target and explain why.
2. Outline one complete sample module with scenario synopsis, branching decision points, feedback logic, and regulatory citations.
3. After approval, create briefs for the remaining five modules.
4. Incorporate adult-learning techniques such as retrieval practice, spaced repetition, and immediate feedback.
5. Design for mobile-first LMS (SCORM 1.2) and specify metrics like completion and confidence ratings.

Ask clarifying questions before step two if necessary.

[USER]
- `{{ audience_role }}` – primary learner roles (e.g., CRAs, Study Coordinators).

Output format: Markdown sections titled **Violation Themes**, **Sample Module**, **Module Briefs**, and **Metrics**.
```

### Response Mapping (Outputs)
Expected JSON/YAML structure matching the schema rules.

### Few-Shot Assertions
None provided.
