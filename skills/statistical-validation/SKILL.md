# Skill: Statistical Validation

**Purpose:** Validate safety claims, model outputs, and analysis results through rigorous statistical testing and hypothesis validation.

## 1. Validation Framework

### 1.1 Validation Categories

| Category | Purpose | Methods |
|---|-|-|
| **Model Validation** | Verify model fits data and predictions | Goodness-of-fit, residual analysis, cross-validation |
| **Statistical Validation** | Test hypotheses about safety parameters | t-tests, ANOVA, chi-square, Kolmogorov-Smirnov |
| **Benchmark Validation** | Compare against known benchmarks | Mean error, RMSE, MAPE vs standards |
| **Sensitivity Validation** | Test robustness to parameter changes | Sobol indices, Monte Carlo sensitivity |
| **Reproducibility Validation** | Verify results are reproducible | Seed testing, cross-platform checks |

### 1.2 Validation Pipeline

```
Model/Data/Result
    │
    ▼
┌──────────────┐
│  Statistical  │  (hypothesis tests)
│  Tests        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Goodness-of- │  (fit quality metrics)
│  Fit          │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Benchmark    │  (compare vs known values)
│  Comparison   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Sensitivity   │  (parameter robustness)
│  Analysis      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Report        │  (validation results, pass/fail)
└──────────────┘
```

## 2. Model Validation Tests

### 2.1 Goodness-of-Fit Tests

```python
import numpy as np
from scipy import stats
from scipy.stats import kstest, shapiro, anderson

def goodness_of_fit_test(data: np.ndarray, dist_name: str, alpha: float = 0.05) -> dict:
    """Test if data fits a given distribution."""
    # Fit distribution parameters
    dist = getattr(stats, dist_name)
    params = dist.fit(data)
    
    # Kolmogorov-Smirnov test
    ks_stat, ks_p = kstest(data, dist_name, args=params)
    
    # Shapiro-Wilk test (normality)
    if len(data) <= 5000:
        sw_stat, sw_p = shapiro(data)
    else:
        # Use Anderson-Darling for larger samples
        ad_result = anderson(data)
        sw_p = ad_result.statistic > np.percentile(ad_result.critical_values, 95)
    
    # Chi-square test (binned)
    observed, bin_edges = np.histogram(data, bins='auto', density=False)
    expected = dist.cdf(bin_edges[:-1], *params)
    expected = np.diff(expected) * len(data)
    chi2_stat, chi2_p = stats.chisquare(observed, expected)
    
    results = {
        "distribution": dist_name,
        "params": params,
        "KS_test": {"statistic": ks_stat, "p_value": ks_p, "pass": ks_p > alpha},
        "shapiro_test": {"statistic": sw_stat, "p_value": sw_p, "pass": sw_p > alpha},
        "chi2_test": {"statistic": chi2_stat, "p_value": chi2_p, "pass": chi2_p > alpha},
        "overall_pass": all([ks_p > alpha, sw_p > alpha, chi2_p > alpha]),
        "n_samples": len(data)
    }
    
    return results
```

### 2.2 Residual Analysis

```python
def analyze_residuals(observed: np.ndarray, predicted: np.ndarray) -> dict:
    """Analyze residuals for model fit quality."""
    residuals = observed - predicted
    
    results = {
        "mean_residual": np.mean(residuals),
        "std_residual": np.std(residuals),
        "RMSE": np.sqrt(np.mean(residuals**2)),
        "MAE": np.mean(np.abs(residuals)),
        "max_abs_residual": np.max(np.abs(residuals)),
        "normality_test": shapiro(residuals) if len(residuals) <= 5000 else None,
        "autocorrelation": np.correlate(residuals, residuals, mode='full') / np.var(residuals)
    }
    
    # Check for patterns in residuals
    if results["autocorrelation"][len(residuals):len(residuals)+1] > 0.2:
        results["has_autocorrelation"] = True
    else:
        results["has_autocorrelation"] = False
    
    return results
```

## 3. Statistical Hypothesis Tests

### 3.1 Collision Rate Comparison (USA vs Canada vs England)

