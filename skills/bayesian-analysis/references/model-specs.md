# Priors and Model Specs — Bayesian Analysis

## Prior Elicitation Guide

### Collision Rate (λ) — Gamma Prior
```
λ ~ Gamma(α, β)
```
- **Uninformative:** Gamma(0.001, 0.001)
- **Weakly informative:** Gamma(1, 10) — mean 0.1, std 0.1
- **Moderate:** Gamma(5, 50) — mean 0.1, std 0.03
- **Justification:** Conjugate prior for Poisson likelihood; well-established in traffic safety literature

### Collision Probability (p) — Beta Prior
```
p ~ Beta(α, β)
```
- **Uninformative:** Beta(1, 1)
- **Weakly informative:** Beta(2, 20) — mean ~0.09
- **Moderate:** Beta(5, 50) — mean ~0.09, tighter
- **Justification:** Conjugate prior for Bernoulli/Binomial likelihood

### Severity Parameter (ξ for GPD) — Normal Prior
```
ξ ~ Normal(0, σ_ξ)
```
- **Conservative:** Normal(0.2, 0.1) — centered near typical ξ values (0.1–0.3)
- **Weakly informative:** Normal(0, 0.5)
- **Justification:** GPD shape parameter is typically small positive; center near prior literature values

### Scale Parameter (σ for GPD) — Half-Cauchy Prior
```
σ ~ Half-Cauchy(0, scale)
```
- **Weakly informative:** Half-Cauchy(0, 5)
- **Justification:** Heavy-tailed prior prevents over-confidence in scale estimates

## Hierarchical Model Specification

### Jurisdiction-Level Hierarchy
```python
# PyMC example
with pm.Model() as hierarchical_model:
    # Hyperpriors
    mu_lambda = pm.Normal('mu_lambda', mu=0, sigma=1)
    sigma_lambda = pm.HalfNormal('sigma_lambda', sigma=1)
    
    # Jurisdiction-specific rates
    lambda_jurisdiction = pm.GaussianRandomWalk(
        'lambda_jurisdiction', 
        mu=mu_lambda, 
        sigma=sigma_lambda, 
        dims='jurisdiction'
    )
    
    # Likelihood
    y_obs = pm.Poisson(
        'y_obs', 
        mu=lambda_jurisdiction[observed_jurisdiction], 
        observed=y_data
    )
```

### Hierarchical EVT Model
```python
with pm.Model() as hierarchical_evt:
    # Global EVT parameters
    xi_global = pm.Normal('xi_global', mu=0.2, sigma=0.1)
    sigma_global = pm.HalfNormal('sigma_global', sigma=2)
    
    # Jurisdiction-specific deviations
    xi_jurisdiction = pm.Normal(
        'xi_jurisdiction', 
        mu=xi_global, 
        sigma=pm.math.sqrt(sigma_global)
    )
    sigma_jurisdiction = pm.HalfNormal(
        'sigma_jurisdiction', 
        mu=sigma_global, 
        sigma=0.5
    )
    
    # GPD likelihood for exceedances
    u = threshold  # threshold from MRL plot
    exceedances = data[data > u]
    
    # Log-likelihood of GPD
    n_exc = len(exceedances)
    log_lik = n_exc * pm.math.log(xi_global / sigma_global) - (1 + 1/xi_global) * pm.math.log(1 + xi_global * (exceedances - u) / sigma_global)
    pm.DensityDist('density', lambda v: log_lik)
```

## MCMC Diagnostics — Thresholds

| Diagnostic | Threshold | Action if Failed |
|---|-|-|
| R-hat (bulk) | < 1.01 | Redraw chains, increase adapt_delta |
| R-hat (tail) | < 1.05 | Check multimodality, reparameterize |
| ESS (bulk) | > 400 per chain | Increase samples, reparameterize |
| ESS (tail) | > 400 per chain | Same as bulk |
| Divergent transitions | 0 | Increase adapt_delta (default 0.8 → 0.95) |
| Tree depth | < max_depth (default 10) | Increase max_depth or reparameterize |
| Acceptance probability | 0.6–0.9 | Tune step size manually |

## Model Comparison

### WAIC (Widely Applicable Information Criterion)
```python
# PyMC
waic = pm.waic(trace, pointwise=True)
print(waic)
# Use lower WAIC for better model fit
```

### LOO (Leave-One-Out Cross-Validation)
```python
# PyMC
loo = pm.loo(trace, pointwise=True)
print(loo)
# Use lower LOO for better out-of-sample prediction
```

### Bayes Factors (when comparing exactly 2 models)
```
BF12 = exp(0.5 * (WAIC2 - WAIC1))
```
- BF12 > 3: Model 1 has substantial support over Model 2
- BF12 > 10: Strong support for Model 1

## Posterior Predictive Checks

```python
# PyMC
post_pred = pm.sample_posterior_predictive(trace, var_names=['y_rep'])

# Compare observed vs predicted
observed_mean = np.mean(y_observed)
predicted_mean = np.mean(post_pred['y_rep'].values.flatten())

# Check should be similar if model fits well
print(f"Observed mean: {observed_mean}")
print(f"Predicted mean: {predicted_mean}")

# Visual check: ECDF comparison
import arviz as az
az.plot_ppc(post_pred, alpha=0.5)
```

## Sensitivity Analysis

```python
def run_sensitivity(y_observed, prior_configs):
    """Test prior sensitivity across multiple prior specifications"""
    results = {}
    for name, prior in prior_configs.items():
        trace = fit_model(y_observed, prior=prior)
        results[name] = {
            'lambda_posterior_median': np.median(trace['lambda']),
            'lambda_95_CI': [np.percentile(trace['lambda'], 2.5), np.percentile(trace['lambda'], 97.5)],
            'ESS': az.ess(trace)['lambda'],
            'R_hat': az.rhat(trace)['lambda']
        }
    return results

# Example prior configs
prior_configs = {
    'uninformative': pm.Gamma('lambda', alpha=0.001, beta=0.001),
    'weakly_informative': pm.Gamma('lambda', alpha=1, beta=10),
    'moderate': pm.Gamma('lambda', alpha=5, beta=50),
    'strong': pm.Gamma('lambda', alpha=50, beta=500)
}
```

## Documentation Template

```markdown
# Model: <model_name>

## Purpose
<What question does this model answer?>

## Data
- Source: <NHTSA FARS / CISS / DfT GB / CMFwiki>
- Period: <YYYY-YYYY>
- Observations: <N>
- Variables: <x1, x2, ...>

## Model Specification
```
<Full model equations>
```

## Priors
| Parameter | Prior | Justification |
|---|-|-|
| λ | Gamma(α, β) | <Justification> |
| σ | Half-Cauchy(0, scale) | <Justification> |

## MCMC Diagnostics
| Diagnostic | Value | Threshold | Pass? |
|---|-|-|-|
| R-hat (bulk) | <val> | <1.01 | ✅/❌ |
| ESS (bulk) | <val> | >400 | ✅/❌ |
| Divergences | <n> | 0 | ✅/❌ |

## Posterior Summaries
| Parameter | Median | 95% CI | Prior Median |
|---|-|-|-|
| λ | <val> | [<lo>, <hi>] | <prior> |

## Model Comparison
| Model | WAIC | LOO | Notes |
|---|-|-|-|
| Model A | <val> | <val> | <notes> |
| Model B | <val> | <val> | <notes> |

## Assumptions & Limitations
1. <Assumption 1>
2. <Limitation 1>
3. <Data sparsity warning if applicable>
```
