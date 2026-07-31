# Domain Agent Skills: Clinical Adjudication Adjudication workflow

## Metadata
- **Domain Namespace:** clinical.adjudication.adjudication_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Analyze Adjudication KPIs
<!-- VALIDATION_METADATA: {"variables": [{"name": "adjudication_log", "description": "event log export", "required": true}], "metadata": {}} -->
### Description
Calculate adjudication performance metrics and recommend improvements.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `adjudication_log` | String | event log export | Yes |


### Core Instructions
```text
[SYSTEM]
- CSV file `adjudication_log` lists all events in an oncology trial.
- Leadership expects a plan to reduce median cycle time by 20%.

Request a data dictionary if any column in the CSV is ambiguous before starting the analysis.

[USER]
1. Load the CSV and compute:
   - median and 90th percentile cycle time from event trigger to final decision
   - reviewer disagreement rate
   - top three root causes of delays inferred from status fields
2. Create bar charts for each metric and save them as PNGs.
3. Recommend at least five concrete process changes tied to these metrics that would achieve the target reduction.

Inputs:
- `{{ adjudication_log }}` – event log export

Output format:
- **Metrics Summary Table**
- Embedded charts or download links for each PNG
- Bullet list of recommendations
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
['- **Metrics Summary Table**\n- Embedded charts or download links for each PNG\n- Bullet list of recommendations']
```

---

## Skill: Real-Time Adjudication Visibility Dashboard
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The input query from the user, containing any specific constraints or parameters.", "required": true}, {"name": "user_query", "description": "Auto-extracted variable user_query", "required": false}], "metadata": {}} -->
### Description
Design a dashboard that provides real-time visibility into clinical endpoint adjudication workflows.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The input query from the user, containing any specific constraints or parameters. | Yes |
| `user_query` | String | Auto-extracted variable user_query | No |


### Core Instructions
```text
[SYSTEM]
- Phase III cardiovascular device study with ~950 suspected events across 120 sites.
- A blinded Clinical Events Committee adjudicates each event.
- Stakeholders need immediate insight into blocked events and next actions.

Ask clarifying questions if any requirement is unclear before producing the dashboard description.

[USER]
1. Draft a textual workflow diagram from site submission to final CEC decision.
2. Define the minimal data model for a role-based dashboard showing:
   - event aging in days
   - disagreement rate
   - percentage of dossiers missing required documents
   - adjudicator workload
3. List five automated alerts or reminders that reduce turnaround time.
4. Recommend two commercial or open-source eAdjudication platforms and justify the choice.

<user_query>
{{ input }}
</user_query>

Output format:
- **Section 1:** Workflow diagram
- **Section 2:** Dashboard data model (table)
- **Section 3:** Alert rules (bullets)
- **Section 4:** Platform recommendations (table)
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
['- **Section 1:** Workflow diagram\n- **Section 2:** Dashboard data model (table)\n- **Section 3:** Alert rules (bullets)\n- **Section 4:** Platform recommendations (table)\n']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['- **Section 1:** Workflow diagram\n- **Section 2:** Dashboard data model (table)\n- **Section 3:** Alert rules (bullets)\n- **Section 4:** Platform recommendations (table)\n']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['- **Section 1:** Workflow diagram\n- **Section 2:** Dashboard data model (table)\n- **Section 3:** Alert rules (bullets)\n- **Section 4:** Platform recommendations (table)\n']
```

**Input Context:**
```yaml
{}
```
**Asserted Output:**
```text
['- **Section 1:** Workflow diagram\n- **Section 2:** Dashboard data model (table)\n- **Section 3:** Alert rules (bullets)\n- **Section 4:** Platform recommendations (table)\n']
```

---

## Skill: Source Document and Endpoint Checklist
<!-- VALIDATION_METADATA: {"variables": [{"name": "charter_excerpt", "description": "relevant sections of the adjudication charter", "required": true}], "metadata": {}} -->
### Description
Create a clear checklist of required documents and endpoint criteria for clinical adjudication.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `charter_excerpt` | String | relevant sections of the adjudication charter | Yes |


### Core Instructions
```text
[SYSTEM]
- Draft adjudication charter lists seven primary endpoints but lacks detail on required source documents.
- Adjudicators previously received incomplete packages.

Ask any clarifying questions before generating the checklist.

[USER]
1. For each endpoint, build a checklist of required documents including imaging, labs, and narrative notes with formatting rules.
2. Convert each endpoint definition into binary inclusion or exclusion criteria.
3. Suggest concise form-field wording (≤50 characters) for EDC alignment.
4. Flag ambiguous language in the draft charter that needs clarification from the sponsor.

Inputs:
- `{{ charter_excerpt }}` – relevant sections of the adjudication charter.

Output format:
- Markdown table per endpoint with columns: *Doc Type*, *Required?*, *Acceptable Formats*, *Notes*.
- Numbered list of **Clarification Needed** items.
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
['- Markdown table per endpoint with columns: *Doc Type*, *Required?*, *Acceptable Formats*, *Notes*.\n- Numbered list of **Clarification Needed** items.']
```
