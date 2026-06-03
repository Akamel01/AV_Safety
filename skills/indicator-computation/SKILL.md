# Skill: Indicator Computation

**Purpose:** Compute all 42 traffic conflict and surrogate safety indicators for every timestep of every simulation run.

## 1. Indicator Architecture

All indicators are organized into 6 categories, each with its own computation module:

```
src/indicators/
├── __init__.py
├── base.py           — Base indicator class with metadata
├── manager.py        — Indicator registry and computation pipeline
├── time_based/       — 11 time-based indicators
│   ├── ttc.py
│   ├── mttc.py
│   ├── pet.py
│   ├── et.py
│   ├── thw.py
│   ├── gap_time.py
│   ├── tet.py
│   ├── tit.py
│   ├── tadv.py
│   ├── pret.py
│   └── worst_ttc.py
├── distance_based/   — 5 distance-based indicators
│   ├── dtc.py
│   ├── psd.py
│   ├── rdcp.py
│   ├── min_spatial_gap.py
│   └── clearance_distance.py
├── deceleration_based/  — 8 deceleration-based indicators
│   ├── drac.py
│   ├── rla.py
│   ├── madr.py
│   ├── drac_diff.py
│   ├── cpi.py
│   ├── max_decel.py
│   ├── avg_decel.py
│   └── dob.py
├── kinematic/        — 5 kinematic indicators
│   ├── delta_v.py
│   ├── closing_speed.py
│   ├── relative_accel.py
│   ├── relative_angle.py
│   └── speed_differential.py
├── severity/         — 6 severity-based indicators
│   ├── delta_v_impact.py
│   ├── expected_severity.py
│   ├── kinetic_energy.py
│   ├── csi.py
│   ├── sri.py
│   └── pce.py
└── probability/      — 6 probability-based indicators
    ├── collision_probability.py
    ├── crash_potential_index.py
    ├── probabilistic_ttc.py
    ├── collision_risk_index.py
    ├── risk_force.py
    └── expected_crash_frequency.py
```

## 2. Base Indicator Class

```python
class Indicator:
    """Base class for all traffic conflict indicators."""
    
    name: str
    category: str  # "time", "distance", "deceleration", "kinematic", "severity", "probability"
    unit: str
    applicable_to: List[str]  # list of conflict types
    formula: str
    references: List[str]
    
    def compute(self, users: List[RoadUser], t: float, trajectory_history: Dict) -> float:
        """Compute indicator value at current timestep."""
        raise NotImplementedError
    
    def compute_over_history(self, trajectory_history: Dict) -> Dict:
        """Compute aggregate statistics over entire simulation history."""
        raise NotImplementedError
```

## 3. All 42 Indicators — Detailed Specs

### 3.1 Time-Based Indicators

#### TTC (Time to Collision)
- **Formula:** `TTC(t) = d(t) / v_rel(t)` when v_rel(t) > 0
- **d(t):** minimum distance between vehicles at time t
- **v_rel(t):** rate of change of d(t) (positive = closing)
- **Valid when:** vehicles are approaching each other (v_rel > 0)
- **References:** Jia & Gerdes (2002), Li et al. (2020)
- **Units:** seconds

#### MTTC (Modified Time to Collision)
- **Formula:** `MTTC(t) = (-v_rel(t) + sqrt(v_rel(t)^2 + 2·a_rel(t)·d(t))) / a_rel(t)`
- **a_rel(t):** relative acceleration
- **Valid when:** a_rel ≠ 0 (accounts for acceleration/deceleration)
- **Units:** seconds

#### PET (Post-Encroachment Time)
- **Formula:** `PET = t_enter2 - t_exit1` for conflict area entry/exit times
- **Valid for:** crossing conflicts only (not for rear-end)
- **Positive PET:** no conflict (safe passage)
- **Negative PET:** actual conflict/overlap in space-time
- **Units:** seconds

#### ET (Encroachment Time)
- **Formula:** `ET = t_exit1 - t_enter1` for a single road user in conflict area
- **Valid when:** user is within conflict zone
- **Units:** seconds

#### THW (Time Headway)
- **Formula:** `THW(t) = (x_lead(t) - x_follow(t) - l_lead) / v_follow(t)`
- **Valid for:** following vehicles in same lane
- **Units:** seconds

