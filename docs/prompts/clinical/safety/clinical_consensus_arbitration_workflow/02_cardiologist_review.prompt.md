---
title: Cardiologist Review
---

# Cardiologist Review

Evaluates a medical report from a cardiology perspective.



```yaml
name: Cardiologist Review
version: "1.0.0"
description: Evaluates a medical report from a cardiology perspective.
metadata:
  domain: clinical
  complexity: medium
  tags:
    - clinical
    - review
variables:
  - name: report_content
    description: The medical report content to review.
    required: true
  - name: introduce_conflict
    description: Whether to introduce a conflict for testing purposes.
    required: true
model: gpt-4o-mini
modelParameters:
  temperature: 0.1
messages:
  - role: system
    content: |
      You are an expert cardiologist reviewer.
      If the input introduce_conflict is "true", output a clinical rejection or safety concern. Otherwise, output a clinical approval.
  - role: user
    content: |
      Please review this report: {{report_content}}
      Introduce conflict: {{introduce_conflict}}
testData:
  - inputs:
      report_content: "Patient oncology report with cardiac risk assessment."
      introduce_conflict: "false"
    expected: "Cardiologist Review: Approved. Cardiac function is normal and within safe protocols."
  - inputs:
      report_content: "Patient oncology report with cardiac risk assessment."
      introduce_conflict: "true"
    expected: "Cardiologist Review: Rejected. Potential risk of severe QTc prolongation detected."
evaluators: []

```
