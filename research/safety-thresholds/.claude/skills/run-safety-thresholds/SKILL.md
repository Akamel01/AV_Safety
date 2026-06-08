---
name: run-safety-thresholds
description: "Validate the safety-thresholds skill — check framework steps, baseline rates, TTC/DRAC thresholds, standards-based thresholds, deployment criteria, and cross-references."
---

# Run: Safety Thresholds Validator

Validates the safety thresholds skill definition for threshold correctness and standards alignment.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/safety-thresholds/.claude/skills/run-safety-thresholds/driver.py
```

The driver outputs:
- Framework step completeness (4 steps)
- Baseline collision rate coverage (3 jurisdictions)
- TTC threshold levels (4 levels)
- DRAC threshold levels (4 levels)
- Standards-based thresholds (UL 4600, ISO 21448)
- Deployment criteria logic correctness
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Safety Thresholds Validation ===
Framework steps: 4/4 ✓ (baseline → acceptable → deployment → validation)
Baseline rates: 3/3 jurisdictions ✓ (USA, Canada, England)
TTC thresholds: 4/4 levels ✓ (critical, dangerous, warning, safe)
DRAC thresholds: 4/4 levels ✓ (emergency, hard, moderate, light)
Standards alignment: ✓ (UL 4600, ISO 21448)
Deployment criteria: ✓ (APPROVED/CONDITIONAL/DENIED with margin)
Continuous monitoring: ✓ (online learning with lambda)
Validation requirements: 5/5 ✓
Cross-references:
  bayesian-evt: ✓ (upstream)
  standards-research: ✓ (upstream)
  risk-metrics: ✓ (sibling)
  risk-quantification: ✓ (downstream)
  portfolio-ui: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import SafetyThresholdValidator
validator = SafetyThresholdValidator()
report = validator.validate()
print(report.summary)
```