#### Gap Time
- **Formula:** `gap_time(t) = (x_ahead(t) - x_behind(t) - l_behind) / v_behind(t)`
- **Similar to THW but for general vehicle pairs**
- **Units:** seconds

#### TET (Time Exposed TTC)
- **Formula:** `TET = Σ dt where TTC(t) < TTC_threshold`
- **Typical threshold:** TTC = 1.5s or 2.0s
- **Aggregation:** Sum of all timesteps where TTC < threshold
- **Units:** seconds

#### TIT (Time Integrated TTC)
- **Formula:** `TIT = ∫(1/TTC(t)) dt` over simulation duration
- **Weighted toward lower TTC values** (more severe conflicts dominate)
- **Aggregation:** Numerical integration (trapezoidal rule)
- **Units:** s⁻¹·s = dimensionless

#### TAdv (Time Advantage)
- **Formula:** `TAdv = t_arrival_A - t_arrival_B` for common conflict point
- **Positive TAdv:** vehicle A has advantage (arrives later or earlier depending on direction)
- **Negative TAdv:** vehicle B has advantage
- **Units:** seconds

#### PrET (Predictive Encroachment Time)
- **Formula:** Extrapolate trajectories forward to predict future PET
- **Method:** Linear prediction using current velocity and acceleration
- **PrET = min(PET_predicted_over_future_horizon)**
- **Horizon:** typically 3-5 seconds
- **Units:** seconds

#### Worst TTC
- **Formula:** `worst_TTC = min(TTC(t))` over simulation
- **Tracks the minimum TTC encountered**
- **Units:** seconds

#### Initial TTC
- **Formula:** `initial_TTC = TTC(t_start)` where t_start is when interaction begins
- **Marks the first computed TTC value**
- **Units:** seconds

### 3.2 Distance-Based Indicators

#### DTC (Distance to Collision)
- **Formula:** `DTC(t) = d(t)·(v_rel(t) / |v_rel(t)|)` when v_rel > 0
- **Physical interpretation:** distance remaining until collision at current approach rate
- **Units:** meters

#### PSD (Proportion of Stopping Distance)
- **Formula:** `PSD = d_available / d_stopping`
- **d_available:** distance to conflict point
- **d_stopping:** braking distance = v² / (2·μ·g) where μ = friction coefficient
- **PSD > 1:** safe (enough distance to stop)
- **PSD < 1:** unsafe (not enough distance to stop)
- **Units:** dimensionless ratio

#### RDCP (Remaining Distance to Conflict Point)
- **Formula:** `RDCP_i(t) = ||p_i(t) - p_conflict||` for each road user
- **p_conflict:** intersection point or closest approach point
- **Units:** meters

#### Minimum Spatial Gap
- **Formula:** `min_gap = min(||p_A(t) - p_B(t)||) over simulation`
- **Tracks the closest approach between two vehicles**
- **Collision threshold:** when gap < (w_A + w_B)/2
- **Units:** meters

#### Clearance Distance
- **Formula:** `clearance = min(||p_A(t) - p_B(t)||) - (w_A/2 + w_B/2)`
- **Positive:** safe clearance
- **Negative:** collision/overlap
- **Units:** meters

### 3.3 Deceleration/Acceleration-Based Indicators

#### DRAC (Deceleration Rate to Avoid Collision)
- **Formula:** `DRAC(t) = (v_A(t)² - v_B(t)²) / (2·(x_B(t) - x_A(t) - l_A))`
- **Interpretation:** required deceleration for following vehicle to avoid rear-end collision
- **Negative DRAC:** collision already imminent (cannot avoid)
- **Units:** m/s²

#### RLA (Required Longitudinal Acceleration)
- **Formula:** `RLA = v_required - v_current / dt`
- **v_required:** velocity needed to reach conflict point at safe time
- **Units:** m/s²

#### MADR (Maximum Available Deceleration Rate)
- **Formula:** `MADR = μ·g` where μ = friction coefficient, g = 9.81 m/s²
- **Typical values:**
  - Dry pavement: μ = 0.7-0.9, MADR = 6.9-8.8 m/s²
  - Wet pavement: μ = 0.4-0.5, MADR = 3.9-4.9 m/s²
  - Icy: μ = 0.1-0.2, MADR = 1.0-2.0 m/s²
