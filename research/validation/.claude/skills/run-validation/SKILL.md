---
name: run-validation
description: "Run the validation pipeline — validate all skills, cross-references, and pipeline results."
---

# Run: Validation Pipeline

Validates the entire AV_Safety portfolio by running all skill validators and producing a unified compliance report.

## Prerequisites

```bash
# Install dependencies
pip install pytest flake8 isort pydocstyle
```

## Run

```bash
python3 /Users/akamel/projects/AV_Safety/skills/validation/.claude/skills/run-validation/driver.py
```

## Expected Output

```
=== Validation Pipeline ===
Skill-level validation: 19/19 skills
Cross-reference validation: 100%
Pipeline integration: PASS
Standards compliance: PASS
Overall: PASS
```

## Direct invocation

```python
from driver import ValidationPipeline
vp = ValidationPipeline()
report = vp.run()
print(report.summary)
```
