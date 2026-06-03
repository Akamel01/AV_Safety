---
name: risk-metrics
description: "Define, implement, and validate quantitative metrics for measuring AV collision risk with citations and benchmarks."
---

# Risk Metrics

Define, implement, and validate quantitative metrics for measuring AV collision risk.

## Key Metrics with Formulas

### Collision Rate (λ)
```
λ = n_collisions / exposure
exposure = Σ (distance_traveled) or Σ (time_driven)
Units: collisions per 10M vehicle miles (VMT) or per 100M vehicle hours (VHT)
Citation: NHTSA standard reporting metric
```

### Severity-Weighted Risk (SWR)
```
SWR = Σ (severity_i × weight_i) / n_events
severity_i ∈ {fatal=1.0, MAIS3+=0.5, injury=0.1, property damage=0.01}
weight_i = exposure_weight_i
Citation: NHTSA ES-28, BANSYSE injury correlation
```

### TTC Distribution
```
TTC(t) = d(t) / v_rel(t) when v_rel > 0
Model TTC as GPD above threshold u
P(TTC < τ) = (1 + ξ·(τ - u)/σ)^(-(1/ξ + 1))
```

### Critical Event Rate
```
Critical event = any TTC < TTC_critical (typically 1.5–2.5s)
Rate = n_critical_events / exposure
Near-miss analysis: use TTC percentile distribution rather than binary collision
```

### Risk per Scenario Type
```
For each conflict type k:
  λ_k = n_collisions_k / exposure_k
  SWR_k = Σ(severity_i × weight_i) / n_events_k
  Report by jurisdiction, time of day, road type
```

### Standard-Aligned Metrics

**UL 4600 Requirements:**
- Risk assessment methodology (Section 6.2)
- Hazard identification (Section 7.1)
- Safety case evidence (Section 10)

**ISO 21448 (SOTIF) Requirements:**
- HARA (Hazard Analysis and Risk Assessment)
- Perceived functional hazards
- Performance limitations
- Manipulation and misuse

**ISO 26262 Requirements:**
- ASIL (Automotive Safety Integrity Level) classification
- Safety goals and requirements
- Technical safety requirements

## Workflow

1. **Define** metric mathematically (formal definition, inputs, outputs)
2. **Implement** in `src/risk_models/metrics/<metric_name>.py`
3. **Test** against known data in `tests/test_<metric>.py`
4. **Validate** against published benchmarks
5. **Document** in `docs/architecture/metrics/<metric_name>.md`

## Output Format

Each metric module must include:
- Mathematical formula (LaTeX in docstring)
- Input/output specs with units
- Citation to source or derivation
- Test coverage ≥ 80%

## Rules

- Every metric must have a cited source or documented derivation
- All parameters justified with literature or data
- Test against multiple data sources when possible
- Document limitations and known edge cases

## Reuse Trigger

Use when:
- Building new risk quantification components
- Comparing risk assessment approaches
- Validating safety claims numerically
- Portfolio visualization of risk metrics

## File Structure
```
src/risk_models/
├── metrics/
│   ├── collision_rate.py
│   ├── severity_weighted_risk.py
│   ├── ttc_distribution.py
│   ├── critical_event_rate.py
│   └── risk_per_scenario_type.py
└── validation/
    ├── benchmark.py
    └── citation_index.py
```
