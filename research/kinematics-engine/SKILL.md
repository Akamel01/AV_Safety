---
name: kinematics-engine
description: "Compute exact trajectories, positions, and velocities for all road users in every conflict type scenario using universal kinematic models."
---

# Kinematics Engine

Compute exact trajectories, positions, and velocities for all road users in every conflict type scenario, driven by computed trajectories and collision probability.

## State Representation

Each road user `i`:
```
State_i(t) = { position: (x, y), velocity: v, heading: θ, acceleration: a, jerk: j }
```

## Vehicle Models

| Model | Position Update | Max Accel | Max Decel | Max Jerk |
|---|-|-|-|-|
| Constant velocity | x(t) = x₀ + v·t | 0 | 0 | 0 |
| Constant acceleration | x(t) = x₀ + v₀t + ½at² | ±5 m/s² | -8 m/s² | 3 m/s³ |
| Pacejka tire | Full dynamics with slip | ±6 m/s² | -10 m/s² | 5 m/s³ |
| Bicycle (single-track) | With steering | ±5 m/s² | -8 m/s² | 4 m/s³ |
| Pedestrian | Bipedal stride | ±1.5 m/s² | -3 m/s² | 2 m/s³ |
| Cyclist | Bicycle + lean | ±2 m/s² | -6 m/s² | 3 m/s³ |

### Pedestrian
- Stride: 0.75m at 1.4 m/s; max 2.2 m/s (brisk), 3.5 m/s (run)
- Turning radius: 0.3m (normal), 0.15m (emergency)
- Reaction: 0.25s perception + 0.75s response = 1.0s typical

### Cyclist
- Cruising: 4–6 m/s (urban), 8–12 m/s (highway); sprint up to 15 m/s
- Braking: 3–5 m at 12 m/s (good pavement)
- Turning radius: ≥2.0m (normal), 1.0m (emergency)

## 8 Conflict Types

### 1. Crossing
- 90° intersection at origin; vehicles approach from perpendicular directions
- Collision: AABB bounding box overlap at intersection

### 2. Merging (Cut-in)
- Lane change into lead vehicle's lane
- Lane change: y(t) = y₀ + Δy·(t/t_change)² for t < t_change (quadratic)
- Δy = lane_width (3.5m); t_change = 2–4s

### 3. Diverging (Lane Exit)
- Vehicle exits to off-ramp; circular arc exit R = 30–50m
- Deceleration while turning

### 4. Weaving
- Two vehicles cross-lane in weave section; sinusoidal lane change: g(t) = 0.5 - 0.5·cos(π·t/t_weave)

### 5. Rear-End
- Same-lane following; B reacts with delay: v_B(t) = v_B0 for t < reaction_time, then decelerate
- Critical: cut-under at short distance

### 6. Sideswipe
- Adjacent/same-lane minimum lateral gap = (w_A + w_B)/2
- Δv_lateral > 0.5 m/s required

### 7. Right-Angle
- Intersection approach; bounding box AABB overlap
- Critical: red-light running time gap analysis

### 8. Opposing Left-Turn
- Turning path: x = R·sin(πt/2t_turn), y = R·(1-cos(πt/2t_turn)); R = 6–10m, t_turn = 3–6s

## Simulation Parameters
- Time step: dt = 0.01s (10ms)
- Sub-stepping: 4× for collision accuracy
- Position accuracy: 0.01m; velocity accuracy: 0.001 m/s
- Collision: AABB per-timestep overlap

## Integration Points
| From Skill | Data |
|---|-|
| scenario-taxonomy | Scenario parameters |
| indicator-computation | State arrays → all 42 indicators |
| 3d-animation | Trajectory arrays → 3D positions |
| bayesian-evt | Monte Carlo collision outputs → GPD fits |
| stochastic-simulation | Monte Carlo parameter sampling |

## Cross-Skill Dependencies

- **scenario-taxonomy** (upstream) — scenario parameters and conflict types drive trajectory logic
- **indicator-computation** (downstream) — state arrays feed into all 42 indicator computations
- **stochastic-simulation** (sibling) — Monte Carlo parameter sampling drives simulation runs
- **3d-animation** (downstream) — trajectory arrays become 3D position inputs
- **bayesian-evt** (sibling) — Monte Carlo collision outputs feed into GPD fits
- **risk-quantification** (sibling) — kinematics engine provides trajectory foundation for the full pipeline

## Reference Implementation

Kinematic models are integrated into `src/risk_quantification/pipeline.py` (step 1: kinematics → step 2: indicators).
Per-conflict-type logic referenced in `single-scenario-demo/data/` scenario JSONs.

## Future File Structure (when src/kinematics/ package is created)
```
src/kinematics/
├── model.py           Universal kinematic model
├── vehicles.py        Vehicle trajectories
├── pedestrians.py     Pedestrian trajectories
├── cyclists.py        Cyclist trajectories
├── intersection.py    Intersection geometry
├── scenarios/         Per-conflict-type trajectory logic
│   ├── crossing.py, merging.py, diverging.py, weaving.py
│   ├── rear_end.py, sideswipe.py, right_angle.py, opposing_lt.py
├── collision.py       Collision detection + impact physics
├── indicators.py      All 42 indicator computations
├── simulation.py      Main time-stepping engine
└── validation.py      Validation against analytical/benchmark cases
```
