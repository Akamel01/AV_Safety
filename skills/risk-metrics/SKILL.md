# Skill: Risk Metrics

**Purpose:** Define, implement, and validate quantitative metrics for measuring AV collision risk.

## Capabilities

1. **Metric definition** — Formalize risk metrics with clear mathematical definitions
2. **Metric implementation** — Code metrics in `src/analysis/` and `src/risk_models/`
3. **Benchmark comparison** — Compare against industry metrics (PMHS, VRU collision rates, etc.)
4. **Sensitivity analysis** — Test how metrics respond to parameter changes

## Key Metrics to Implement

- **Collision rate** (per distance, per trip, per exposure hour)
- **Severity-weighted risk** (injury level × frequency)
- **Time-to-collision** distributions
- **Critical event rate** (near-miss analysis)
- **Risk per scenario type** (intersection, highway, urban, pedestrian, etc.)
- **Standard-aligned metrics** (from UL 4600, ISO 21448)

## Workflow

1. **Define** metric mathematically (formal definition, inputs, outputs)
2. **Implement** in `src/risk_models/metrics/<metric_name>.py`
3. **Test** against known data in `tests/test_<metric>.py`
4. **Validate** against published benchmarks
5. **Document** in `docs/architecture/metrics/<metric_name>.md`

## Output Format

Each metric module must include:
- Mathematical formula (LaTeX in docstring)
- Input/output specs
- Parameter descriptions with units
- Citation to source or derivation
- Test coverage ≥ 80%

## Rules

- Every metric must have a cited source or documented derivation
- Never use undefined constants — all parameters justified
- Test against multiple data sources when possible
- Document limitations and known edge cases

## Reuse

This skill is used when:
- Building new risk quantification components
- Comparing risk assessment approaches
- Validating safety claims numerically
- Portfolio visualization of risk metrics
