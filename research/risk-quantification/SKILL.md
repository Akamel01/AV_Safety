---
name: risk-quantification
description: "Build end-to-end risk quantification pipeline integrating kinematics, Monte Carlo, Bayesian EVT, collision modeling, and safety thresholds."
---

# Risk Quantification

End-to-end risk quantification pipeline integrating all previous skills: collision modeling, Bayesian EVT, safety thresholds, and portfolio visualization.

## Pipeline Architecture (7 Steps)

```
Scenarios
  ↓ Kinematics (trajectory computation)
  ↓ Indicators (42 computed indicators)
  ↓ Monte Carlo (simulation + parameter sampling)
  ↓ Bayesian EVT (GPD fitting + posterior)
  ↓ Collision Modeling (ML prediction + uncertainty)
  ↓ Safety Thresholds (threshold comparison)
  ↓ Portfolio (UI + visualization)
```

## Risk Scoring Formula

```python
weights = {
    "collision_rate": 0.3,
    "severity": 0.3,
    "uncertainty": 0.2,
    "threshold_compliance": 0.2
}

risk_score = (
    weights["collision_rate"] * mc_results["collision_rate"] +
    weights["severity"] * bayesian_results["severity_score"] +
    weights["uncertainty"] * (1 - bayesian_results["confidence"]) +
    weights["threshold_compliance"] * (1 - threshold_results["margin_percent"])
)

risk_level = (
    "LOW" if risk_score < 0.2 else
    "MEDIUM" if risk_score < 0.5 else
    "HIGH" if risk_score < 0.8 else
    "CRITICAL"
)
```

## Report Structure (8 Sections)
1. Executive summary (total scenarios, overall risk level, deployment recommendation)
2. Methodology (kinematic model, simulation method, Bayesian model, ML models, thresholds)
3. Scenario results (collision rate, severity, TTC/DRAC distributions, GPD fit, safety margin)
4. Cross-scenario analysis (conflict type comparison, jurisdiction comparison, severity distribution)
5. Threshold analysis (safe thresholds, deployment readiness)
6. Recommendations
7. Uncertainty analysis (primary source, confidence level, sensitivity)
8. Appendices (parameter specs, model validation, data sources, computational details)

## Compliance Checker

```python
compliance_level = (
    "FULL" if collision_rate < safe_threshold else
    "CONDITIONAL" if collision_rate < deployment_threshold else
    "NON_COMPLIANT"
)
required_improvement = max(0, (collision_rate - safe_threshold) / collision_rate * 100)
```

## Output Formats
- **JSON:** Per-scenario results (scenario, MC, Bayesian EVT, thresholds)
- **CSV:** Flat table (scenario_id, conflict_type, jurisdiction, collision_rate, n_collisions, severity_mean, safety_margin, compliance)

## Validation Requirements

| Check | Method | Pass Condition |
|---|-|-|
| All steps complete | Step execution log | 100% completion |
| No NaN outputs | Value check | No NaN in results |
| Convergence achieved | R-hat, ESS | R-hat < 1.01, ESS > 400 |
| Threshold compliance | Comparison | All scenarios evaluated |
| Reproducibility | Seed testing | Same results with same seed |

- Minimum scenarios: ≥ 16 (2 per conflict type)
- Minimum Monte Carlo samples: ≥ 10,000 per scenario
- Bayesian convergence: R-hat < 1.01, ESS > 400
- Statistical power: ≥ 0.80 for significance tests
- Uncertainty bounds: 95% CI reported for all estimates

## Reuse Trigger

Use when:
- Running complete risk quantification pipeline
- Generating risk reports for portfolio
- Checking compliance against safety thresholds
- Exporting results in multiple formats

## Cross-Skill Dependencies

- **kinematics-engine** (upstream) — trajectories feed pipeline step 1
- **indicator-computation** (upstream) — 42 indicators feed pipeline step 2
- **stochastic-simulation** (upstream) — Monte Carlo engine feeds pipeline step 3
- **bayesian-evt** (upstream) — GPD/EVT analysis feeds pipeline step 4
- **collision-modeling** (upstream) — ML models feed pipeline step 5
- **safety-thresholds** (upstream) — threshold definitions feed pipeline step 6
- **portfolio-ui** (downstream) — pipeline results drive portfolio visualization
- **portfolio-deploy** (downstream) — pipeline outputs deployed to portfolio

## File Structure (actual — matches `src/risk_quantification/`)
```
src/risk_quantification/
├── pipeline.py              Main pipeline orchestrator (7-step pipeline)
├── risk_scoring.py          Risk scoring with GPD integration
├── threshold_checker.py     Threshold compliance checking
├── results_aggregator.py    Aggregate results across scenarios
├── report_generator.py      Generate risk reports
├── output_formats.py        JSON, CSV, Markdown exporters
├── pipeline_validation.py   Validate pipeline outputs
└── output_formats/          (submodule directory)
└── validation/              (submodule directory)
```
