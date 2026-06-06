---
name: bayesian-evt
description: "Quantify collision risk (occurrence likelihood and severity) using Bayesian Hierarchical Extreme Value Theory, integrated with kinematics engine, indicator computation, and stochastic simulation."
---

# Bayesian Hierarchical EVT

Quantify collision risk (occurrence likelihood and severity) using Bayesian Hierarchical Extreme Value Theory, integrated with the kinematics engine, indicator computation, and stochastic simulation.

## EVT Theory

- **Block Maxima → GEV:** model min TTC over fixed time blocks
- **Peaks-over-Threshold → GPD:** model all values exceeding threshold ✅ (preferred — more data-efficient)

### GPD Model

```
For excesses X - u > 0 over threshold u:

f(x; ξ, σ) = (1/σ) · (1 + ξ(x-u)/σ)^(-(1/ξ + 1))

ξ = shape (tail heaviness):
  ξ > 0: heavy-tailed (Pareto)
  ξ = 0: exponential (Gumbel)
  ξ < 0: bounded (Weiblet)
σ = scale (spread)
u = threshold
```

### Collision Rate Estimation

```
P(collision) = P(exceedance) × P(TTC < TTC_threshold | exceedance)
             = (1 - F(u)) × (1 + ξ·(TTC_threshold - u)/σ)^(-(1/ξ + 1))
```

### Severity Estimation

```
Severity | Collision ~ GPD(ξ_sev, σ_sev)
Parameters from: ΔV at impact, impact angle, vehicle mass ratio, occupant protection
Severity index: S = δ · f(ΔV, θ, μ_mass, μ_protect)
```

## Hierarchical Structure (4 Levels)

1. **Scenario level:** ξ_s, σ_s ~ Normal(ξ_hyper, τ_ξ), HalfNormal(τ_σ)
2. **Conflict type level:** ξ_hyper_k ~ Normal(μ_ξ, ρ_ξ), σ_hyper_k ~ HalfNormal(ρ_σ)
3. **Jurisdiction level:** μ_ξ_j, ρ_ξ_j ~ Priors
4. **Cross-jurisdiction:** Global hyperpriors on jurisdiction parameters

## MRL Threshold Selection

1. Sort extreme values descending
2. For each u_i, compute mean of (X - u_i) for all X > u_i
3. Plot mean residual life (MRL) vs u: linear for large u when GPD valid
4. Threshold = first point where linearity begins
5. **Stability analysis:** fit GPD at [u-δ, u, u+δ], check ξ and σ overlap within CI
6. **QQ-plot validation:** transform data, plot empirical vs GPD quantiles; 45° line = good fit

## Cross-Skill Dependencies

- **stochastic-simulation** (upstream) — extreme values from Monte Carlo (min TTC < u) drive GPD fitting
- **kinematics-engine** (upstream) — collision times, ΔV, impact angles, positions for threshold selection and severity model
- **indicator-computation** (upstream) — all 42 indicator values replaced by GPD estimates
- **bayesian-analysis** (sibling) — shares hierarchical modeling approach; bayesian-evt specific to EVT/GEV/GPD
- **safety-thresholds** (downstream) — GPD-predicted collision rates feed into safe threshold computation
- **risk-metrics** (downstream) — GPD-predicted severity and collision rate drive risk metric computation
- **risk-quantification** (sibling) — bayesian-evt provides the EVT module for the full risk quantification pipeline

## Cross-Skill Data Flow

**P(collision) from GPD replaces heuristic collision probability**
**GPD-predicted severity replaces heuristic severity metrics**
**Credible intervals on all estimates propagate to downstream skills**

## Validation Requirements

- **R-hat:** < 1.01 for all parameters
- **ESS:** > 400 per parameter (total > 2000)
- **LOO/WAIC:** lower is better for model comparison
- **PPC:** observed and predicted CDFs overlap, tail behavior matches GPD
- **Prior sensitivity:** test multiple priors, compare posteriors

## Prior Specifications

| Parameter | Weakly Informative | Informative (when lit. available) |
|---|-|-|
| ξ (shape) | Normal(0, 0.5) | Normal(0.3, 0.1) from BANSYSE |
| σ (scale) | HalfNormal(σ=3) | HalfNormal(μ=5, σ=1) |
| μ_ξ (hyper) | Normal(0, 1) | — |
| σ_ξ (hyper) | HalfNormal(σ=0.5) | — |
| collision rate | Beta(1, 99) | Gamma(5, 100) from NHTSA |

## Output Format

```python
{
    "scenario_id": "RE-CA-001",
    "conflict_type": "rear-end",
    "jurisdiction": "USA",
    "threshold": {"u": 1.5, "method": "MRL", "stability": "passed"},
    "gpd_parameters": {
        "xi": {"median": 0.35, "ci95": [0.12, 0.58], "rhat": 1.002, "ess": 1200},
        "sigma": {"median": 8.2, "ci95": [5.4, 12.1], "rhat": 1.001, "ess": 1400}
    },
    "collision_rate": {"estimate": 0.0234, "ci95": [0.0156, 0.0342], "n_collisions": 234, "n_sim": 10000},
    "severity": {
        "delta_v_gpd": {"xi": {"median": 0.42, "ci95": [0.18, 0.67]}, "sigma": {"median": 15.3, "ci95": [10.2, 22.8]}},
        "expected_severity": {"fatal_probability": 0.0012, "mai3_plus_probability": 0.0087, "injury_probability": 0.0456}
    },
    "posterior_predictive": {"cdf_ks_stat": 0.023, "tail_fit": "good", "qq_plot_pvalue": 0.45}
}
```

## Reference Implementation Location

GPD/EVT logic is distributed across the active src/ packages:

- **`src/risk_quantification/pipeline.py`** — orchestrates EVT stage in the 7-step pipeline (kinematics → indicators → Monte Carlo → Bayesian EVT → collision modeling → safety thresholds → portfolio output)
- **`src/risk_quantification/risk_scoring.py`** — GPD-based risk scoring
- **`src/risk_quantification/threshold_checker.py`** — GPD collision rate vs threshold
- **`src/safety_thresholds/baseline_estimator.py`** — baseline risk (GPD-informed)
- **`src/safety_thresholds/collision_rate_thresholds.py`** — collision rate thresholds
- **`src/safety_thresholds/ttc_thresholds.py`** — TTC thresholds (used by EVT)
- **`src/safety_thresholds/drac_thresholds.py`** — DRAC thresholds (used by EVT)

Future: dedicated `src/evaluation/bayesian_evt/` package when module scope grows beyond pipeline integration.
