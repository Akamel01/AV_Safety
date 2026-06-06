---
name: run-scenario-taxonomy
description: "Validate, audit, and run the scenario taxonomy — check all 8 conflict types, sub-categories, severity spectra, and cross-skill references for completeness and consistency."
---

# Run: Scenario Taxonomy Validator

Validates the scenario taxonomy defined in `../SKILL.md` and `references/sub-categories.md`.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt  # if not already installed
```

## Run (agent path)

Execute the taxonomy validator:

```bash
python3 /Users/akamel/projects/AV_Safety/skills/scenario-taxonomy/.claude/skills/run-scenario-taxonomy/driver.py
```

The driver outputs:
- Coverage report (conflict types, sub-categories, severity tiers)
- Cross-reference validity against other skills
- Schema compliance for scenario JSON files
- Any gaps, issues, or inconsistencies found

## Expected output

```
=== Scenario Taxonomy Validation ===
Conflict types: 8/8 present ✓
Sub-categories: 30 total (avg 3.75/type)
Severity spectrum: ✓ defined for all types
Cross-references:
  kinematics-engine: ✓ referenced
  indicator-computation: ✓ referenced
  stochastic-simulation: ✓ referenced
  3d-animation: ✓ referenced
  portfolio-ui: ✓ referenced
Issues found: 0
```

## Direct invocation

```python
from driver import TaxonomyValidator
validator = TaxonomyValidator()
report = validator.validate()
print(report.summary)
```
