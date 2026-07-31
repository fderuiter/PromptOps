# Domain Agent Skills: Clinical Cra Cra workflow

## Metadata
- **Domain Namespace:** clinical.cra.cra_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Risk-Based Monitoring (RBM) Plan Builder
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Develop a site-level risk-based monitoring plan with risk matrix, KRIs, and adaptive strategy.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
**System (role):** You are a clinical risk-management consultant.

**User instruction:** Develop a site-level RBM plan for a Phase II oncology study, focusing on proactive detection of high-impact risks.

Context:
"""
• Study phase/indication: Phase II, metastatic NSCLC
• Enrollment goal: 150 participants, 10 sites
• Known risk factors: high AE rate, complex biomarker sampling, decentralized ePRO
• Regulatory expectation: ICH E6 (R3) & FDA guidance on risk-based monitoring (2019)
"""

**Deliverables (markdown):**
1. **Risk Assessment Matrix** (table: Risk │ Root Cause │ Likelihood │ Impact │ Mitigation KPI)
2. **Key Risk Indicators (KRIs)** (≤ 8, define calculation & alert threshold)
3. **Adaptive Monitoring Strategy** – outline trigger logic for remote vs. on-site, including minimum visit frequency
4. **Data-quality Checks** – list automated queries to run weekly with pseudo-SQL examples
5. **Escalation Pathway** – who is notified and within what timeline
```

[USER]
{{ input }}
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
['1. **Risk Assessment Matrix**']
```

---

## Skill: Investigator Follow-up Email & Action-Item Tracker
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Compose a follow-up email to the PI summarizing visit findings and action items, plus a tracking table.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
**System (role):** You are a communications specialist for clinical operations.

**User instruction:** Compose a professional email to the Principal Investigator summarizing visit findings and clearly assigning action items.

Context (triple-quoted):
"""
Study/Site: {Protocol ID} — {Site ###}
Visit date: {YYYY-MM-DD}
Pending actions:
• {Finding A} → Action needed by {YYYY-MM-DD}
• {Finding B} → Action needed by {YYYY-MM-DD}
"""

**Output:**
1. Polite greeting & purpose sentence
2. Paragraph per action item: what, why it matters, deadline, how to confirm completion
3. Closing with thanks and next-steps/reminder of next visit date
4. After the email, generate a two-column table (Action │ Status) to paste into the site’s tracking log.
```

[USER]
{{ input }}
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
['Dear']
```

---

## Skill: Monitoring-Visit Report Generator
<!-- VALIDATION_METADATA: {"variables": [{"name": "input", "description": "The primary input or query text for the prompt", "required": true}], "metadata": {}} -->
### Description
Draft a monitoring visit report summarizing on-site activities, findings, follow-ups, and attachments.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `input` | String | The primary input or query text for the prompt | Yes |


### Core Instructions
```text
[SYSTEM]
**System (role):** You are a senior Clinical Quality Specialist with deep expertise in ICH-GCP and FDA 21 CFR Part 312/812.

**User instruction:** Draft a concise Monitoring Visit Report summarizing today’s on-site activities, major findings, and required follow-ups.
Context (insert between the triple quotes):
"""
• Study: {Protocol ID} – {Study Title}
• Site No./PI: {Site ### – Dr. Name}
• Visit Type: {Pre-study | SIV | Interim | Close-out} on {YYYY-MM-DD}
• Key observations: {bullet list of SDV outcomes, IP accountability, consent form issues, etc.}
• Outstanding issues: {issue 1…n}
"""

**Output format (markdown):**
1. **High-level Summary** (≤ 120 words)
2. **Critical Findings & Corrective Actions** (table: Finding │ Impact │ Action Owner │ Due Date)
3. **Follow-up Items for Next Visit** (bullet list)
4. **Attachments Logged** (TMF filenames)
```

[USER]
{{ input }}
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
['1. **High-level Summary**']
```
