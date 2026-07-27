## Description
Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. If this is a new prompt or workflow, explain its intended persona and use case.

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New prompt/workflow (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation (`docs/`, `overview.md` if creating a new directory)
- [ ] I have run `./scripts/validate_prompts.sh` successfully and all checks pass locally
- [ ] If submitting a prompt: it follows `docs/template_prompt.prompt.yaml` schema
- [ ] If submitting a prompt: it includes realistic `testData` and `evaluators`
- [ ] If submitting a prompt: jinja variables are correctly formatted without spaces inside brackets (e.g. `{{var_name}}`)
- [ ] New and existing unit tests pass locally with my changes

## Code Reuse Verification
- [ ] **Author**: Confirmed I searched directories `promptops/promptops/` and `studio/studio/` to reuse existing YAML/file parsing and UI list helpers (in `utils.py` & `helpers.py`) before submitting.
- [ ] **Reviewer**: Confirmed standard helper patterns are reused and no redundant utility or custom workflows were introduced.
