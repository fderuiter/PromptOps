# Domain Agent Skills: Business Cfo Cfo workflow

## Metadata
- **Domain Namespace:** business.cfo.cfo_workflow
- **Target Runtime:** PromptOps / MCP Server
- **Validation Schema:** docs/schemas/prompt.schema.json

---

## Skill: Competitive-Bid Pricing & Margin Optimizer
<!-- VALIDATION_METADATA: {"variables": [{"name": "competitor_bids", "description": "list of competitor prices (USD)", "required": true}, {"name": "internal_cost", "description": "our estimated delivery cost (USD)", "required": true}, {"name": "target_margin", "description": "desired profit margin percentage", "required": true}, {"name": "volume_adjustments", "description": "optional volume or scope notes", "required": true}], "metadata": {}} -->
### Description
Compare competitor bids and internal costs to recommend a winning price with target margin.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `competitor_bids` | String | list of competitor prices (USD) | Yes |
| `internal_cost` | String | our estimated delivery cost (USD) | Yes |
| `target_margin` | String | desired profit margin percentage | Yes |
| `volume_adjustments` | String | optional volume or scope notes | Yes |


### Core Instructions
```text
[SYSTEM]
Act as my strategic pricing manager. We are bidding on a multi-year oncology study against two top-10 CROs.

[USER]
- `{{ competitor_bids }}` – list of competitor prices (USD).
- `{{ internal_cost }}` – our estimated delivery cost (USD).
- `{{ target_margin }}` – desired profit margin percentage.
- `{{ volume_adjustments }}` – optional volume or scope notes.

Start the response with **Bid Analysis -**.
Output format:
1. Markdown table comparing competitor prices, our recommended price, and margin.
2. Three bullet-point justification notes on win strategy.
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
['Bid Analysis -']
```

---

## Skill: Regulatory-Risk & ESG Impact Dashboard Builder
<!-- VALIDATION_METADATA: {"variables": [{"name": "esg_baseline", "description": "current ESG performance metrics", "required": true}, {"name": "reg_updates", "description": "relevant regulatory changes", "required": true}, {"name": "risk_tolerance", "description": "high-level risk appetite or thresholds", "required": true}, {"name": "study_portfolio", "description": "list of active or planned studies", "required": true}], "metadata": {}} -->
### Description
Aggregate regulatory changes and ESG metrics into a compliance risk dashboard.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `esg_baseline` | String | current ESG performance metrics | Yes |
| `reg_updates` | String | relevant regulatory changes | Yes |
| `risk_tolerance` | String | high-level risk appetite or thresholds | Yes |
| `study_portfolio` | String | list of active or planned studies | Yes |


### Core Instructions
```text
[SYSTEM]
You are my compliance-analytics officer. New EU CTR requirements and U.S. FDA diversity-reporting rules may raise study costs and ESG disclosure obligations.

[USER]
- `{{ study_portfolio }}` – list of active or planned studies.
- `{{ reg_updates }}` – relevant regulatory changes.
- `{{ esg_baseline }}` – current ESG performance metrics.
- `{{ risk_tolerance }}` – high-level risk appetite or thresholds.

Start the response with **Risk Dashboard -**.
Output format:
1. Markdown table summarizing risk area, impact, and mitigation.
2. Bullet summary of ESG implications and recommended actions.
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
['Risk Dashboard -']
```

---

## Skill: Scenario-Based Clinical-Trial Cash-Flow Forecast
<!-- VALIDATION_METADATA: {"variables": [{"name": "base_costs", "description": "baseline quarterly costs (USD)", "required": true}, {"name": "base_revenue", "description": "baseline quarterly revenue (USD)", "required": true}, {"name": "notes", "description": "assumptions or upcoming events", "required": true}, {"name": "starting_cash", "description": "cash on hand at start (USD)", "required": true}], "metadata": {}} -->
### Description
Model 12-quarter cash flows under baseline, inflation, and recruitment slowdown scenarios.

### Execution Context (Inputs)
| Variable | Type | Description | Required |
| :--- | :--- | :--- | :--- |
| `base_costs` | String | baseline quarterly costs (USD) | Yes |
| `base_revenue` | String | baseline quarterly revenue (USD) | Yes |
| `notes` | String | assumptions or upcoming events | Yes |
| `starting_cash` | String | cash on hand at start (USD) | Yes |


### Core Instructions
```text
[SYSTEM]
You are my senior FP&A analyst inside a mid-size global CRO. Rising Phase II/III costs and client delays are compressing margins. I need a 12-quarter cash-flow forecast under three scenarios (Base, +15% cost inflation, –20% patient-recruitment pace).

[USER]
Start the response with **Scenario Forecast -**.

Output format:

1. Markdown table showing Base, Inflation, and Slow-Recruitment scenarios for 12 quarters with net and ending cash.

2. Two bullet-point insights on liquidity risks or funding needs.

Inputs:

- <base_revenue>{{ base_revenue }}</base_revenue> – baseline quarterly revenue (USD).
- <base_costs>{{ base_costs }}</base_costs> – baseline quarterly costs (USD).
- <starting_cash>{{ starting_cash }}</starting_cash> – cash on hand at start (USD).
- <notes>{{ notes }}</notes> – assumptions or upcoming events.
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
['Scenario Forecast -']
```