```python
def compare_collision_rates(rates: dict, jurisdictions: list, alpha: float = 0.05) -> dict:
    """Compare collision rates across jurisdictions using proportion tests."""
    results = {}
    
    # Pairwise comparisons
    for i in range(len(jurisdictions)):
        for j in range(i+1, len(jurisdictions)):
            jur1 = jurisdictions[i]
            jur2 = jurisdictions[j]
            n1 = rates[jur1]["n_trials"]
            p1 = rates[jur1]["rate"]
            n2 = rates[jur2]["n_trials"]
            p2 = rates[jur2]["rate"]
            
            # Two-proportion z-test
            p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
            z_stat = (p1 - p2) / np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            
            results[f"{jur1}_vs_{jur2}"] = {
                "z_statistic": z_stat,
                "p_value": p_value,
                "significant": p_value < alpha,
                "confidence_interval": _proportion_diff_ci(p1, p2, n1, n2, alpha)
            }
    
    # ANOVA-like test across all jurisdictions
    if len(jurisdictions) > 2:
        chi2_stat, chi2_p = _chi2_homogeneity_test(rates, jurisdictions)
        results["homogeneity_test"] = {
            "chi2_statistic": chi2_stat,
            "p_value": chi2_p,
            "significant": chi2_p < alpha
        }
    
    return results

def _proportion_diff_ci(p1, p2, n1, n2, alpha: float = 0.05) -> tuple:
    """Confidence interval for difference in proportions."""
    z = stats.norm.ppf(1 - alpha/2)
    se = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    diff = p1 - p2
    margin = z * se
    return (diff - margin, diff + margin)

def _chi2_homogeneity_test(rates: dict, jurisdictions: list) -> tuple:
    """Test if collision rates are homogeneous across jurisdictions."""
    observed = np.array([rates[j]["n_collisions"] for j in jurisdictions])
    total = np.array([rates[j]["n_trials"] for j in jurisdictions])
    expected = np.array([rate * trial for rate, trial in zip(observed / total, total)])
    return stats.chisquare(observed, expected)
```

### 3.2 Severity Distribution Comparison

```python
def compare_severity_distributions(df: pd.DataFrame, severity_col: str = "severity_level") -> dict:
    """Compare severity distributions across jurisdictions using chi-square test."""
    cross_tab = pd.crosstab(df["jurisdiction"], df[severity_col])
    
    # Chi-square test
    chi2, p, dof, expected = stats.chisquare(cross_tab.values.flatten(), ddof=len(cross_tab.columns))
    
    # Cramer's V for effect size
    n = cross_tab.sum().sum()
    min_dim = min(cross_tab.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim))
    
    return {
        "chi2_statistic": chi2,
        "p_value": p,
        "degrees_of_freedom": dof,
        "cramers_v": cramers_v,
        "significant": p < 0.05,
        "effect_size": "small" if cramers_v < 0.1 else "medium" if cramers_v < 0.3 else "large",
        "contingency_table": cross_tab.to_dict()
    }
```

## 4. Benchmark Validation

### 4.1 Benchmark Database

```python
BENCHMARKS = {
    "NHTSA_fatal_crash_rate_per_100M_miles": 1.12,  # approximate 2020 value
    "NHTSA_fatal_vehicle_miles_traveled": 3.22,  # billion vehicle miles per 100M
    "UK_fatal_road_crashes_annual": 1500,  # approximate
    "Canada_fatal_road_crashes_annual": 1800,  # approximate
    "average_TTC_safe_threshold": 2.5,  # seconds
    "panic_braking_max_rate": 8.0,  # m/s²
    "normal_braking_rate": 3.0,  # m/s²
    "reaction_time_mean": 1.5,  # seconds
    "reaction_time_std": 0.5,  # seconds
    "friction_coefficient_dry": 0.8,  # average
    "collision_rate_merging_typical": 0.02,  # per 1000 conflicts
    "collision_rate_rear_end_typical": 0.03,  # per 1000 conflicts
    "collision_rate_right_angle_typical": 0.01,  # per 1000 conflicts
}

def validate_against_benchmarks(model_results: dict) -> dict:
    """Validate model results against published benchmarks."""
    results = {}
    
    for benchmark_name, benchmark_value in BENCHMARKS.items():
        if benchmark_name in model_results:
            model_value = model_results[benchmark_name]
            relative_error = abs(model_value - benchmark_value) / benchmark_value
            
            results[benchmark_name] = {
                "benchmark_value": benchmark_value,
                "model_value": model_value,
                "relative_error": relative_error,
                "within_10pct": relative_error < 0.10,
                "within_20pct": relative_error < 0.20,
                "status": "pass" if relative_error < 0.20 else "fail"
            }
    
    return results
```

