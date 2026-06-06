---
name: run-bayesian-analysis
description: "Validate the bayesian-analysis skill — check model types, workflow steps, output format completeness, prior elicitation, and cross-references."
---

# Run: Bayesian Analysis Validator

Validates the Bayesian analysis skill definition for model completeness and workflow correctness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/bayesian-analysis/.claude/skills/run-bayesian-analysis/driver.py
```

The driver outputs:
- Model type coverage (5 key models)
- Workflow step completeness (5 steps)
- Output format compliance (5 required elements)
- Prior elicitation coverage
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Bayesian Analysis Validation ===
Model types: 5/5 ✓
Workflow steps: 5/5 ✓
Output format: ✓ (likelihood, priors, diagnostics, PPC, comparison)
Prior elicitation: ✓ (literature + domain expertise)
Cross-references:
  bayesian-evt: ✓ (sibling)
  stochastic-simulation: ✓ (upstream)
  safety-thresholds: ✓ (downstream)
  risk-metrics: ✓ (downstream)
  risk-quantification: ✓ (downstream)
  scenario-taxonomy: ✓ (upstream)
  data-ingest: ✓ (upstream)
Issues found: 0
```

## Direct invocation

```python
from driver import BayesianValidator
validator = BayesianValidator()
report = validator.validate()
print(report.summary)
```
