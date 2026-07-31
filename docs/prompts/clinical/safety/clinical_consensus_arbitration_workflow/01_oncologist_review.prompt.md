---
title: Oncologist Review
---

# Oncologist Review

Evaluates a medical report from an oncology perspective.



```yaml
name: Oncologist Review
version: "1.0.0"
description: Evaluates a medical report from an oncology perspective.
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
      You are an expert clinical oncologist.
      If the input introduce_conflict is "true", output a clinical rejection or safety concern. Otherwise, output a clinical approval.
  - role: user
    content: |
      Please review this report: {{report_content}}
      Introduce conflict: {{introduce_conflict}}
testData:
  - inputs:
      report_content: "Patient oncology report with cardiac risk assessment."
      introduce_conflict: "false"
    expected: "Oncologist Review: Approved. The patient meets all criteria and has no active oncology exclusions."
  - inputs:
      report_content: "Patient oncology report with cardiac risk assessment."
      introduce_conflict: "true"
    expected: "Oncologist Review: Approved. The patient meets all criteria and has no active oncology exclusions."
evaluators: []

```
