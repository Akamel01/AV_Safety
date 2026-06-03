# Detailed Bayesian EVT Implementation

## PyMC Model Specification

```python
import pymc as pm
import arviz as az
import numpy as np

def build_bayesian_evt_model(extreme_values, scenario_ids, conflict_type_ids, jurisdiction_ids):
    with pm.Model() as model:
        # Global hyperpriors
        mu_xi_global = pm.Normal("mu_xi_global", mu=0, sigma=1)
        sigma_xi_global = pm.HalfNormal("sigma_xi_global", sigma=1)
        mu_sigma_global = pm.HalfNormal("mu_sigma_global", sigma=2)
        sigma_sigma_global = pm.HalfNormal("sigma_sigma_global", sigma=1)
        
        # Conflict-type level
        xi_conflict = pm.Normal("xi_conflict", mu=mu_xi_global, sigma=sigma_xi_global,
                                shape=len(np.unique(conflict_type_ids)))
        sigma_conflict = pm.HalfNormal("sigma_conflict", mu=mu_sigma_global, sigma=sigma_sigma_global,
                                       shape=len(np.unique(conflict_type_ids)))
        
        # Scenario level (nested within conflict type)
        xi_scenario = pm.Normal("xi_scenario", mu=xi_conflict[conflict_type_ids], sigma=0.1,
                                shape=len(np.unique(scenario_ids)))
        sigma_scenario = pm.HalfNormal("sigma_scenario", mu=sigma_conflict[conflict_type_ids], sigma=0.1,
                                       shape=len(np.unique(scenario_ids)))
        
        # Jurisdiction level
        xi_jurisdiction = pm.Normal("xi_jurisdiction", mu=xi_conflict[conflict_type_ids], sigma=0.05,
                                    shape=len(np.unique(jurisdiction_ids)))
        
        # GPD likelihood
        xi_obs = xi_scenario[scenario_ids]
        sigma_obs = sigma_scenario[conflict_type_ids]
        pm.GPD("likelihood", xi=xi_obs, sigma=sigma_obs, observed=extreme_values)
    
    return model
```

## Sampling and Diagnostics

```python
# Sample from posterior
trace = pm.sample(draws=4000, tune=2000, chains=4, target_accept=0.95)

# Diagnostics
az.plot_trace(trace, var_names=["xi_conflict", "sigma_conflict"])
az.rhat(trace)           # must be < 1.01
az.ess(trace)            # must be > 400
az.loo(trace)            # LOO for model comparison
az.waic(trace)           # WAIC alternative
```

## Posterior Predictive Check

```python
post_pred = pm.sample_posterior_predictible(trace, var_names=["likelihood"])
observed = trace.posterior["likelihood"].mean(dim=["chain", "sample"]).values
predicted = post_pred["likelihood"].mean(dim=["chain", "sample"]).values

import matplotlib.pyplot as plt
plt.plot(np.sort(observed), label="Observed")
plt.plot(np.sort(predicted), label="Predicted", alpha=0.5)
plt.legend()
plt.xlabel("Excess value")
plt.ylabel("CDF")
plt.title("Posterior Predictive Check")
```

## Cross-Jurisdiction Comparison

```python
def compare_jurisdictions(trace, collision_threshold=2.0, u_threshold=1.5):
    results = {}
    for jur in ["USA", "Canada", "England"]:
        xi_j = trace.posterior["xi_jurisdiction"].sel(jurisdiction=jur)
        sigma_j = trace.posterior["sigma_jurisdiction"].sel(jurisdiction=jur)
        threshold_excess = collision_threshold - u_threshold
        p_collision = (1 + xi_j * threshold_excess / sigma_j) ** (-(1/xi_j + 1))
        results[jur] = {
            "xi": xi_j.median().values,
            "sigma": sigma_j.median().values,
            "collision_rate": p_collision.median().values,
            "ci95": p_collision.quantile([0.025, 0.975]).values
        }
    return results
```

## MRL Threshold Selection (Detailed)

```python
def mrl_threshold_selection(excesses, delta=0.05):
    """
    Method:
    1. Sort extreme values in descending order
    2. For each u_i, compute mean of (X - u_i) for all X > u_i
    3. Plot e(u) vs u: linear for large u when GPD valid
    4. Threshold = first point where linearity begins
    """
    sorted_vals = np.sort(excesses)[::-1]  # descending
    
    mrl_values = []
    thresholds = []
    
    for i, u in enumerate(sorted_vals):
        excess_above = excesses[excesses > u] - u
        if len(excess_above) < 10:  # minimum count
            break
        e_u = np.mean(excess_above)
        mrl_values.append(e_u)
        thresholds.append(u)
    
    # Find linearity break point
    # Compute slope between consecutive points
    slopes = np.diff(mrl_values) / np.diff(thresholds)
    
    # Threshold = first point where slope stabilizes
    for i in range(1, len(slopes)):
        if abs(slopes[i] - slopes[i-1]) / abs(slopes[i-1]) < delta:
            return thresholds[i], thresholds[:i+1], mrl_values[:i+1]
    
    return thresholds[0], thresholds, mrl_values

def stability_analysis(extremes, u, delta=0.05):
    """Check if GPD parameters are stable at neighboring thresholds."""
    from scipy import stats
    
    for test_u in [u - delta, u, u + delta]:
        excesses = extremes[extremes > test_u] - test_u
        if len(excesses) < 20:
            continue
        # Fit GPD
        xi_hat, sigma_hat = stats.genn.fit(excesses, floc=test_u)
        # Store for comparison
    # Return stability: True if parameters overlap within CI
```

## QQ-Plot Validation

```python
def qq_plot_validation(extremes, xi, sigma, threshold):
    """Transform data and compare empirical vs GPD quantiles."""
    # Transform: F(u + x) = (1 + ξ·x/σ)^(-(1/ξ + 1))
    if xi != 0:
        gpd_quantiles = np.power(1 + xi * (extremes - threshold) / sigma, -(1/xi + 1))
    else:
        gpd_quantiles = 1 - np.exp(-(extremes - threshold) / sigma)
    
    # Empirical CDF
    emp_cdf = (np.argsort(np.argsort(extremes)) + 1) / len(extremes)
    
    import matplotlib.pyplot as plt
    plt.plot(emp_cdf, gpd_quantiles, 'o', alpha=0.5)
    plt.plot([0, 1], [0, 1], 'r--')  # 45° line
    plt.xlabel("Empirical CDF")
    plt.ylabel("GPD Quantiles")
    plt.title("QQ-Plot Validation")
```

## Data Sources by Jurisdiction

| Jurisdiction | Data Source | Relevant Standards |
|---|-|-|
| USA | NHTSA FARS, NHTSA CISS, NASS-CRS | NHTSA AV Safety Framework, FMVSS |
| Canada | Transport Canada, CMFwiki Canada, ICBC | Transport Canada AV guidelines |
| England | DfT GB Road Casualties, JACArP, Highways England | UK AV Standards, JCTC guidance |
