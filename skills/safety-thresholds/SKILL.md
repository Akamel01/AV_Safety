---
name: safety-thresholds
description: "Quantify 'safe enough' thresholds for autonomous vehicle deployment using statistical analysis, Bayesian modeling, and regulatory frameworks."
---

# Safety Thresholds

Quantify "safe enough" thresholds for autonomous vehicle deployment using statistical analysis, Bayesian modeling, and regulatory frameworks.

## Framework: "How Safe is Safe Enough?"

1. **Establish baseline risk** — human driver collision rates by jurisdiction
2. **Define acceptable risk** — how much safer AV must be vs humans
3. **Set deployment thresholds** — minimum safety level for AV approval
4. **Validate thresholds** — test against real-world data and standards

## Jurisdiction Baseline Collision Rates

| Jurisdiction | Fatal Rate (per 100M miles) | Injury Rate | Property Damage Rate | Source |
|---|-|-|-|-|
| USA | 1.12 [1.05–1.19] | 125.0 | 500.0 | NHTSA FARS 2020 |
| Canada | 0.89 [0.82–0.96] | 98.0 | 410.0 | Transport Canada 2020 |
| England | 0.72 [0.65–0.79] | 85.0 | 380.0 | DfT GB 2020 |

## TTC Thresholds

| Level | Threshold (s) | Description | Action |
|---|-|-|-|
| Critical | 1.0 | Immediate collision likely | Emergency brake |
| Dangerous | 2.0 | High collision risk | Hard brake |
| Warning | 3.0 | Moderate collision risk | Alert driver |
| Safe | 5.0 | Low collision risk | Monitor |

## DRAC Thresholds

| Level | Threshold (m/s²) | Description | Action |
|---|-|-|-|
| Emergency | 8.0 | Maximum emergency braking | Full brake |
| Hard brake | 5.0 | Hard braking required | Hard brake |
| Moderate | 3.0 | Moderate braking | Alert driver |
| Light | 1.5 | Light braking | Monitor |

## Threshold Computation

```python
# Safe threshold = baseline × (1 - required_reduction)
# Deployment threshold = safe_threshold × (1 + margin)
margin = 0.15  # 15% margin
```

### Example Thresholds
| Jurisdiction | Safe Threshold | Deployment Threshold | Baseline Fatal Rate | Required Reduction |
|---|-|-|-|-|
| USA | 0.85 | 0.97 | 1.12 | 24.1% |
| Canada | 0.67 | 0.77 | 0.89 | 24.7% |
| England | 0.54 | 0.62 | 0.72 | 25.0% |

## Standards-Based Thresholds

### UL 4600
- Collision avoidance: minimum TTC = 2.0s, max acceptable rate = 10⁻⁶/hour
- Risk management: individual risk ≤ 10⁻⁵/hour, societal ≤ 10⁻⁷/hour
- Risk reduction ≥ 90% below baseline

### ISO 21448 (SOTIF)
- Performance: min TTC ≥ 2.5s, degradation tolerance ≤ 10%, fallback ≥ 50m
- Hazard analysis: unintended functionality = zero tolerance
- TTC ≥ 1.0s at perception limit, ≥ 2.0s at actuation limit

## Deployment Criteria

```python
compliance = (
    "APPROVED" if av_rate < safe_threshold else
    "CONDITIONAL" if av_rate < deployment_threshold else
    "DENIED"
)
margin = (deployment_threshold - av_rate) / deployment_threshold × 100
```

## Continuous Monitoring

- Update thresholds via online learning: `updated = (1-λ) × prior + λ × likelihood`
- Learning rate λ = 0.01 (default)
- Bayesian update for threshold estimation

## Validation Requirements

| Criterion | Test | Pass Condition |
|---|-|-|
| Statistical significance | Compare AV vs baseline | p < 0.05 |
| Practical significance | Reduction ≥ 10% | True |
| Standards alignment | UL 4600 / ISO 21448 | Compliant |
| Jurisdiction alignment | Meets local requirements | True |
| Margin adequacy | ≥ 15% margin | True |

## Documentation
Every threshold: source, methodology, assumptions, confidence level
Comparison to published benchmarks with citation
Sensitivity analysis for key parameters
Review by independent safety experts (if available)

## Reuse Trigger

Use when:
- Defining safe thresholds for AV deployment
- Comparing AV performance against safety standards
- Validating thresholds against real-world data
- Building compliance matrices for regulatory approval

## File Structure
```
src/safety_thresholds/
├── baseline_estimator.py     Human driver baseline rates
├── acceptable_risk.py        Define acceptable risk reduction
├── safe_threshold.py         Compute safe/deployment thresholds
├── ttc_thresholds.py         TTC threshold definitions
├── drac_thresholds.py        DRAC threshold definitions
├── standards.py              UL 4600 / ISO 21448 thresholds
├── deployment_criteria.py    AV deployment evaluation
└── monitoring.py             Continuous monitoring / online update
```
