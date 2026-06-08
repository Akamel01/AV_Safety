---
name: stochastic-simulation
description: "Drive Monte Carlo simulations for collision risk quantification, parameter sampling, and uncertainty propagation through the kinematic engine."
---

# Stochastic Simulation

Drive Monte Carlo simulations for collision risk quantification, parameter sampling, and uncertainty propagation through the kinematic engine.

## Simulation Framework

```
Parameter Space (θ)
    ↓
Monte Carlo Sampler (N iterations)
    For each i:
        1. Sample θ_i ~ p(θ)
        2. Run simulation
        3. Extract outcomes
        4. Compute results
    ↓
Results: collision rate, severity stats, indicator CDFs, uncertainty bounds
```

## Parameter Distributions

| Parameter | Distribution | Conditions |
|---|-|-|
| Speed (urban car) | Normal(μ, σ) | μ=11.2, σ=3.1, range [0, 33.3] |
| Speed (highway car) | Normal | μ=27.8, σ=4.2, range [15.6, 41.7] |
| Reaction time | Lognormal | Normal: μ_log=0.7 σ=0.3; Alert: 0.5/0.2; Distracted: 0.9/0.4 |
| Braking delay | Lognormal | Standard: μ_log=-0.5 σ=0.2; Panic: -0.3/0.15 |
| Road friction | Normal | Dry: μ=0.80 σ=0.05; Wet: 0.45/0.08; Snow: 0.20/0.08 |
| Cut-in distance | Normal/Lognormal | Aggressive: μ=10; Normal: 25; Conservative: 40 |

### Vehicle Speed Distributions
| Type | Road | μ | σ | Range |
|---|-|-|-|-|
| Urban car | urban | 11.2 m/s | 3.1 | [0, 33.3] |
| Urban SUV | urban | 12.0 m/s | 3.5 | [0, 33.3] |
| Highway car | highway | 27.8 m/s | 4.2 | [15.6, 41.7] |
| Highway SUV | highway | 28.5 m/s | 4.5 | [15.6, 41.7] |
| Highway truck | highway | 24.0 m/s | 3.8 | [13.9, 36.1] |

### Friction Distributions
| Surface | μ | σ | Range | MADR (m/s²) |
|---|-|-|-|-|
| Dry asphalt | 0.80 | 0.05 | [0.6, 0.95] | 6.9–8.8 |
| Wet asphalt | 0.45 | 0.08 | [0.3, 0.6] | 3.9–4.9 |
| Snow | 0.20 | 0.08 | [0.1, 0.35] | 1.0–2.9 |
| Ice | 0.10 | 0.05 | [0.05, 0.20] | 0.5–1.5 |
| Gravel | 0.55 | 0.10 | [0.4, 0.75] | ~5.4 |

### Reaction Time Conditions
| Condition | μ_log | σ_log | Median |
|---|-|-|-|
| Alert | 0.5 | 0.2 | ~1.4s |
| Normal | 0.7 | 0.3 | ~2.0s |
| Distracted | 0.9 | 0.4 | ~2.7s |
| Elderly | 1.0 | 0.35 | ~3.0s |
| Exhausted | 1.1 | 0.45 | ~3.3s |

## Monte Carlo Engine Design

```python
class MonteCarloEngine:
    def __init__(self, scenario, n_samples=10000):
        self.scenario = scenario
        self.n_samples = n_samples
    
    def run(self) -> dict:
        # For each iteration:
        #   1. Sample parameters from distributions
        #   2. Validate (speed [0,50], reaction [0.1,5], friction [0.05,1.0])
        #   3. Run kinematic simulation
        #   4. Record collision/no-collision + all applicable indicators
        return self._aggregate_results(collisions, indicators)
    
    def _aggregate_results(self, collisions, indicators):
        return {
            "collision_rate": n_collisions / n_sim,
            "collision_rate_ci95": wilson_ci(n_collisions, n_sim),
            # Per-indicator: mean, median, p5, p25, p75, p95, min, max
        }
    
    def wilson_ci(self, successes, trials, confidence=0.95):
        p = successes / trials
        z = norm.ppf((1 + confidence) / 2)
        denom = 1 + z**2 / trials
        center = (p + z**2 / (2*trials)) / denom
        margin = z * sqrt((p*(1-p) + z**2/(4*trials)) / trials) / denom
        return (max(0, center-margin), min(1, center+margin))
```

## Adaptive Sample Sizing

- **Init:** 1,000 samples
- **Step:** +500 per iteration
- **Max:** 50,000
- **Convergence:** CI width < 2%
- **Stop:** converged or max reached

## Uncertainty Quantification

- **Binomial CI:** Wilson score interval (default 95%)
- **Bootstrap CI:** 10,000 bootstrap resamples for non-parametric estimates
- **Sobol sensitivity:** SALib for parameter importance (S1 first-order, ST total-effect)

## Validation Requirements

1. **Convergence:** CI width < 2% (default threshold)
2. **Stability:** Same seed → same results (deterministic)
3. **Distribution fit:** Sampled parameters match target distributions
4. **Benchmark:** Collision rates vs published crash data
5. **Cross-validation:** Independent simulation tool comparison
6. **Reproducibility:** Log all random seeds, parameter distributions, simulation params

## Reuse Trigger

Use when:
- Running Monte Carlo for any conflict scenario
- Quantifying uncertainty in collision risk estimates
- Computing sensitivity of parameters to outcomes
- Generating stochastic outcome data for Bayesian EVT

## Cross-Skill Dependencies

- **scenario-taxonomy** (upstream) — parameter distributions per conflict type
- **kinematics-engine** (downstream) — sampled parameters drive kinematic simulation
- **bayesian-evt** (downstream) — extreme values from Monte Carlo feed GPD fitting
- **indicator-computation** (downstream) — simulation runs produce indicator histories
- **risk-quantification** (sibling) — Monte Carlo results feed the risk quantification pipeline
- **data-ingest** (sibling) — data-derived distributions inform parameter priors

## File Structure (target — when src/simulation/ package is created)
```
src/simulation/
├── engine.py            Monte Carlo engine
├── adaptive_engine.py   Adaptive sample sizing
├── parameter_sampler.py Distribution sampling
├── convergence.py       Convergence detection
├── sensitivity.py       Sobol sensitivity analysis
├── scenarios/config/    Scenario-specific parameter configs
└── results/
    ├── aggregation.py   Monte Carlo aggregation
    ├── statistics.py    Statistical summaries
    └── export.py        Export (JSON, CSV)
```
