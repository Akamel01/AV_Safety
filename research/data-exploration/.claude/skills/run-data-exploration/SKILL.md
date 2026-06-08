---
name: run-data-exploration
description: "Validate the data-exploration skill — check EDA pipeline completeness, reference implementation correctness, cross-references, and data availability for analysis."
---

# Run: Data Exploration Validator

Validates the EDA pipeline definition in `../SKILL.md` and `references/implementation-details.md`.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt  # if not already installed
```

## Run (agent path)

Execute the EDA validator:

```bash
python3 /Users/akamel/projects/AV_Safety/skills/data-exploration/.claude/skills/run-data-exploration/driver.py
```

The driver outputs:
- Pipeline completeness (all 5 stages defined)
- Reference implementation correctness
- Cross-reference validity against other skills
- Data availability status
- Any gaps or issues found

## Expected output

```
=== Data Exploration Validation ===
EDA pipeline stages: 5/5 defined ✓
Reference implementations: ✓ present with code
Cross-references:
  data-ingest: ✓ (upstream)
  bayesian-analysis: ✓ (downstream)
  risk-metrics: ✓ (downstream)
  scenario-taxonomy: ✓ (taxonomy segmentation)
  stochastic-simulation: ✓ (distribution sampling)
Data availability:
  data/raw/: empty
  data/processed/: empty
  notebooks/: empty
Issues found: 0
```

## Direct invocation

```python
from driver import EDAValidator
validator = EDAValidator()
report = validator.validate()
print(report.summary)
```
