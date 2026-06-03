# Skill: Kinematics Engine

**Purpose:** Compute exact trajectories, positions, and velocities for all road users in every conflict type scenario.

## Overview

Every scenario in the playground is driven by kinematic simulations. This skill defines the universal kinematic model and provides per-conflict-type trajectory computation logic.

---

## 1. Universal Kinematic Model

### 1.1 State Representation

Each road user `i` is tracked by:
```
State_i(t) = {
    position: (x_i(t), y_i(t))    // meters, in global reference frame
    velocity: v_i(t)                // m/s, speed magnitude
    heading: θ_i(t)                 // radians, angle from +x axis
    acceleration: a_i(t)            // m/s², tangential
    jerk: j_i(t)                    // m/s³, for smooth transitions
}
```

### 1.2 Vehicle Models

| Model | Position Update | Max Acceleration | Max Deceleration | Max Jerk |
|---|---|---|---|---|
| **Constant velocity** | x(t) = x₀ + v·t, y(t) = y₀ | 0 | 0 | 0 |
| **Constant acceleration** | x(t) = x₀ + v₀·t + ½a·t² | ±5 m/s² | -8 m/s² | 3 m/s³ |
| **Pacejka tire model** | Full dynamics with slip angle | ±6 m/s² | -10 m/s² | 5 m/s³ |
| **Bicycle model** | Single-track model with steering | ±5 m/s² | -8 m/s² | 4 m/s³ |
| **Pedestrian** | Bipedal with stride limits | ±1.5 m/s² | -3 m/s² | 2 m/s³ |
| **Cyclist** | Bicycle with lean angle | ±2 m/s² | -6 m/s² | 3 m/s³ |

### 1.3 Pedestrian Model
```
Stride length: 0.75 m at 1.4 m/s (normal walking)
Max speed: 2.2 m/s (brisk walking), 3.5 m/s (running)
Turning radius: 0.3 m (normal), 0.15 m (emergency)
Acceleration: max ±1.5 m/s²
Reaction time: 0.25s (perception) + 0.75s (response) = 1.0s typical
```

### 1.4 Cyclist Model
```
Cruising speed: 4-6 m/s (urban), 8-12 m/s (highway)
Sprint speed: up to 15 m/s
Braking distance: 3-5 m at 12 m/s (good pavement)
Turning radius: ≥2.0 m (normal), 1.0 m (emergency)
Acceleration: max ±2 m/s²
```

---

## 2. Per-Conflict-Type Trajectory Logic

### 2.1 Crossing Conflicts

**Geometry:**
- Two vehicles approach intersection at 90° (or specified angle α)
- Intersection center at origin (0, 0)
- Vehicle A: moving along -x → +x, crossing at y = 0
- Vehicle B: moving along -y → +y, crossing at x = 0

**Collision condition:**
```
If |x_A(t_coll) - x_B(t_coll)| < (w_A + w_B)/2
AND |y_A(t_coll) - y_B(t_coll)| < (l_A + l_B)/2
then collision
where w = vehicle width, l = vehicle length
```

**Trajectory phases:**
1. **Approach:** Constant speed (or with braking) until intersection approach zone
2. **Decision point:** At distance D_decision from intersection (reaction time boundary)
3. **Action:** Three branches:
   - Brake: decelerate to stop before intersection
   - Accelerate: increase speed to clear intersection before B arrives
   - Proceed: maintain speed through intersection
4. **Post-conflict:** Either clear or collide

**Key parameters:**
- `v_A_initial, v_B_initial` — approach speeds
- `D_A_start, D_B_start` — initial distances from intersection
- `reaction_time_A, reaction_time_B` — per driver
- `brake_capacity_A, brake_capacity_B` — max deceleration
- `road_friction` — μ for braking calculations
- `intersection_angle` — 90° standard, configurable

### 2.2 Merging Conflicts (Cut-in)

**Geometry:**
- Two vehicles in adjacent lanes or lane + ramp
- Vehicle A: lead vehicle, constant lane
- Vehicle B: cutting-in vehicle, lateral movement into A's lane

**Trajectory for cut-in vehicle:**
```
Lane change: y_B(t) = y_B0 + Δy·f(t)
where f(t) = (t/t_change)² for t < t_change (quadratic merge)
         f(t) = 1 for t ≥ t_change
Δy = lane_width (typical 3.5m lane change)
t_change = 2-4 seconds (typical lane change time)
```

**Collision condition:**
```
When vehicles share the same lane:
|x_A(t) - x_B(t)| < (l_A + l_B)/2 AND |y_A(t) - y_B(t)| < (w_A + w_B)/2
```

**Key parameters:**
- `v_A, v_B` — speeds
- `D_gap` — initial longitudinal gap (A ahead of B)
- `Δy` — lateral offset for lane change
- `t_change` — lane change duration
- `reaction_time_B` — how long before B starts merging
- `a_B_accel` — acceleration during merge

