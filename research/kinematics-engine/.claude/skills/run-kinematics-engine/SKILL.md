---
name: run-kinematics-engine
description: "Validate the kinematics-engine skill — check vehicle models, conflict type trajectories, simulation parameters, and cross-references for trajectory computation completeness."
---

# Run: Kinematics Engine Validator

Validates the kinematics engine definition in `../SKILL.md` and `references/` for trajectory computation completeness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/kinematics-engine/.claude/skills/run-kinematics-engine/driver.py
```

The driver outputs:
- Vehicle model completeness (5 models checked)
- Conflict type trajectory definitions (8 types checked)
- Simulation parameter correctness (dt, sub-stepping, accuracy)
- Pedestrian/cyclist parameter validation
- Cross-reference completeness against other skills
- Any gaps or issues found

## Expected output

```
=== Kinematics Engine Validation ===
Vehicle models: 5/5 ✓ (constant velocity, constant accel, Pacejka, bicycle, pedestrian)
Conflict type trajectories: 8/8 ✓
Simulation params: ✓ (dt=10ms, sub-step=4x, accuracy verified)
Pedestrian params: ✓ (stride 0.75m@1.4m/s, reaction 1.0s)
Cyclist params: ✓ (cruising 4-12 m/s, braking 3-5m)
Cross-references:
  scenario-taxonomy: ✓ (upstream)
  indicator-computation: ✓ (downstream)
  stochastic-simulation: ✓ (sibling)
  3d-animation: ✓ (downstream)
  bayesian-evt: ✓ (sibling)
  risk-quantification: ✓ (sibling)
Issues found: 0
```

## Direct invocation

```python
from driver import KinematicsValidator
validator = KinematicsValidator()
report = validator.validate()
print(report.summary)
```
