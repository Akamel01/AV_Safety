# Skill: Bayesian Hierarchical EVT

**Purpose:** Quantify collision risk (occurrence likelihood and severity) using Bayesian Hierarchical Extreme Value Theory, integrated with the kinematics engine, indicator computation, and stochastic simulation.

## 1. EVT Framework Overview

### 1.1 Core Theory

Extreme Value Theory (EVT) models the tail behavior of distributions — exactly what we need for collision risk, where rare extreme events (very low TTC, very high DRAC) matter most.

**Two EVT approaches for collision risk:**

1. **Block Maxima → Generalized Extreme Value (GEV)** — model minimum TTC over fixed time blocks
2. **Peaks-over-Threshold → Generalized Pareto (GPD)** — model all values exceeding threshold ✅

We use GPD because it's more data-efficient and directly applicable to traffic conflicts.

### 1.2 GPD Model

```
For excesses X - u > 0 over threshold u:

f(x; ξ, σ) = (1/σ) · (1 + ξ(x-u)/σ)^(-(1/ξ + 1))

where:
  ξ = shape parameter (tail heaviness)
  ξ > 0: heavy-tailed (Pareto type) — extreme events possible
  ξ = 0: exponential (Gumbel type) — light-tailed
  ξ < 0: bounded (Weibull type) — upper bound exists
  σ = scale parameter (spread)
  u = threshold
```

### 1.3 Hierarchical Structure

```
Level 1 (Scenario): θ_s = {ξ_s, σ_s} ~ GPD parameters for scenario s
                    ξ_s ~ Normal(ξ_hyper, τ_ξ)
                    σ_s ~ HalfNormal(τ_σ)

Level 2 (Conflict Type): ξ_hyper_k ~ Normal(μ_ξ, ρ_ξ)
                         σ_hyper_k ~ HalfNormal(ρ_σ)

Level 3 (Jurisdiction): μ_ξ_j ~ Prior
                         ρ_ξ_j ~ Prior

Level 4 (Cross-Jurisdiction): Global hyperpriors on jurisdiction parameters
```

### 1.4 Collision Rate Estimation

```
P(collision | collision_threshold) = P(TTC < TTC_threshold | GPD)

For GPD: P(X - u > x) = (1 + ξ·x/σ)^(-(1/ξ + 1))

Collision probability:
  P_collision = P(exceedance) × P(TTC < TTC_threshold | exceedance)
             = (1 - F(u)) × (1 + ξ·(TTC_threshold - u)/σ)^(-(1/ξ + 1))

where F(u) is the CDF of the parent distribution at threshold u
```

### 1.5 Collision Severity Estimation

```
Severity | Collision ~ GPD(ξ_sev, σ_sev)

Parameters modeled from:
  - ΔV at impact (from kinematics)
  - Impact angle (from relative direction)
  - Vehicle mass ratio
  - Occupant protection level

Severity index: S = δ · f(ΔV, θ, μ_mass, μ_protect)

where δ scales the energy transfer, f maps to injury severity
```

## 2. Mean Residual Life Threshold Selection

### 2.1 Method

```
For each candidate threshold u:
  e(u) = E[X - u | X > u] = estimated mean excess

Plot e(u) vs u:
  - If GPD is valid: e(u) ≈ u/ξ + const (linear for large u)
  - Threshold = first point where linearity begins

Implementation:
  1. Sort extreme values in descending order
  2. For each u_i, compute mean of (X - u_i) for all X > u_i
  3. Compute bootstrap confidence bands
  4. Threshold = argmin_u |slope(e(u)) - slope(e(u+δ))|
```

### 2.2 Stability Analysis

```
For threshold u and neighboring thresholds [u-δ, u, u+δ]:
  1. Fit GPD at each
  2. Check if ξ and σ are stable (overlap within CI)
  3. If stable: u is valid
  4. If not: increase u and repeat
```

### 2.3 QQ-Plot Validation

```
1. Fit GPD at selected threshold
2. Transform data: F(u + x) = (1 + ξ·x/σ)^(-(1/ξ + 1))
3. Plot empirical quantiles vs GPD quantiles
4. If points fall on 45° line: GPD fits well
```

## 3. PyMC Implementation

### 3.1 Model Specification