### 2.3 Diverging Conflicts (Lane Exit)

**Geometry:**
- Vehicle exits its lane (right lane to off-ramp)
- May conflict with adjacent lane traffic

**Trajectory for exiting vehicle:**
```
Lane exit: y_exiting(t) = y0 - Δy·f(t)  // moving right (negative y)
Decceleration: v(t) = v0 - a_brake·(t - t_start)
Off-ramp curve: x(t) = R·sin(θ(t)), y(t) = R·cos(θ(t))  // circular arc exit
R = exit radius (typically 30-50m for highway exits)
```

### 2.4 Weaving Conflicts

**Geometry:**
- Multiple vehicles in a weave section between closely spaced ramps
- Vehicle A: lane change from left to right
- Vehicle B: lane change from right to left (opposite direction)
- Conflict occurs when both change lanes simultaneously

**Trajectory for weaving vehicles:**
```
Vehicle A: y_A(t) = y_A0 + Δy·g_A(t)
Vehicle B: y_B(t) = y_B0 - Δy·g_B(t)
where g(t) = 0.5 - 0.5·cos(π·t/t_weave)  // sinusoidal lane change
```

**Collision condition:**
```
When vehicles' lateral positions overlap:
|x_A - x_B| < safety_gap AND |y_A - y_B| < (w_A + w_B)/2
safety_gap = minimum longitudinal spacing for safe lane change
```

### 2.5 Rear-End Conflicts

**Geometry:**
- Two vehicles in same lane, following relationship
- Vehicle A: lead (can decelerate)
- Vehicle B: following (reacts with delay)

**Trajectory for following vehicle with reaction delay:**
```
For t < reaction_time: v_B(t) = v_B0 (no reaction yet)
For t ≥ reaction_time: v_B(t) = v_B0 + a_brake_B·(t - reaction_time)
a_brake_B = min(brake_capacity, required_braking)
required_braking = (v_B² - v_rel²) / (2·d_remaining)
where d_remaining = x_A(t) - x_B(t) - l_A
```

**Collision condition:**
```
|x_A(t) - x_B(t)| ≤ (l_A + l_B)/2
```

**Critical scenario: cut-under**
```
B merges into A's lane at very short distance
x_A(t_collide) - x_B(t_collide) < l_A
This creates a sideswipe or T-bone if angles differ
```

### 2.6 Sideswipe Conflicts

**Geometry:**
- Two vehicles in adjacent or same lane
- Minimum lateral gap = (w_A + w_B)/2

**Collision condition:**
```
|x_A(t) - x_B(t)| < clearance_threshold (e.g., 3·length of one vehicle)
AND |y_A(t) - y_B(t)| < (w_A + w_B)/2
AND Δv_lateral = |v_A_lat(t) - v_B_lat(t)| > 0.5 m/s
```

**Sideswipe variant: lane-change induced**
```
Vehicle B starts lane change toward A
If gap < critical_gap:
    critical_gap = v_B_lat × reaction_time_B + 0.5 × a_brake_B × reaction_time_B²
Then sideswipe occurs if A doesn't brake or accelerate away
```

### 2.7 Right-Angle Conflicts

**Geometry:**
- Intersection approach (same as crossing) but focus on perpendicular impact
- Vehicle A enters from north, B from east (or vice versa)
- Intersection width W_int (typically 10-15m)

**Collision condition:**
```
Vehicles' bounding boxes overlap at any point within intersection
Bounding box for vehicle at (x,y), heading θ, length l, width w:
x_extent = [x - l/2·cos(θ) - w/2·sin(θ), x + l/2·cos(θ) + w/2·sin(θ)]
y_extent = [y - l/2·sin(θ) + w/2·cos(θ), y + l/2·sin(θ) - w/2·cos(θ)]
Collision when x_extents and y_extents both overlap
```

**Critical scenario: red-light running**
```
Vehicle A runs red: proceeds through intersection without stopping
Vehicle B has green but is too far/slow to stop
A's time to intersection: t_A = D_A / v_A
B's time to intersection: t_B = D_B / v_B
Collision if |t_A - t_B| < conflict_duration (typically 1-2s)
```

### 2.8 Opposing Left-Turn Conflicts

**Geometry:**
- Vehicle A: turning left across opposing traffic (or into opposing lane)
- Vehicle B: oncoming, heading straight (or also turning)
- Intersection center as reference

**Trajectory for left-turn vehicle:**
```
Turning path (approximate):
x_A(t) = R_turn · sin(π·t/(2·t_turn))
y_A(t) = R_turn · (1 - cos(π·t/(2·t_turn)))
R_turn = turning radius (typically 6-10m for standard intersection)
t_turn = time to complete turn (typically 3-6s)
```

**Collision condition:**
```
When turning path intersects oncoming path:
Oncoming: x_B(t) = x_B0 - v_B·t, y_B(t) = y_B0
Overlap when turning path and oncoming path share space simultaneously
```

