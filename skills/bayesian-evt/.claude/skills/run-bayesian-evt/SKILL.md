---
name: run-bayesian-evt
description: "Validate the bayesian-evt skill — check GPD model specification, hierarchical structure, MRL threshold selection, validation diagnostics, cross-references, and reference implementation correctness."
---

# Run: Bayesian EVT Validator

Validates the Bayesian Hierarchical EVT pipeline definition in `../SKILL.md` and `references/implementation-details.md`.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt  # if not already installed
```

## Run (agent path)

Execute the EVT validator:

```bash
python3 /Users/akamel/projects/AV_Safety/skills/bayesian-evt/.claude/skills/run-bayesian-evt/driver.py
```

The driver outputs:
- GPD model correctness (formula, parameter constraints)
- Hierarchical structure completeness (4 levels)
- MRL threshold selection method validity
- Validation diagnostics coverage (r-hat, ESS, LOO/WAIC, PPC)
- Prior specifications completeness
- Cross-reference validity against other skills
- Reference implementation correctness (typo checks, PyMC API)
- Any gaps or issues found

## Expected output

```
=== Bayesian EVT Validation ===
GPD model: ✓ correct (formula, parameter constraints)
Hierarchical levels: 4/4 ✓ (scenario, conflict-type, jurisdiction, cross-jurisdiction)
MRL threshold selection: ✓ present with stability analysis
Validation diagnostics: 5/5 (r-hat, ESS, LOO, WAIC, PPC)
Prior specifications: ✓ complete (weakly informative + informative)
Cross-references:
  stochastic-simulation: ✓ (upstream)
  kinematics-engine: ✓ (upstream)
  indicator-computation: ✓ (upstream)
  bayesian-analysis: ✓ (sibling)
  safety-thresholds: ✓ (downstream)
  risk-metrics: ✓ (downstream)
  risk-quantification: ✓ (sibling)
Reference implementation: ✓ (no API typos, GPD likelihood correct)
Issues found: 0
```

## Direct invocation

```python
from driver import EVTValidator
validator = EVTValidator()
report = validator.validate()
print(report.summary)
```