- **Units:** m/s²

#### DRAC-MADR Difference
- **Formula:** `safety_margin = MADR - DRAC`
- **Positive:** sufficient braking capability
- **Negative:** required braking exceeds capability (collision likely)
- **Units:** m/s²

#### CPI (Crash Potential Index)
- **Formula:** `CPI = P(DRAC > MADR)` — probability that required deceleration exceeds available
- **Simplified:** `CPI = max(0, DRAC/MADR - 1)`
- **Range:** [0, 1]
- **CPI = 0:** no crash potential
- **CPI = 1:** certain crash (DRAC >> MADR)
- **Units:** dimensionless probability

#### Max Deceleration
- **Formula:** `max_decel = max(|a(t)|) where a(t) < 0` over simulation
- **Tracks the peak braking effort observed**
- **Units:** m/s²

#### Average Deceleration
- **Formula:** `avg_decel = mean(|a(t)|) where a(t) < 0` over simulation
- **Units:** m/s²

#### DOB (Deceleration Occurrence caused by Braking)
- **Formula:** Count of harsh braking events (|a| > threshold) / total simulation time
- **Harsh braking threshold:** typically |a| > 4.0 m/s²
- **Units:** events/second or events/hour

### 3.4 Kinematic Indicators

#### Delta-V (Relative Speed)
- **Formula:** `delta_v = ||v_A - v_B||` at impact or at any timestep
- **At collision:** this is the speed difference at moment of impact
- **Used as primary severity predictor**
- **Units:** m/s

#### Closing Speed
- **Formula:** `closing_speed = -d(||p_A - p_B||)/dt = -v_rel · cos(θ)` where θ is angle between velocity and separation vector
- **Positive:** vehicles approaching
- **Negative:** vehicles separating
- **Units:** m/s

#### Relative Acceleration
- **Formula:** `relative_accel = ||a_A - a_B||`
- **Units:** m/s²

#### Relative Direction Angle
- **Formula:** `angle = arccos((v_A · v_B) / (|v_A| · |v_B|))`
- **0°:** same direction
- **90°:** orthogonal
- **180°:** opposing
- **Units:** degrees

#### Speed Differential
- **Formula:** `speed_diff = |v_A - v_B|` for vehicles in same or adjacent lanes
- **Used to assess lane-changing safety**
- **Units:** m/s

### 3.5 Severity-Based Indicators

#### Delta-V at Impact
- **Formula:** Same as delta_v but specifically at the moment of collision
- **Directly correlates with injury severity**
- **Reference:** NHTSA ES-28 crashworthiness correlation
- **Units:** m/s

#### Expected Collision Severity
- **Formula:** `severity = f(delta_v, impact_angle, vehicle_mass_ratio)`
- **Based on:** NHTSA BANSYSE injury probability models
- **Output:** probability of MAIS 3+ (serious injury) or fatality
- **Units:** probability [0, 1]

#### Kinetic Energy at Conflict
- **Formula:** `KE = ½·μ_eff·delta_v²` where μ_eff = reduced mass = (m_A·m_B)/(m_A+m_B)
- **Units:** Joules

#### CSI (Conflict Severity Index)
- **Formula:** `CSI = (delta_v^n) / (time_exposure)` for some power n (typically 2-3)
- **Weighted measure combining exposure and severity**
- **Units:** m/sⁿ·s⁻¹

#### SRI (Severity Rate Index)
- **Formula:** `SRI = Σ (severity_i × weight_i) / total_events`
- **severity_i:** individual event severity (e.g., delta_v)
- **weight_i:** weighting factor (e.g., based on time exposure)
- **Units:** weighted average

#### PCE (Potential Collision Energy)
- **Formula:** `PCE = ½·μ_eff·delta_v²` (same as kinetic energy)
- **Estimates energy transfer during hypothetical crash**
- **Units:** Joules

### 3.6 Probability-Based Indicators

#### CP (Collision Probability)
- **Formula:** `CP = P(collision | current_state)` estimated from trajectory predictions
- **Method:** Monte Carlo simulation of future trajectories with uncertainty
- **Output:** probability [0, 1]
- **Units:** probability

