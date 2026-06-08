---
name: run-stochastic-simulation
description: "Validate the stochastic-simulation skill — check Monte Carlo framework, parameter distributions, adaptive sizing, uncertainty quantification, and cross-references."
---

# Run: Stochastic Simulation Validator

Validates the stochastic simulation skill definition for Monte Carlo completeness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/stochastic-simulation/.claude/skills/run-stochastic-simulation/driver.py
```

The driver outputs:
- Monte Carlo framework completeness
- Parameter distribution coverage (speed, friction, reaction time, etc.)
- Adaptive sample sizing logic correctness
- Uncertainty quantification methods (Wilson CI, bootstrap, Sobol)
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== Stochastic Simulation Validation ===
MC framework: ✓ (5-step loop: sample → validate → run → extract → aggregate)
Parameter distributions: ✓ (speed, friction, reaction, braking, cut-in)
Vehicle speed distributions: 5/5 types ✓
Friction distributions: 5/5 surfaces ✓
Reaction time conditions: 5/5 conditions ✓
Adaptive sizing: ✓ (init 1k → +500/iter → max 50k → CI width <2%)
Uncertainty methods: 3/3 ✓ (Wilson CI, bootstrap, Sobol)
Cross-references:
  scenario-taxonomy: ✓ (upstream)
  kinematics-engine: ✓ (downstream)
  bayesian-evt: ✓ (downstream)
  indicator-computation: ✓ (downstream)
  risk-quantification: ✓ (sibling)
  data-ingest: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import StochSimValidator
validator = StochSimValidator()
report = validator.validate()
print(report.summary)
```
