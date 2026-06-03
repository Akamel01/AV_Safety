# Per-Conflict-Type Trajectory Formulas

## 1. Crossing Conflicts

### Geometry
- Intersection center at origin (0, 0)
- Vehicle A: -x → +x, crossing at y = 0
- Vehicle B: -y → +y, crossing at x = 0

### Collision Condition
```
|x_A(t) - x_B(t)| < (w_A + w_B)/2
AND |y_A(t) - y_B(t)| < (l_A + l_B)/2
```

### Trajectory Phases
1. Approach: constant speed until intersection approach zone
2. Decision point: at distance D_decision from intersection (reaction time boundary)
3. Action: brake / accelerate / proceed
4. Post-conflict: clear or collide

### Key Parameters
- v_A_initial, v_B_initial — approach speeds
- D_A_start, D_B_start — initial distances from intersection
- reaction_time_A/B — per driver
- brake_capacity_A/B — max deceleration
- road_friction — μ for braking
- intersection_angle — 90° standard, configurable

---

## 2. Merging Conflicts (Cut-in)

### Lane Change Formula
```
y_B(t) = y_B0 + Δy·f(t)
f(t) = (t/t_change)²  for t < t_change
f(t) = 1              for t ≥ t_change
Δy = lane_width (3.5m)
t_change = 2–4s
```

### Collision Condition (same lane)
```
|x_A(t) - x_B(t)| < (l_A + l_B)/2
AND |y_A(t) - y_B(t)| < (w_A + w_B)/2
```

### Key Parameters
- v_A, v_B — speeds
- D_gap — initial longitudinal gap (A ahead of B)
- Δy — lateral offset
- t_change — lane change duration
- reaction_time_B — how long before B merges
- a_B_accel — acceleration during merge

---

## 3. Diverging Conflicts (Lane Exit)

### Exiting Vehicle
```
Lane exit: y(t) = y0 - Δy·f(t)  // moving right (negative y)
Decceleration: v(t) = v0 - a_brake·(t - t_start)
Off-ramp curve: x(t) = R·sin(θ(t)), y(t) = R·cos(θ(t))  // circular arc
R = 30–50m for highway exits
```

---

## 4. Weaving Conflicts

### Lane Change (Sinusoidal)
```
Vehicle A: y_A(t) = y_A0 + Δy·g_A(t)
Vehicle B: y_B(t) = y_B0 - Δy·g_B(t)
g(t) = 0.5 - 0.5·cos(π·t/t_weave)
```

### Collision Condition
```
|x_A - x_B| < safety_gap
AND |y_A - y_B| < (w_A + w_B)/2
```

---

## 5. Rear-End Conflicts

### Following Vehicle with Reaction Delay
```
For t < reaction_time: v_B(t) = v_B0
For t ≥ reaction_time: v_B(t) = v_B0 + a_brake_B·(t - reaction_time)
required_braking = (v_B² - v_rel²) / (2·d_remaining)
d_remaining = x_A(t) - x_B(t) - l_A
```

### Critical: Cut-under
```
x_A(t_collide) - x_B(t_collide) < l_A
Creates sideswipe or T-bone if angles differ
```

---

## 6. Sideswipe Conflicts

### Collision Condition
```
|x_A(t) - x_B(t)| < clearance_threshold (~3× vehicle length)
AND |y_A(t) - y_B(t)| < (w_A + w_B)/2
AND Δv_lateral > 0.5 m/s
```

### Lane-change Induced
```
critical_gap = v_B_lat × reaction_time_B + 0.5 × a_brake_B × reaction_time_B²
Sideswipe if gap < critical_gap and A doesn't brake/accelerate
```

---

## 7. Right-Angle Conflicts

### Bounding Box Collision
```
x_extent = [x - l/2·cos(θ) - w/2·sin(θ), x + l/2·cos(θ) + w/2·sin(θ)]
y_extent = [y - l/2·sin(θ) + w/2·cos(θ), y + l/2·sin(θ) - w/2·cos(θ)]
Collision when x_extents AND y_extents both overlap
```

### Red-Light Running Time Gap
```
t_A = D_A / v_A (A's time to intersection)
t_B = D_B / v_B (B's time to intersection)
Collision if |t_A - t_B| < conflict_duration (typically 1–2s)
```

---

## 8. Opposing Left-Turn Conflicts

### Turning Path
```
x_A(t) = R_turn · sin(π·t/(2·t_turn))
y_A(t) = R_turn · (1 - cos(π·t/(2·t_turn)))
R_turn = 6–10m; t_turn = 3–6s
```

### Collision Condition
```
Oncoming: x_B(t) = x_B0 - v_B·t, y_B(t) = y_B0
Overlap when turning path and oncoming path share space simultaneously
```
