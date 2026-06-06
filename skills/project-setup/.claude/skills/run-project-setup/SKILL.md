---
name: run-project-setup
description: "Validate the project-setup skill — check setup steps, directory creation, Docker validation, skill count verification, and cross-references."
---

# Run: Project Setup Validator

Validates the project setup skill definition for environment initialization completeness.

## Prerequisites

```bash
# Project setup validation — checks that setup steps are complete
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/project-setup/.claude/skills/run-project-setup/driver.py
```

The driver outputs:
- Setup step coverage (5 steps: pip install, Python env, directories, Docker, skills)
- Directory creation completeness
- Docker validation coverage
- Skill count verification (18 skills)
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Project Setup Validation ===
Setup steps: 5/5 ✓ (pip install, Python verify, directories, Docker, skills check)
Directory creation: ✓ (data/raw, data/processed, docs/standards, docs/research, models, checks, reports)
Docker validation: ✓ (docker + docker-compose version check)
Skill count: 18/18 ✓ (each has SKILL.md + references/)
Cross-references:
  data-ingest: ✓ (downstream)
  portfolio-deploy: ✓ (downstream)
  standards-research: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import SetupValidator
validator = SetupValidator()
report = validator.validate()
print(report.summary)
```
