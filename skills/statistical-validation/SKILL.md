---
name: statistical-validation
description: "Validate safety claims, model outputs, and analysis results through rigorous statistical testing and hypothesis validation."
---

# Statistical Validation

Validate safety claims, model outputs, and analysis results through rigorous statistical testing and hypothesis validation.

## Validation Framework

### 5 Validation Categories
| Category | Purpose | Methods |
|---|-|-|
| Model Validation | Verify model fits data | Goodness-of-fit, residual analysis, cross-validation |
| Statistical Validation | Test hypotheses about parameters | t-tests, ANOVA, chi-square, KS test |
| Benchmark Validation | Compare against known benchmarks | RMSE, MAPE vs standards |
| Sensitivity Validation | Test robustness to parameters | Sobol indices, Monte Carlo sensitivity |
| Reproducibility Validation | Verify reproducible results | Seed testing, cross-platform checks |

### Pipeline
```
Model/Data/Result → Statistical Tests → Goodness-of-Fit → Benchmark Comparison → Sensitivity → Report
```

## Goodness-of-Fit Tests

- **Kolmogorov-Smirnov:** test data vs distribution
- **Shapiro-Wilk:** normality test (n ≤ 5000); **Anderson-Darling:** for n > 5000
- **Chi-square (binned):** test observed vs expected frequencies
- All must pass (p > 0.05) for model to be considered adequate

## Residual Analysis

```
mean_residual, std_residual, RMSE, MAE, max_abs_residual, normality_test, autocorrelation
```
- Autocorrelation threshold: > 0.2 = significant pattern (should not occur)

## Statistical Hypothesis Tests

### Collision Rate Comparison (pairwise z-test)
```
z = (p1 - p2) / sqrt(p_pool * (1-p_pool) * (1/n1 + 1/n2))
p_pool = (p1*n1 + p2*n2) / (n1 + n2)
```

### Severity Distribution (chi-square)
- Cross-tabulate jurisdiction × severity
- Cramer's V for effect size: small < 0.1, medium < 0.3, large ≥ 0.3

### Homogeneity (chi-square)
- Test if collision rates are homogeneous across jurisdictions

## Benchmark Validation

### Benchmark Database
| Benchmark | Value |
|---|-|
| NHTSA fatal crash rate (per 100M miles) | 1.12 |
| UK fatal road crashes (annual) | 1500 |
| Canada fatal road crashes (annual) | 1800 |
| TTC safe threshold (s) | 2.5 |
| Panic braking max rate (m/s²) | 8.0 |
| Normal braking rate (m/s²) | 3.0 |
| Reaction time mean (s) | 1.5 |
| Friction coefficient (dry) | 0.8 |
| Collision rate merging (per 1000) | 0.02 |
| Collision rate rear-end (per 1000) | 0.03 |
| Collision rate right-angle (per 1000) | 0.01 |

- **Pass:** within 20% of benchmark; **Fail:** > 20% error

## Sensitivity Analysis

### One-at-a-Time (OAT)
- Perturb each parameter ±10% in 5 levels
- Report: sensitivity, elasticity, direction (positive/negative/neutral)

### Sobol Indices
- First-order (S1): individual parameter contribution
- Total-order (ST): total contribution (including interactions)
- Interaction effects: ST - S1

## Validation Report Structure (6 sections)
1. Summary (total tests, passed, failed, overall)
2. Model validation (goodness-of-fit, residual analysis)
3. Hypothesis tests (rate comparisons, severity tests)
4. Benchmark validation (pass/fail per benchmark)
5. Sensitivity analysis (key findings)
6. Key findings (top 3 takeaways)

## Quality Standards

| Criterion | Threshold |
|---|-|
| Significance level | alpha = 0.05 |
| Minimum sample size | n ≥ 30 per group |
| Normality check | Shapiro-Wilk before t-tests |
| Equal variance | Levene's test before ANOVA |
| Goodness-of-fit | All tests pass (p > 0.05) |
| Benchmark comparison | Within 20% of published values |

## Documentation Requirements
- Every test: null hypothesis, alternative, alpha, p-value, conclusion
- Every comparison: test type, assumptions, effect size
- Every validation: criteria, thresholds, pass/fail

## Reuse Trigger

Use when:
- Validating model outputs before deployment
- Testing statistical hypotheses about safety parameters
- Comparing results against published benchmarks
- Generating validation reports for regulatory submission
- Testing sensitivity of key parameters

## File Structure
```
src/statistical_validation/
├── validation_engine.py    Main validation orchestrator
├── goodness_of_fit.py      KS, Shapiro-Wilk, Anderson-Darling, chi-square
├── residual_analysis.py    Residual diagnostics
├── hypothesis_tests.py     t-tests, ANOVA, chi-square, proportion tests
├── benchmark_validation.py Benchmark comparison
├── sensitivity.py          OAT and Sobol sensitivity analysis
├── report_generator.py     Validation report generation
└── validation_report.md    Generated validation report
```
