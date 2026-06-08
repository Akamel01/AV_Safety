---
name: run-risk-quantification
description: "Validate the risk-quantification skill — check pipeline architecture (7 steps), risk scoring formula, report structure, compliance checker, and cross-references."
---

# Run: Risk Quantification Validator

Validates the risk quantification pipeline definition for completeness and correctness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/risk-quantification/.claude/skills/run-risk-quantification/driver.py
```

The driver outputs:
- Pipeline architecture verification (7 steps)
- Risk scoring formula correctness
- Report structure completeness (8 sections)
- Compliance checker logic validation
- Validation requirements completeness
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Risk Quantification Validation ===
Pipeline steps: 7/7 ✓ (kinematics → indicators → MC → EVT → collision → thresholds → portfolio)
Risk scoring: ✓ (4 weights, 4 risk levels)
Report structure: 8/8 sections ✓
Compliance checker: ✓ (FULL/CONDITIONAL/NON_COMPLIANT)
Validation requirements: ✓ (5 checks: steps, NaN, convergence, thresholds, reproducibility)
Cross-references:
  kinematics-engine: ✓ (upstream)
  indicator-computation: ✓ (upstream)
  stochastic-simulation: ✓ (upstream)
  bayesian-evt: ✓ (upstream)
  collision-modeling: ✓ (upstream)
  safety-thresholds: ✓ (upstream)
  portfolio-ui: ✓ (downstream)
  portfolio-deploy: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import RiskQuantValidator
validator = RiskQuantValidator()
report = validator.validate()
print(report.summary)
```