## 5. Sensitivity Analysis

### 5.1 One-at-a-Time (OAT) Sensitivity

```python
def sensitivity_analysis_oat(model_fn, param_name: str, param_base: float, 
                            delta: float = 0.1, n_levels: int = 5) -> dict:
    """Perform one-at-a-time sensitivity analysis."""
    results = {}
    
    # Create perturbations
    perturbations = np.linspace(param_base * (1 - delta), param_base * (1 + delta), n_levels)
    outputs = [model_fn(**{param_name: p}) for p in perturbations]
    
    # Compute sensitivity indices
    outputs = np.array(outputs)
    param_range = perturbations[-1] - perturbations[0]
    output_range = outputs.max() - outputs.min()
    
    results = {
        "parameter": param_name,
        "base_value": param_base,
        "parameter_range": [perturbations[0], perturbations[-1]],
        "output_range": [outputs.min(), outputs.max()],
        "sensitivity": output_range / param_range if param_range > 0 else 0,
        "elasticity": (output_range / outputs.mean()) / (param_range / param_base) if outputs.mean() != 0 and param_base != 0 else 0,
        "direction": "positive" if outputs[-1] > outputs[0] else "negative" if outputs[-1] < outputs[0] else "neutral"
    }
    
    return results
```

### 5.2 Sobol Sensitivity Indices

```python
def sobol_sensitivity(model_fn, param_bounds: dict, n_samples: int = 10000) -> dict:
    """Compute Sobol sensitivity indices using Saltelli sampling."""
    param_names = list(param_bounds.keys())
    n_params = len(param_names)
    
    # Generate Saltelli sample
    S = saltelli.sample(problem={"num_vars": n_params, "names": param_names, "bounds": list(param_bounds.values())}, n=n_samples)
    
    # Run model for each sample
    outputs = np.array([model_fn(**dict(zip(param_names, row))) for row in S])
    
    # Compute Sobol indices
    Si = analyze({"num_vars": n_params, "names": param_names, "bounds": list(param_bounds.values())}, outputs, print_to_console=False)
    
    return {
        "first_order": Si["S1"],
        "total_order": Si["ST"],
        "interaction_effects": {
            param_names[i]: Si["ST"][i] - Si["S1"][i] 
            for i in range(n_params)
        }
    }
```

## 6. Validation Report

### 6.1 Report Structure

```markdown
# Statistical Validation Report

## 1. Summary
- Total tests: {n_tests}
- Passed: {n_passed}
- Failed: {n_failed}
- Overall: {"PASS" if n_failed == 0 else "FAIL"}

## 2. Model Validation
### 2.1 Goodness-of-Fit
{goodness_of_fit_results}

### 2.2 Residual Analysis
{residual_analysis_results}

## 3. Hypothesis Tests
### 3.1 Collision Rate Comparisons
{rate_comparison_results}

### 3.2 Severity Distribution Tests
{severity_test_results}

## 4. Benchmark Validation
{benchmark_validation_results}

## 5. Sensitivity Analysis
{sensitivity_results}

## 6. Key Findings
1. {finding_1}
2. {finding_2}
3. {finding_3}
```

## 7. Validation Requirements

### 7.1 Statistical Rigor
- **All tests** report p-values and effect sizes
- **All comparisons** use appropriate statistical tests (parametric vs non-parametric)
- **All models** pass goodness-of-fit tests at alpha = 0.05
- **All benchmarks** within 20% of published values

### 7.2 Documentation
- Every test: null hypothesis, alternative, alpha, p-value, conclusion
- Every comparison: test type, assumptions, effect size
- Every validation: criteria, thresholds, pass/fail

### 7.3 Quality Standards
- **Significance level:** alpha = 0.05 (default)
- **Minimum sample size:** n ≥ 30 for each group
- **Normality check:** Shapiro-Wilk before t-tests
- **Equal variance check:** Levene's test before ANOVA