```python
import pymc as pm
import arviz as az
import numpy as np

def build_bayesian_evt_model(
    extreme_values: np.ndarray,  # excesses over threshold
    scenario_ids: np.ndarray,     # which scenario each excess belongs to
    conflict_type_ids: np.ndarray,  # which conflict type
    jurisdiction_ids: np.ndarray,   # which jurisdiction
):
    with pm.Model() as model:
        # Global hyperpriors
        mu_xi_global = pm.Normal("mu_xi_global", mu=0, sigma=1)
        sigma_xi_global = pm.HalfNormal("sigma_xi_global", sigma=1)
        
        mu_sigma_global = pm.HalfNormal("mu_sigma_global", sigma=2)
        sigma_sigma_global = pm.HalfNormal("sigma_sigma_global", sigma=1)
        
        # Conflict-type level
        xi_conflict = pm.Normal(
            "xi_conflict",
            mu=mu_xi_global,
            sigma=sigma_xi_global,
            shape=len(np.unique(conflict_type_ids))
        )
        sigma_conflict = pm.HalfNormal(
            "sigma_conflict",
            mu=mu_sigma_global,
            sigma=sigma_sigma_global,
            shape=len(np.unique(conflict_type_ids))
        )
        
        # Scenario level (nested within conflict type)
        xi_scenario = pm.Normal(
            "xi_scenario",
            mu=xi_conflict[conflict_type_ids],
            sigma=0.1,
            shape=len(np.unique(scenario_ids))
        )
        sigma_scenario = pm.HalfNormal(
            "sigma_scenario",
            mu=sigma_conflict[conflict_type_ids],
            sigma=0.1,
            shape=len(np.unique(scenario_ids))
        )
        
        # Jurisdiction level (for cross-jurisdiction analysis)
        xi_jurisdiction = pm.Normal(
            "xi_jurisdiction",
            mu=xi_conflict[conflict_type_ids],
            sigma=0.05,
            shape=len(np.unique(jurisdiction_ids))
        )
        
        # GPD likelihood
        xi_obs = xi_scenario[scenario_ids]
        sigma_obs = sigma_scenario[conflict_type_ids]
        
        pm.GPD(
            "likelihood",
            xi=xi_obs,
            sigma=sigma_obs,
            observed=extreme_values
        )
    
    return model
```

### 3.2 Sampling

```python
# Sample from posterior
trace = pm.sample(
    draws=4000,
    tune=2000,
    chains=4,
    target_accept=0.95,  # higher for HMC convergence
    progressbar=True
)

# Diagnostics
az.plot_trace(trace, var_names=["xi_conflict", "sigma_conflict"])
az.rhat(trace)           # must be < 1.01 for convergence
az.ess(trace)            # must be > 400 for adequate samples
az.loo(trace)            # LOO for model comparison
az.waic(trace)           # WAIC alternative
```

### 3.3 Posterior Predictive Check

```python
# Check if model fits the data
post_pred = pm.sample_posterior_predictive(trace, var_names=["likelihood"])

# Plot observed vs predicted distribution
observed = trace.posterior["likelihood"].mean(dim=["chain", "sample"]).values
predicted = post_pred["likelihood"].mean(dim=["chain", "sample"]).values

# Compare CDFs
import matplotlib.pyplot as plt
plt.plot(np.sort(observed), label="Observed")
plt.plot(np.sort(predicted), label="Predicted", alpha=0.5)
plt.legend()
plt.xlabel("Excess value")
plt.ylabel("CDF")
plt.title("Posterior Predictive Check")
```

## 4. Bayesian Hierarchical Structure by Jurisdiction

### 4.1 Jurisdiction Mapping

| Jurisdiction | Data Source | Relevant Standards |
|---|---|---|
| **USA** | NHTSA FARS, NHTSA CISS, NASS-CRS | NHTSA AV Safety Framework, FMVSS |
| **Canada** | Transport Canada, CMFwiki Canada, ICBC | Transport Canada AV guidelines |
| **England** | DfT GB Road Casualties, JACArP, Highways England | UK AV Standards, JCTC guidance |

### 4.2 Hierarchical Model

```
Global hyperpriors
    ├── μ_ξ (global shape mean)
    └── μ_σ (global scale mean)
    
    Conflict-type level (8 types)
        ├── xi_crossing, xi_merging, ...
        └── sigma_crossing, sigma_merging, ...
    
    Scenario level (nested within conflict type)
        ├── xi_scenario_001, xi_scenario_002, ...
        └── sigma_scenario_001, sigma_scenario_002, ...
    
    Jurisdiction level (nested within conflict type)
        ├── xi_USA, xi_Canada, xi_England
        └── sigma_USA, sigma_Canada, sigma_England
    
    Priors on all levels
```

### 4.3 Cross-Jurisdiction Comparison

```python
# Compare collision rates across jurisdictions
def compare_jurisdictions(trace, collision_threshold=2.0):
    """Compute and compare collision rates across jurisdictions."""
    results = {}
    
    for jur in ["USA", "Canada", "England"]:
        # Extract jurisdiction-specific GPD parameters
        xi_j = trace.posterior["xi_jurisdiction"].sel(jurisdiction=jur)
        sigma_j = trace.posterior["sigma_jurisdiction"].sel(jurisdiction=jur)
        
        # Compute collision probability
        # P(TTC < threshold | GPD) = (1 + ξ·(threshold - u)/σ)^(-(1/ξ + 1))
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

## 5. File Structure

```
src/evaluation/bayesian_evt/
├── __init__.py
├── gpd.py              — GPD fitting and sampling
├── hierarchical.py     — Bayesian hierarchical model (PyMC)
├── collision_rate.py   — Collision occurrence likelihood estimation
├── severity_model.py   — Severity distribution fitting
├── threshold_selection.py — Mean residual life plot + stability analysis
├── posterior_predictive.py — PPC validation checks
├── jurisdiction.py     — Cross-jurisdiction comparison
├── crisis.py           — Full risk quantification pipeline
└── visualization.py    — Posterior plots, MRL plots, QQ-plots
```

## 6. Integration with Other Skills

### 6.1 Input from Stochastic Simulation
```python
# From Monte Carlo runs, extract extreme values
extreme_values = []
scenario_ids = []
conflict_type_ids = []

