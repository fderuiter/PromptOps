# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- Deleted the entire `prompts/speculative/` directory (~70 prompt files across ~35 subdirectories). All content was AI-generated hallucinated buzzword prompts with no real human utility — combining unrelated technical and artistic jargon (e.g. "Abyssal-Gothic Liquidity Router", "Byzantine Chromodynamic Flocculation Architect", "Cetacean Origami Sharding", "QCD Chanoyu Autoscaler", etc.). Removed corresponding entry from `prompts/README.md` directory map.

### Added
- `.gitignore` for build artifacts and environments.
- `CONTRIBUTING.md` guide.
- GitHub Issue and Pull Request templates.
- `.pre-commit-config.yaml` for automated validation.
- Duplicate name validation in the unified promptops validation CLI tool.
- `promptops search` for searching prompts.
- `docs/USAGE.md`.
- Integrated last modified timestamp checks into the unified promptops validation CLI tool.

### Changed
- `README.md` with explicit setup and validation instructions.
- Renamed duplicate prompt `E2E Test Discovery Template` to `E2E Test Discovery Lifecycle Template`.