#### Crash Potential Index (CPI) — from deceleration category
- See DRAC-MADR section above
- **Range:** [0, 1]
- **Units:** probability

#### Probabilistic TTC
- **Formula:** `pTTT(t) = P(TTC(t) < TTC_threshold | uncertainties)`
- **Accounts for uncertainty in trajectory predictions**
- **Method:** Sample from uncertainty distributions, compute TTC distribution, estimate CDF
- **Units:** probability

#### Collision Risk Index
- **Formula:** `CRI = CP × ExpectedSeverity`
- **Combined probability and severity metric**
- **Range:** [0, ∞) (higher = more risky)
- **Units:** composite

#### Risk Force
- **Formula:** `RiskForce = momentum × curvature_of_trajectory`
- **Based on:** risk field theory — vehicles create "risk fields" that extend based on speed and direction
- **Higher speed + sharper turn = larger risk field**
- **Units:** N·m (force-moment)

#### Expected Crash Frequency
- **Formula:** `ECF = Σ P(collision_i) over all conflict pairs over time horizon`
- **Aggregates individual collision probabilities across all vehicle pairs**
- **Units:** crashes per hour or per simulation

---

## 4. Indicator Aggregation Strategy

### 4.1 Per-Timestep Computation
At each simulation timestep (dt = 10ms):
```
For each vehicle pair:
    for indicator in applicable_indicators:
        value = indicator.compute(state, t)
        store(t, pair_index, indicator_name, value)
```

### 4.2 Aggregation Over Simulation
```
For each indicator over full simulation:
    worst_value = min/max (depending on indicator)
    mean_value = mean(values)
    median_value = median(values)
    p5, p25, p75, p95 = percentiles
    time_exposed = count(valid values) / total_steps
```

### 4.3 Indicator Applicability Matrix

| Indicator | Crossing | Merging | Diverging | Weaving | Rear-end | Sideswipe | Right-angle | Opp LT |
|---|---|---|---|---|---|---|---|---|
| TTC | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ | ✅ | ✅ |
| MTTC | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ | ✅ | ✅ |
| PET | ✅✅ | ⚠️ | ⚠️ | ❌ | ❌ | ⚠️ | ✅✅ | ✅ |
| THW | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅✅ | ❌ | ❌ | ⚠️ |
| DRAC | ❌ | ✅ | ✅ | ✅ | ✅✅ | ✅ | ❌ | ✅ |
| Delta-V | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ |
| CPI | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ | ✅ | ✅ |
| PCE | ✅✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ |
| CP | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ |
| CSI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SRI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RiskForce | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Implementation Details

### 5.1 Unit Conversion
All indicators must track their unit and convert consistently:
```python
class Indicator:
    def compute(self, users, t, trajectory_history):
        # All inputs in SI units (meters, m/s, m/s²)
        # Return value in standard unit for this indicator
        # If custom units requested, convert
        ...
```

### 5.2 NaN/Inf Handling
```python
# Handle division by zero in TTC
if v_rel <= 0:
    return float('inf')  # not approaching

# Handle NaN from sqrt of negative
if discriminant < 0:
    return float('inf')  # no collision possible
```

### 5.3 Performance Optimization
- Vectorize computation using numpy arrays
- Batch indicator computations for same timestep
- Cache computed values to avoid recomputation
- Use sparse storage for indicator history (only store non-nan values)

### 5.4 Reference Data

**Vehicle dimensions (NHTSA):**
- Compact car: L=4.3m, W=1.8m, M=1200kg
- Mid-size car: L=4.7m, W=1.85m, M=1400kg
- SUV: L=4.8m, W=2.0m, M=1800kg
- Pick-up: L=5.5m, W=2.1m, M=2200kg
- Heavy truck: L=12.0m, W=2.6m, M=18000kg
- Pedestrian: mass=70kg, height=1.7m
- Cyclist: mass=80kg (person+bike), bike L=1.7m, W=0.7m

**Friction coefficients:**
- Dry asphalt: 0.7-0.9
- Wet asphalt: 0.4-0.5
- Snow: 0.1-0.3
- Ice: 0.05-0.15
