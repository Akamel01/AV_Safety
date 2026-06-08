---
name: run-collision-modeling
description: "Validate the collision-modeling skill — check ML model types, feature set (30+ features), feature selection methods, model comparison framework, and cross-references."
---

# Run: Collision Modeling Validator

Validates the collision modeling skill definition for ML model completeness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/collision-modeling/.claude/skills/run-collision-modeling/driver.py
```

The driver outputs:
- ML model type coverage (5 models)
- Feature set completeness (30+ features across 7 groups)
- Feature selection methods completeness
- Model comparison framework correctness
- Performance thresholds appropriateness
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Collision Modeling Validation ===
ML model types: 5/5 ✓ (logistic, RF, XGBoost, NN, Bayesian)
Feature set: 30/30+ ✓ (7 groups: kinematic, distance, decel, severity, prob, metadata, derived)
Feature selection: 3/3 ✓ (RF importance, MI, RFE)
Model comparison: ✓ (accuracy, precision, recall, f1, AUC-ROC, CM, feature_importance)
Performance thresholds: ✓ (5 metrics with min/target)
Statistical validation: ✓ (paired t-test, McNemar, CV, LOJO, mean+std)
Cross-references:
  kinematics-engine: ✓ (upstream)
  bayesian-evt: ✓ (upstream)
  stochastic-simulation: ✓ (upstream)
  indicator-computation: ✓ (upstream)
  safety-thresholds: ✓ (downstream)
  risk-metrics: ✓ (downstream)
  risk-quantification: ✓ (downstream)
  statistical-validation: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import CollisionModelValidator
validator = CollisionModelValidator()
report = validator.validate()
print(report.summary)
```
