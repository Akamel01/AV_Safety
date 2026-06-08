---
name: validation
description: "End-to-end validation pipeline for the AV_Safety portfolio — orchestrates checks across all skills and validates results against international standards."
---

# Validation Pipeline

End-to-end validation for the AV_Safety portfolio. Orchestrates checks across all upstream skills and produces a unified compliance report.

## Validation Layers

| Layer | Scope | Source Skill |
|---|---|---|
| Skill-level | Each skill's structure (driver, references, subskill) | Each individual skill |
| Integration | Cross-skill dependency graph | skill-deps (above) |
| Pipeline | Full end-to-end scenario run | risk-quantification |
| Standards | Alignment with UL 4600, ISO 21448, ISO 26262 | standards-research |

## Validation Checkpoints

```
skill-check → dep-check → pipeline-run → standards-compliance → report
```

## Checklist

- [ ] All 19 skills have driver.py
- [ ] All skills have references/ directory
- [ ] All skills have .claude/skills/run-{name}/SKILL.md subskill
- [ ] Cross-skill dependency graph is consistent
- [ ] End-to-end scenario runs without error
- [ ] Results align with international safety standards
- [ ] Monte Carlo convergence achieved
- [ ] Bayesian EVT posterior is well-formed
- [ ] Threshold checks pass for all jurisdictions
- [ ] Test coverage >= 80%

## Cross-Skill Dependencies

- **statistical-validation** (upstream) — statistical test framework used by this skill
- **safety-thresholds** (upstream) — threshold definitions used in compliance checks
- **risk-quantification** (upstream) — pipeline results validated here
- **standards-research** (upstream) — standards definitions used in compliance section
- **collision-modeling** (upstream) — collision predictions validated
- **indicator-computation** (upstream) — 42 indicators validated
- **kinematics-engine** (upstream) — kinematic results validated
- **bayesian-evt** (upstream) — EVT results validated
- **portfolio-ui** (downstream) — visualization depends on validated data

## Output

Validation produces:
- A pass/fail report per skill
- A combined compliance score (0-100)
- Detailed findings for any failures
- Recommendations for fixes
