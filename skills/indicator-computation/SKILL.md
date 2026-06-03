---
name: indicator-computation
description: "Compute all 42 traffic conflict and surrogate safety indicators for every timestep of every simulation run."
---

# Indicator Computation

Compute all 42 traffic conflict and surrogate safety indicators for every timestep of every simulation run.

## 6 Categories, 42 Indicators

| Category | Count | Indicators |
|---|-|-|
| Time-based | 11 | TTC, MTTC, PET, ET, THW, gap_time, TET, TIT, TAdv, PrET, worst_TTC |
| Distance-based | 5 | DTC, PSD, RDCP, min_spatial_gap, clearance |
| Deceleration-based | 8 | DRAC, RLA, MADR, DRAC-MADR, CPI, max_decel, avg_decel, DOB |
| Kinematic | 5 | delta_v, closing_speed, relative_accel, relative_angle, speed_diff |
| Severity | 6 | delta_v_impact, expected_severity, kinetic_energy, CSI, SRI, PCE |
| Probability | 6 | CP, CPI (decel), pTTT, CRI, RiskForce, ECF |

## Applicability Matrix Summary

| Indicator | Most Useful For |
|---|-|
| TTC, MTTC, PET | All conflict types (TTC universal) |
| THW, gap_time | Following vehicles (rear-end) |
| DRAC, MADR | Deceleration-based scenarios (rear-end, merging) |
| delta_v | All (primary severity predictor) |
| CP, CRI | Universal risk assessment |
| PCE, kinetic_energy | Severity comparison |

## Aggregation Strategy

Per-timestep (dt = 10ms):
- For each vehicle pair: compute all applicable indicators
- Store: t, pair_index, indicator_name, value

Over simulation:
- worst_value = min/max (indicator-dependent)
- mean/median/p5/p25/p75/p95 = percentiles
- time_exposed = count(valid) / total_steps

## Base Indicator Class

```python
class Indicator:
    name: str
    category: str  # time | distance | deceleration | kinematic | severity | probability
    unit: str
    applicable_to: List[str]  # conflict types
    formula: str
    references: List[str]
    
    def compute(self, users: List[RoadUser], t: float, trajectory_history: Dict) -> float:
        raise NotImplementedError
    
    def compute_over_history(self, trajectory_history: Dict) -> Dict:
        raise NotImplementedError
```

## Implementation Notes

- All inputs in SI units (meters, m/s, m/s²)
- Handle NaN/Inf: TTC with v_rel ≤ 0 returns inf; MTTC with negative discriminant returns inf
- Vectorize with numpy; batch same-timestep computations
- Sparse storage for indicator history

## Reference Data

### Vehicle Dimensions (NHTSA)
| Type | Length | Width | Mass |
|---|-|-|-|
| Compact car | 4.3m | 1.8m | 1200kg |
| Mid-size car | 4.7m | 1.85m | 1400kg |
| SUV | 4.8m | 2.0m | 1800kg |
| Pick-up | 5.5m | 2.1m | 2200kg |
| Heavy truck | 12.0m | 2.6m | 18000kg |
| Pedestrian | — | — | 70kg |
| Cyclist | 1.7m | 0.7m | 80kg |

### Friction Coefficients
| Surface | μ range | MADR (m/s²) |
|---|-|-|
| Dry asphalt | 0.7–0.9 | 6.9–8.8 |
| Wet asphalt | 0.4–0.5 | 3.9–4.9 |
| Snow | 0.1–0.3 | 1.0–2.9 |
| Ice | 0.05–0.15 | 0.5–1.5 |

## File Structure
```
src/indicators/
├── base.py           Base indicator class
├── manager.py        Indicator registry and pipeline
├── time_based/       11 indicators (ttc, mttc, pet, et, thw, etc.)
├── distance_based/   5 indicators (dtc, psd, rdcp, min_spatial_gap, clearance)
├── deceleration_based/ 8 indicators (drac, rla, madr, etc.)
├── kinematic/        5 indicators (delta_v, closing_speed, etc.)
├── severity/         6 indicators (delta_v_impact, expected_severity, etc.)
└── probability/      6 indicators (cp, pttt, cri, risk_force, ecf)
```
