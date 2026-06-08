---
name: collision-modeling
description: "Build collision risk prediction models using ML and statistical methods, integrated with Bayesian EVT and kinematic simulation outputs."
---

# Collision Modeling

Build collision risk prediction models using machine learning and statistical methods, integrated with Bayesian EVT and kinematic simulation outputs.

## Model Types

| Model | Purpose | Output |
|---|-|-|
| Logistic Regression | Binary collision prediction | P(collision) |
| Random Forest | Multi-class risk classification | Risk level |
| XGBoost | Gradient-boosted risk score | Risk score |
| Neural Network | Complex risk surface | Risk probability |
| Bayesian Model | Uncertainty-aware prediction | P(collision|features) + CI |

## Feature Set (30+ Features)

### Kinematic Features (7)
speed_lead, speed_follow, speed_diff, relative_accel, closing_speed, delta_v, acceleration_ratio

### Distance Features (7)
ttc, mttc, pet, dtc, min_gap, clearance, psd

### Deceleration Features (5)
drac, rla, madr, max_decel, cpi

### Severity Features (4)
delta_v_impact, kinetic_energy, pce, csi

### Probability Features (3)
collision_probability, crash_potential, risk_force

### Scenario Metadata (6)
conflict_type, road_type, road_friction, weather, lighting, number_of_lanes

### Derived Features (3)
speed_ratio, ttc_normalized, gap_normalized

## Feature Selection Methods
- Random forest importance (threshold: > mean)
- Mutual information (threshold: > mean)
- Recursive feature elimination (RFE)

## Model Comparison Framework

```python
compare_models(models, X_test, y_test) → {
  each_model: {
    accuracy, precision, recall, f1, auc_roc,
    confusion_matrix, feature_importance
  }
}
```

## Validation Requirements

### Performance Thresholds
| Metric | Minimum | Target |
|---|-|-|
| Accuracy | ≥ 0.80 | ≥ 0.90 |
| Precision | ≥ 0.75 | ≥ 0.85 |
| Recall | ≥ 0.70 | ≥ 0.85 |
| F1 Score | ≥ 0.75 | ≥ 0.85 |
| AUC-ROC | ≥ 0.80 | ≥ 0.90 |

### Statistical Validation
- Paired t-test or McNemar's test for model comparison
- Report p-values for all comparisons (p < 0.05 required)
- 5-fold cross-validation for model selection
- Leave-one-jurisdiction-out validation for generalization
- Report mean and std of metrics across folds

## Reuse Trigger

Use when:
- Building ML-based collision risk prediction models
- Selecting best model from multiple candidates
- Validating model performance against benchmarks
- Feature engineering for risk prediction

## Cross-Skill Dependencies

- **kinematics-engine** (upstream) — kinematic features feed ML models
- **bayesian-evt** (upstream) — EVT outputs provide Bayesian model inputs
- **stochastic-simulation** (upstream) — Monte Carlo data trains ML models
- **indicator-computation** (upstream) — 42 indicators become features
- **safety-thresholds** (downstream) — ML predictions evaluated against safety thresholds
- **risk-metrics** (downstream) — model outputs feed risk metric computation
- **risk-quantification** (downstream) — ML models integrated into risk pipeline
- **statistical-validation** (sibling) — model validation methods shared

## File Structure (target — when src/risk_models/ package is created)
```
src/risk_models/
├── collision_model.py    Base collision model class
├── logistic_regression.py Logistic regression model
├── random_forest.py       Random forest model
├── xgboost_model.py       XGBoost model
├── neural_network.py      Neural network model
├── bayesian_model.py      Bayesian predictive model
├── ensemble.py            Ensemble model combining multiple
├── validation.py          Model validation metrics
└── benchmarking.py        Compare models against benchmarks
```
