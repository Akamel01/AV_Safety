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

## File Structure
```
src/risk_quantification/
├── pipeline.py              Main pipeline orchestrator
├── scenario_runner.py       Run individual scenarios
├── batch_runner.py          Run all scenarios
├── results_aggregator.py    Aggregate results
├── risk_report_generator.py Generate risk reports
├── threshold_checker.py     Compare against safety thresholds
├── output_formats/
│   ├── json_export.py       Export to JSON
│   ├── csv_export.py        Export to CSV
│   └── markdown_report.py   Generate markdown report
└── validation/
    └── pipeline_validation.py Validate pipeline outputs
```