for run in monte_carlo_results:
    # Extract minimum TTC from each run
    min_ttc = np.min(run["TTC_values"])
    if min_ttc < threshold_u:
        excess = threshold_u - min_ttc  # positive excess
        extreme_values.append(excess)
        scenario_ids.append(run["scenario_id"])
        conflict_type_ids.append(run["conflict_type_id"])

extreme_values = np.array(extreme_values)
```

### 6.2 Input from Kinematics Engine
```python
# Trajectory data provides:
# - Exact collision times
# - Delta-V at impact
# - Impact angles
# - Vehicle positions/velocities at each timestep
# These feed into:
# - GPD threshold selection
# - Severity model parameters
# - Validation checks
```

### 6.3 Output to Indicator Computation
```python
# Bayesian results feed into indicator computation:
# - P(collision) replaces heuristic collision probability
# - GPD-predicted severity replaces heuristic severity metrics
# - Credible intervals on all estimates
# Result: more rigorous, statistically grounded indicators
```

## 7. Validation Requirements

### 7.1 Convergence Diagnostics
- **R-hat:** must be < 1.01 for all parameters
- **ESS:** must be > 400 for all parameters
- **Chain mixing:** trace plots show no drift
- **Effective sample size:** total ESS > 2000 per parameter

### 7.2 Model Comparison
- **LOO (Leave-One-Out):** lower is better
- **WAIC:** lower is better
- **Cross-validation:** hold-out test sets

### 7.3 Posterior Predictive Checks
- **CDF comparison:** observed and predicted CDFs overlap
- **Mean/median comparison:** within 95% CI
- **Tail behavior:** extreme values match GPD fit

### 7.4 Prior Sensitivity Analysis
- Test multiple prior specifications
- Compare posteriors across priors
- Document which priors are "informative" vs "weakly informative"

## 8. Prior Specifications

### 8.1 Default Priors (weakly informative)

```python
# Shape parameter ξ (typically -1 to 1 for traffic conflicts)
xi_prior = pm.Normal("xi", mu=0, sigma=0.5)

# Scale parameter σ (typically 0.1 to 20 for TTC in seconds)
sigma_prior = pm.HalfNormal("sigma", sigma=3)

# Jurisdiction hyperpriors
mu_xi_prior = pm.Normal("mu_xi", mu=0, sigma=1)
sigma_xi_prior = pm.HalfNormal("sigma_xi", sigma=0.5)

# Collision rate (typically 0.001 to 0.1 for traffic conflicts)
collision_rate_prior = pm.Beta("collision_rate", alpha=1, beta=99)
```

### 8.2 Informative Priors (when literature values available)

```python
# From published crash severity models (e.g., BANSYSE, ES-28)
xi_informative = pm.Normal("xi", mu=0.3, sigma=0.1)
sigma_informative = pm.HalfNormal("sigma", mu=5, sigma=1)

# From NHTSA FARS crash rate statistics
rate_prior = pm.Gamma("rate", alpha=5, beta=100)
```

## 9. Output Format

```python
{
    "scenario_id": "RE-CA-001",
    "conflict_type": "rear-end",
    "jurisdiction": "USA",
    "threshold": {
        "u": 1.5,
        "method": "mean_residual_life",
        "stability_analysis": "passed"
    },
    "gpd_parameters": {
        "xi": {
            "median": 0.35,
            "ci95": [0.12, 0.58],
            "rhat": 1.002,
            "ess": 1200
        },
        "sigma": {
            "median": 8.2,
            "ci95": [5.4, 12.1],
            "rhat": 1.001,
            "ess": 1400
        }
    },
    "collision_rate": {
        "estimate": 0.0234,
        "ci95": [0.0156, 0.0342],
        "n_collisions": 234,
        "n_simulations": 10000
    },
    "severity": {
        "delta_v_gpd": {
            "xi": {"median": 0.42, "ci95": [0.18, 0.67]},
            "sigma": {"median": 15.3, "ci95": [10.2, 22.8]}
        },
        "expected_severity": {
            "fatal_probability": 0.0012,
            "mai3_plus_probability": 0.0087,
            "injury_probability": 0.0456
        }
    },
    "posterior_predictive": {
        "cdf_ks_stat": 0.023,
        "tail_fit": "good",
        "qq_plot_pvalue": 0.45
    }
}
```
