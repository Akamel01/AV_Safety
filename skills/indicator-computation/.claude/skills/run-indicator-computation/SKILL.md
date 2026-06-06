---
name: run-indicator-computation
description: "Validate the indicator-computation skill — check all 42 indicators across 6 categories, applicability matrices, vehicle dimensions, friction coefficients, and cross-references."
---

# Run: Indicator Computation Validator

Validates the indicator computation skill definition for completeness of all 42 indicators across 6 categories.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/indicator-computation/.claude/skills/run-indicator-computation/driver.py
```

The driver outputs:
- Indicator count by category (6 categories, 42 indicators)
- Applicability matrix coverage (all conflict types)
- Vehicle dimension data correctness
- Friction coefficient data coverage
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Indicator Computation Validation ===
Categories: 6/6 ✓
Total indicators: 42/42 ✓
  Time-based: 11 ✓
  Distance-based: 5 ✓
  Deceleration-based: 8 ✓
  Kinematic: 5 ✓
  Severity: 6 ✓
  Probability: 6 ✓
Vehicle dimensions: ✓ (6 types from NHTSA)
Friction coefficients: ✓ (4 surfaces)
Cross-references:
  kinematics-engine: ✓ (upstream)
  scenario-taxonomy: ✓ (upstream)
  stochastic-simulation: ✓ (downstream)
  bayesian-evt: ✓ (downstream)
  risk-quantification: ✓ (downstream)
  risk-metrics: ✓ (sibling)
  3d-animation: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import IndicatorValidator
validator = IndicatorValidator()
report = validator.validate()
print(report.summary)
```
