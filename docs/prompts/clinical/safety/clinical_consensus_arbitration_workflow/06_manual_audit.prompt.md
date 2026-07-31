---
title: Manual Clinical Audit Fallback
---

# Manual Clinical Audit Fallback

Places the report in the manual safety review queue due to disagreement.



```yaml
name: Manual Clinical Audit Fallback
version: "1.0.0"
description: Places the report in the manual safety review queue due to disagreement.
metadata:
  domain: clinical
  complexity: medium
  tags:
    - clinical
    - safety
variables:
  - name: meta_orchestration_summary
    description: Summary of disagreement.
    required: true
model: gpt-4o-mini
modelParameters:
  temperature: 0.1
messages:
  - role: system
    content: |
      You are a clinical safety auditor.
  - role: user
    content: |
      Review conflict summary for audit: {{meta_orchestration_summary}}
testData:
  - inputs: {}
    expected: "Manual Audit: Fallback initiated. Sent to manual queue due to medical expert disagreement: Cardiologist concerns regarding QTc prolongation."
evaluators: []

```
