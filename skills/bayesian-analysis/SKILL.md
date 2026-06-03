# Skill: Bayesian Analysis

**Purpose:** Apply Bayesian statistical methods to quantify uncertainty in collision risk estimates and safety claims.

## Capabilities

1. **Prior elicitation** — Construct informed priors from literature and domain expertise
2. **Model specification** — Define hierarchical Bayesian models for risk data
3. **Inference** — Fit models using MCMC or variational methods (PyMC, Stan)
4. **Posterior analysis** — Extract credible intervals, posterior predictive checks, model comparison
5. **Sensitivity analysis** — Test how priors and model structure affect risk conclusions

## Workflow

1. **Define** the Bayesian model (likelihood, priors, hierarchical structure)
2. **Specify** in PyMC or Stan format in `src/analysis/bayesian/<model_name>.py`
3. **Fit** the model and run convergence diagnostics (R-hat, ESS)
4. **Validate** with posterior predictive checks
5. **Document** model assumptions, priors, and posterior summaries in `docs/research/bayesian/<model_name>.md`

## Key Models to Implement

- **Bayesian collision rate estimation** — rate parameters with proper priors
- **Hierarchical jurisdiction models** — USA/Canada/UK comparisons
- **Bayesian model comparison** — for competing risk models
- **Bayesian safety threshold estimation** — posterior distributions on "safe enough" thresholds
- **Meta-analysis framework** — synthesize findings across studies

## Output Format

Each Bayesian analysis module must include:
- Full model specification (likelihood + prior + hierarchical structure)
- MCMC diagnostics (R-hat, ESS, chain counts)
- Posterior summaries (median, 95% CI, prior vs posterior comparison)
- Posterior predictive check results
- Model comparison metrics (LOO, WAIC if applicable)

## Rules

- Always report full uncertainty (credible intervals), not point estimates
- Document every prior choice with justification
- Run convergence diagnostics — never trust uncritical MCMC output
- Compare multiple models; never assume the first model is the right one
- Flag when data is too sparse to support confident conclusions

## Reuse

This skill is used when:
- Quantifying uncertainty in any risk estimate
- Comparing AV safety across jurisdictions
- Estimating safety thresholds with proper uncertainty bounds
- Synthesizing evidence from multiple sources