---

## 3. Trajectory Computation Pipeline

### 3.1 Time-stepping Engine

```python
# Simulation parameters
dt = 0.01  # 10ms timestep (high fidelity for animation)
t_max = 10.0  # max simulation duration
t_start = 0.0

# Main loop
t = t_start
while t <= t_max:
    for each road user i:
        if i.state.has_been_updated:
            # Update based on current control inputs
            i.state = kinematic_update(i.state, dt, i.controls)
        else:
            i.state = kinematic_default(i.state, dt)
    
    # Check collision at this timestep
    if check_collisions(all_users):
        collision_found = True
        collision_time = t
        break
    
    # Compute indicators at this timestep
    indicators = compute_indicators(all_users, t)
    store_indicators(t, indicators)
    
    t += dt
```

### 3.2 Collision Detection Method

```python
def check_collisions(users):
    for pair in all_pairs(users):
        # Get bounding boxes at current timestep
        box_A = get_bounding_box(pair[0].state)
        box_B = get_bounding_box(pair[1].state)
        
        # AABB overlap test
        if (box_A.min_x < box_B.max_x and box_A.max_x > box_B.min_x and
            box_A.min_y < box_B.max_y and box_A.max_y > box_B.min_y):
            return True, pair, current_timestep
        
    return False, None, None
```

### 3.3 Indicator Computation at Each Timestep

```python
def compute_indicators(users, t):
    indicators = {}
    
    # Time-based
    indicators['TTC'] = compute_TTC(users)
    indicators['PET'] = compute_PET(users)
    indicators['TET'] = compute_TET(users)
    indicators['TIT'] = compute_TIT(users)
    indicators['THW'] = compute_THW(users)
    
    # Distance-based
    indicators['DTC'] = compute_DTC(users)
    indicators['min_spatial_gap'] = compute_min_spatial_gap(users)
    
    # Deceleration-based
    indicators['DRAC'] = compute_DRAC(users)
    indicators['RLA'] = compute_RLA(users)
    
    # Kinematic
    indicators['delta_v'] = compute_delta_v(users)
    indicators['closing_speed'] = compute_closing_speed(users)
    
    # Severity
    indicators['kinetic_energy'] = compute_kinetic_energy(users)
    indicators['PCE'] = compute_PCE(users)
    
    # Probability
    indicators['CP'] = compute_collision_probability(users)
    
    return indicators
```

---

## 4. File Structure

```
src/kinematics/
├── __init__.py
├── model.py           — Universal kinematic model classes
├── vehicles.py        — Vehicle trajectory computation
├── pedestrians.py     — Pedestrian trajectory computation
├── cyclists.py        — Cyclist trajectory computation
├── intersection.py    — Intersection geometry and conflict detection
├── scenarios/
│   ├── __init__.py
│   ├── crossing.py    — Crossing conflict trajectories
│   ├── merging.py     — Merging conflict trajectories
│   ├── diverging.py   — Diverging conflict trajectories
│   ├── weaving.py     — Weaving conflict trajectories
│   ├── rear_end.py    — Rear-end conflict trajectories
│   ├── sideswipe.py   — Sideswipe conflict trajectories
│   ├── right_angle.py — Right-angle conflict trajectories
│   └── opposing_lt.py — Opposing left-turn trajectories
├── collision.py       — Collision detection and impact physics
├── indicators.py      — All 42 indicator computations
├── simulation.py      — Main simulation engine (time-stepping)
└── validation.py      — Validate trajectories against known cases
```

---

## 5. Validation Requirements

Each trajectory model must be validated against:

1. **Analytical solutions** — For constant velocity case, TTC = d/v_rel has closed-form solution
2. **Published benchmarks** — Compare against NHTSA crash reconstruction examples
3. **Known edge cases** — Zero speed, infinite distance, parallel paths
4. **Cross-validation** — Two independent implementations produce same results

---

## 6. Integration Points

- **Scenario taxonomy skill:** Takes scenario parameters from taxonomy, feeds into kinematic model
- **Indicator computation skill:** Receives state arrays from kinematic engine, computes all 42 indicators
- **3D animation skill:** Receives trajectory arrays, maps to 3D positions for rendering
- **Bayesian EVT skill:** Receives Monte Carlo outputs (trajectory collisions), fits GPD to extreme values
- **Stochastic simulation skill:** Drives Monte Carlo parameter sampling, calls kinematic engine for each run

---

## 7. Precision Requirements

- Position accuracy: 0.01m (for smooth animation)
- Velocity accuracy: 0.001 m/s (for indicator precision)
- Time step: 10ms (dt = 0.01s) for smooth physics
- Collision detection: per-timestep with AABB overlap
- Sub-stepping: Use 4 sub-steps per timestep for collision accuracy
- Impact velocity: computed at collision instant (interpolated between timesteps)
