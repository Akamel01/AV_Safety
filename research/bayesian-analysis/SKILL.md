---
name: bayesian-analysis
description: "Apply Bayesian hierarchical models for collision risk quantification with PyMC/Stan, including prior elicitation, MCMC diagnostics, posterior analysis, and model comparison."
---

# Bayesian Analysis

Apply Bayesian statistical methods to quantify uncertainty in collision risk estimates and safety claims.

## Capabilities

- **Prior elicitation** — Construct informed priors from literature and domain expertise
- **Model specification** — Define hierarchical Bayesian models for risk data
- **Inference** — Fit models using MCMC or variational methods (PyMC, Stan)
- **Posterior analysis** — Extract credible intervals, posterior predictive checks, model comparison
- **Sensitivity analysis** — Test how priors and model structure affect risk conclusions

## Cross-Skill Dependencies

- **bayesian-evt** (sibling) — shares hierarchical modeling; bayesian-evt specific to EVT/GEV/GPD
- **stochastic-simulation** (upstream) — Monte Carlo outputs feed Bayesian model data
- **safety-thresholds** (downstream) — Bayesian posteriors inform safe threshold computation
- **risk-metrics** (downstream) — Bayesian risk estimates feed risk metric computation
- **risk-quantification** (downstream) — Bayesian module provides posterior analysis for the full pipeline
- **scenario-taxonomy** (upstream) — scenario hierarchy drives hierarchical model structure
- **data-ingest** (upstream) — cleaned data becomes Bayesian model input

## Workflow

1. **Define** the Bayesian model (likelihood, priors, hierarchical structure)
2. **Specify** in `src/evaluation/bayesian/<model_name>.py` (target package)
3. **Fit** the model and run convergence diagnostics (R-hat, ESS)
4. **Validate** with posterior predictive checks
5. **Document** model assumptions, priors, and posterior summaries in `docs/research/bayesian/<model_name>.md`

## Key Models

- **Bayesian collision rate estimation** — rate parameters with Gamma/Poisson priors
- **Hierarchical jurisdiction models** — USA/Canada/England comparisons
- **Bayesian model comparison** — for competing risk models
- **Bayesian safety threshold estimation** — posterior distributions on "safe enough" thresholds
- **Meta-analysis framework** — synthesize findings across studies

## Output Format

Each module must include:
- Full model specification (likelihood + prior + hierarchical structure)
- MCMC diagnostics (R-hat, ESS, chain counts)
- Posterior summaries (median, 95% CI, prior vs posterior)
- Posterior predictive check results
- Model comparison metrics (LOO, WAIC if applicable)

## Reuse Trigger

Use when:
- Quantifying uncertainty in any risk estimate
- Comparing AV safety across jurisdictions
- Estimating safety thresholds with proper uncertainty bounds
- Synthesizing evidence from multiple sources
