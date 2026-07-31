# Clinical Consensus Arbitration Workflow Overview

## Prompts
- **[Oncologist Review](01_oncologist_review.prompt.yaml)**: Evaluates a medical report from an oncology perspective.
- **[Cardiologist Review](02_cardiologist_review.prompt.yaml)**: Evaluates a medical report from a cardiology perspective.
- **[Toxicologist Review](03_toxicologist_review.prompt.yaml)**: Evaluates a medical report from a toxicology perspective.
- **[Meta-Orchestrator Clinical Review](04_meta_orchestrator.prompt.yaml)**: Compiles and summarizes the expert reviews.
- **[Jinja-Based Arbitration](05_arbitration.prompt.yaml)**: Runs Jinja arbitration parsing consensus vs disagreement.
- **[Manual Clinical Audit Fallback](06_manual_audit.prompt.yaml)**: Places the report in the manual safety review queue due to disagreement.
- **[Output Validated Clinical Data](07_validated_data.prompt.yaml)**: Standardized final validated clinical report generation.
