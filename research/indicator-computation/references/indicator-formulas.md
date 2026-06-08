# All 42 Indicator Formulas

## 3.1 Time-Based Indicators (11)

### TTC (Time to Collision)
- **Formula:** `TTC(t) = d(t) / v_rel(t)` when v_rel(t) > 0
- **d(t):** minimum distance between vehicles
- **v_rel(t):** rate of change of d(t) (positive = closing)
- **Units:** seconds
- **References:** Jia & Gerdes (2002), Li et al. (2020)

### MTTC (Modified Time to Collision)
- **Formula:** `MTTC(t) = (-v_rel + sqrt(v_rel² + 2·a_rel·d)) / a_rel`
- **a_rel:** relative acceleration
- **Valid when:** a_rel ≠ 0
- **Units:** seconds

### PET (Post-Encroachment Time)
- **Formula:** `PET = t_enter2 - t_exit1` for conflict area entry/exit times
- **Valid for:** crossing conflicts (not rear-end)
- **Positive:** safe; **Negative:** conflict
- **Units:** seconds

### ET (Encroachment Time)
- **Formula:** `ET = t_exit1 - t_enter1` for a road user in conflict area
- **Units:** seconds

### THW (Time Headway)
- **Formula:** `THW = (x_lead - x_follow - l_lead) / v_follow`
- **Valid for:** following vehicles in same lane
- **Units:** seconds

### Gap Time
- **Formula:** `gap_time = (x_ahead - x_behind - l_behind) / v_behind`
- **Similar to THW for general pairs**
- **Units:** seconds

### TET (Time Exposed TTC)
- **Formula:** `TET = Σ dt where TTC(t) < TTC_threshold`
- **Threshold:** 1.5s or 2.0s
- **Units:** seconds

### TIT (Time Integrated TTC)
- **Formula:** `TIT = ∫(1/TTC(t)) dt` over simulation duration
- **Weighted toward lower TTC**
- **Units:** dimensionless

### TAdv (Time Advantage)
- **Formula:** `TAdv = t_arrival_A - t_arrival_B` for common conflict point
- **Positive:** A has advantage
- **Units:** seconds

### PrET (Predictive Encroachment Time)
- **Formula:** Extrapolate trajectories forward, `PrET = min(PET_predicted)` over 3–5s horizon
- **Units:** seconds

### Worst TTC
- **Formula:** `worst_TTC = min(TTC(t))` over simulation
- **Units:** seconds

### Initial TTC
- **Formula:** `initial_TTC = TTC(t_start)` where interaction begins
- **Units:** seconds

## 3.2 Distance-Based Indicators (5)

### DTC (Distance to Collision)
- **Formula:** `DTC = d(t)·(v_rel / |v_rel|)` when v_rel > 0
- **Units:** meters

### PSD (Proportion of Stopping Distance)
- **Formula:** `PSD = d_available / d_stopping` where `d_stopping = v² / (2·μ·g)`
- **PSD > 1:** safe; **PSD < 1:** unsafe
- **Units:** dimensionless

### RDCP (Remaining Distance to Conflict Point)
- **Formula:** `RDCP_i = ||p_i - p_conflict||`
- **Units:** meters

### Minimum Spatial Gap
- **Formula:** `min_gap = min(||p_A(t) - p_B(t)||)` over simulation
- **Collision threshold:** gap < (w_A + w_B)/2
- **Units:** meters

### Clearance Distance
- **Formula:** `clearance = min(||p_A - p_B||) - (w_A/2 + w_B/2)`
- **Positive:** safe; **Negative:** collision
- **Units:** meters

## 3.3 Deceleration-Based Indicators (8)

### DRAC (Deceleration Rate to Avoid Collision)
- **Formula:** `DRAC = (v_A² - v_B²) / (2·(x_B - x_A - l_A))`
- **Negative DRAC:** collision imminent
- **Units:** m/s²

### RLA (Required Longitudinal Acceleration)
- **Formula:** `RLA = (v_required - v_current) / dt`
- **Units:** m/s²

### MADR (Maximum Available Deceleration Rate)
- **Formula:** `MADR = μ·g`
- **Dry pavement:** 6.9–8.8 m/s²; **Wet:** 3.9–4.9; **Icy:** 1.0–2.0
- **Units:** m/s²

