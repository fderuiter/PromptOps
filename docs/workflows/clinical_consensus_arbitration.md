---
title: Clinical Consensus Arbitration Workflow
---

# Clinical Consensus Arbitration Workflow

A clinical peer review workflow that executes three distinct expert steps and uses Jinja to parse and route them.

## Workflow Diagram

```mermaid
graph TD
    classDef stepNode fill:#1a5f7a,stroke:var(--md-default-fg-color,var(--text-color,#0d3a4d)),stroke-width:2px,color:#ffffff;
    classDef inputNode fill:#2c5e43,stroke:var(--md-default-fg-color,var(--text-color,#183b27)),stroke-width:2px,color:#ffffff;
    INPUT_report_content([Input: report_content]):::inputNode
    INPUT_introduce_conflict([Input: introduce_conflict]):::inputNode
    oncologist_review[oncologist_review<br><i>01_oncologist_review.prompt.yaml</i>]:::stepNode
    INPUT_report_content -. report_content .-> oncologist_review
    INPUT_introduce_conflict -. introduce_conflict .-> oncologist_review
    oncologist_review -->|sequential| cardiologist_review
    cardiologist_review[cardiologist_review<br><i>02_cardiologist_review.prompt.yaml</i>]:::stepNode
    INPUT_report_content -. report_content .-> cardiologist_review
    INPUT_introduce_conflict -. introduce_conflict .-> cardiologist_review
    cardiologist_review -->|sequential| toxicologist_review
    toxicologist_review[toxicologist_review<br><i>03_toxicologist_review.prompt.yaml</i>]:::stepNode
    INPUT_report_content -. report_content .-> toxicologist_review
    INPUT_introduce_conflict -. introduce_conflict .-> toxicologist_review
    toxicologist_review -->|sequential| meta_orchestration
    meta_orchestration[meta_orchestration<br><i>04_meta_orchestrator.prompt.yaml</i>]:::stepNode
    oncologist_review -. oncologist_review .-> meta_orchestration
    cardiologist_review -. cardiologist_review .-> meta_orchestration
    toxicologist_review -. toxicologist_review .-> meta_orchestration
    meta_orchestration -->|sequential| arbitration
    arbitration[arbitration<br><i>05_arbitration.prompt.yaml</i>]:::stepNode
    meta_orchestration -. meta_orchestration_summary .-> arbitration
    arbitration -->|conditional| manual_audit
    arbitration -->|unconditional| validated_data
    manual_audit[manual_audit<br><i>06_manual_audit.prompt.yaml</i>]:::stepNode
    meta_orchestration -. meta_orchestration_summary .-> manual_audit
    manual_audit -->|sequential| validated_data
    validated_data[validated_data<br><i>07_validated_data.prompt.yaml</i>]:::stepNode
    meta_orchestration -. meta_orchestration_summary .-> validated_data
    linkStyle default stroke:var(--md-default-fg-color,var(--text-color,#767676)),stroke-width:2px;
```


