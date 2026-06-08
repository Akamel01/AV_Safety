---
name: run-3d-animation
description: "Validate the 3d-animation skill — check technology stack, core systems, integration points, quality requirements, and cross-references for animation completeness."
---

# Run: 3D Animation Validator

Validates the 3D animation skill definition for rendering and animation completeness.

## Prerequisites

```bash
pip3 install -r /Users/akamel/projects/AV_Safety/requirements.txt
```

## Run (agent path)

```bash
python3 /Users/akamel/projects/AV_Safety/skills/3d-animation/.claude/skills/run-3d-animation/driver.py
```

The driver outputs:
- Technology stack verification (Three.js r160+, post-processing, 2D fallback)
- Core systems completeness (scene manager, vehicle model, lighting, camera, HUD)
- Asset quality specifications
- Integration point coverage
- Quality requirements verification
- Cross-reference completeness
- Any gaps or issues found

## Expected output

```
=== 3D Animation Validation ===
Technology stack: ✓ (Three.js r160+, post-processing, Canvas 2D fallback)
Core systems: 5/5 ✓ (scene, vehicle, lighting, camera, HUD)
Asset quality: ✓ (8 asset types with specs)
Integration inputs: 5/5 ✓ (taxonomy, kinematics, indicators, MC, EVT)
Integration outputs: 4/4 ✓ (3D scene, 2D scene, HUD, plots)
Quality requirements: ✓ (visual, animation, UI)
Cross-references:
  scenario-taxonomy: ✓ (upstream)
  kinematics-engine: ✓ (upstream)
  indicator-computation: ✓ (upstream)
  stochastic-simulation: ✓ (upstream)
  bayesian-evt: ✓ (upstream)
  portfolio-ui: ✓ (downstream)
Issues found: 0
```

## Direct invocation

```python
from driver import AnimationValidator
validator = AnimationValidator()
report = validator.validate()
print(report.summary)
```