### DRAC-MADR Difference
- **Formula:** `safety_margin = MADR - DRAC`
- **Positive:** sufficient; **Negative:** collision likely
- **Units:** m/s²

### CPI (Crash Potential Index)
- **Formula:** `CPI = P(DRAC > MADR)` → simplified: `max(0, DRAC/MADR - 1)`
- **Range:** [0, 1]
- **Units:** probability

### Max Deceleration
- **Formula:** `max_decel = max(|a(t)|) where a(t) < 0`
- **Units:** m/s²

### Average Deceleration
- **Formula:** `avg_decel = mean(|a(t)|) where a(t) < 0`
- **Units:** m/s²

### DOB (Deceleration Occurrence caused by Braking)
- **Formula:** Count of harsh braking events (|a| > 4.0 m/s²) / total time
- **Units:** events/second or events/hour

## 3.4 Kinematic Indicators (5)

### Delta-V (Relative Speed)
- **Formula:** `delta_v = ||v_A - v_B||` at any timestep
- **Primary severity predictor**
- **Units:** m/s

### Closing Speed
- **Formula:** `closing_speed = -v_rel · cos(θ)` where θ = angle between velocity and separation
- **Positive:** approaching; **Negative:** separating
- **Units:** m/s

### Relative Acceleration
- **Formula:** `relative_accel = ||a_A - a_B||`
- **Units:** m/s²

### Relative Direction Angle
- **Formula:** `angle = arccos((v_A · v_B) / (|v_A| · |v_B|))`
- **0°:** same direction; **90°:** orthogonal; **180°:** opposing
- **Units:** degrees

### Speed Differential
- **Formula:** `speed_diff = |v_A - v_B|` for same/adjacent lanes
- **Units:** m/s

## 3.5 Severity Indicators (6)

### Delta-V at Impact
- **Formula:** Same as delta_v at collision moment
- **Directly correlates with injury severity (NHTSA ES-28)**
- **Units:** m/s

### Expected Collision Severity
- **Formula:** `severity = f(delta_v, impact_angle, vehicle_mass_ratio)`
- **Based on:** NHTSA BANSYSE injury probability models
- **Output:** probability of MAIS 3+ or fatality
- **Units:** probability [0, 1]

### Kinetic Energy at Conflict
- **Formula:** `KE = ½·μ_eff·delta_v²` where μ_eff = (m_A·m_B)/(m_A+m_B)
- **Units:** Joules

### CSI (Conflict Severity Index)
- **Formula:** `CSI = delta_v^n / time_exposure` (n typically 2–3)
- **Weighted measure combining exposure and severity**
- **Units:** m/sⁿ·s⁻¹

### SRI (Severity Rate Index)
- **Formula:** `SRI = Σ(severity_i × weight_i) / total_events`
- **Units:** weighted average

### PCE (Potential Collision Energy)
- **Formula:** `PCE = ½·μ_eff·delta_v²` (same as kinetic energy)
- **Units:** Joules

## 3.6 Probability Indicators (6)

### CP (Collision Probability)
- **Formula:** `CP = P(collision | current_state)` from Monte Carlo trajectory predictions
- **Range:** [0, 1]
- **Units:** probability

### CPI (from deceleration)
- **See DRAC-MADR section** above
- **Range:** [0, 1]

### Probabilistic TTC (pTTT)
- **Formula:** `pTTT(t) = P(TTC(t) < TTC_threshold | uncertainties)`
- **Method:** Sample from uncertainty distributions, estimate CDF
- **Units:** probability

### CRI (Collision Risk Index)
- **Formula:** `CRI = CP × ExpectedSeverity`
- **Combined probability and severity**
- **Range:** [0, ∞)
- **Units:** composite

### Risk Force
- **Formula:** `RiskForce = momentum × curvature_of_trajectory`
- **Based on:** risk field theory
- **Units:** N·m (force-moment)

### Expected Crash Frequency (ECF)
- **Formula:** `ECF = Σ P(collision_i)` over all conflict pairs over time horizon
- **Units:** crashes per hour or per simulation
