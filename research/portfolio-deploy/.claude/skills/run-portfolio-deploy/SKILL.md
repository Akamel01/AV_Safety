---
name: run-portfolio-deploy
description: "Validate the portfolio-deploy skill — check deployment targets, CI/CD pipeline, deployment checklist, and cross-references."
---

# Run: Portfolio Deploy Validator

Validates the portfolio deploy skill definition for deployment completeness.

## Prerequisites

```bash
# Deployment skill validation — no Python dependencies needed
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/portfolio-deploy/.claude/skills/run-portfolio-deploy/driver.py
```

The driver outputs:
- Deployment target coverage (portfolio UI, pipeline API, documentation)
- CI/CD pipeline completeness (lint → test → build → deploy)
- Deployment checklist coverage (10 items)
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Portfolio Deploy Validation ===
Deployment targets: 3/3 ✓ (UI, API, docs)
CI/CD pipeline: ✓ (lint → test → build → deploy)
Deployment checklist: 10/10 ✓
Cross-references:
  portfolio-ui: ✓ (upstream)
  risk-quantification: ✓ (upstream)
  standards-research: ✓ (upstream)
  portfolio-ui: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import DeployValidator
validator = DeployValidator()
report = validator.validate()
print(report.summary)
```
