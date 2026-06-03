# Investigation Plan: AV_Safety Collision Risk Playground

**Date:** 2026-06-02
**Goal:** Produce a project blueprint from this investigation, deriving refined scope, goals, and requirements.

---

## Phase 1: Problem Deconstruction

### Task 1.1: Define the playground's core interaction model
- Determine user controls (sliders, inputs) per scenario type
- Map severity parameters to their physical meaning and units
- Define the "severity spectrum" for each conflict type (benign → catastrophic)
- Identify which indicators to compute per conflict type and which are universal

**Evidence needed:** None — this is design work. But we must avoid designing indicators that are meaningless for certain conflict types (e.g., PET is irrelevant for rear-end conflicts).

### Task 1.2: Conflict type × scenario sub-category taxonomy
Build the full taxonomy mapping:

```
Crossing:
  - Intersection crossing (perpendicular)
  - Mid-block crossing (jaywalking, crosswalk)
  - Signalized vs unsignalized

Merging:
  - Lane addition (on-ramp)
  - Lane change (cut-in from adjacent lane)
  - Merging from shoulder

Diverging:
  - Lane exit (off-ramp)
  - Lane change (outbound)

Weaving:
  - Short weave (between closely spaced ramps)
  - Long weave (between distant ramps)
  - Single-vehicle weave vs multi-vehicle

Rear-end:
  - Following scenario (constant gap)
  - Cut-in (vehicle merges ahead)
  - Sudden braking (lead decelerates rapidly)
  - Cut-under (vehicle merges in front at close range)

Sideswipe:
  - Same-direction sideswipe
  - Lane-change induced sideswipe
  - Merging sideswipe

Right-angle:
  - Intersection right-angle (cross-traffic)
  - T-bone at stop sign
  - T-bone at signal

Opposing left-turn:
  - Unprotected left across opposing traffic
  - Protected left (yield scenario)
  - Opposing vehicle also turning (intersection)
```

**Evidence needed:** Validate that this taxonomy covers the major crash types in NHTSA's FARS/CRSS or equivalent databases. Check what the literature uses as standard categories.

### Task 1.3: Map indicators to conflict types
Determine which indicators apply to which conflict types:

| Conflict Type | TTC | PET | DRAC | Delta-V | CPI | Others |
|---|---|---|---|---|---|---|
| Crossing | ✅ | ✅ | ✅ | ✅ | ✅ | TET, PCE |
| Merging | ✅ | ⚠️ | ✅ | ✅ | ✅ | THW |
| Diverging | ✅ | ⚠️ | ✅ | ✅ | ✅ | THW |
| Weaving | ✅ | ❌ | ✅ | ✅ | ✅ | TIT, CPI |
| Rear-end | ✅ | ❌ | ✅✅ | ✅✅ | ✅✅ | RLA, MADR |
| Sideswipe | ✅ | ⚠️ | ✅ | ✅ | ✅ | PSD |
| Right-angle | ✅ | ✅✅ | ✅ | ✅✅ | ✅✅ | PCE, CSI |
| Opposing LT | ✅ | ✅ | ✅ | ✅ | ✅ | TAdv, RDCP |

**Evidence needed:** Cross-reference with surrogate safety literature (e.g., Hagman et al., Lord & Mannering traffic safety review) to validate indicator applicability per conflict type.

---

## Phase 2: Physics & Kinematics Model

### Task 2.1: Define the kinematic model for each road user
- Position as function of time: `p_i(t) = (x_i(t), y_i(t))`
- Velocity: `v_i(t) = |v_i(t)|` with direction
- Acceleration: `a_i(t) = dv_i/dt`
- Vehicle dimensions: length, width (standard dimensions per type)
- Vehicle types: sedan, SUV, truck (for pedestrian impact severity), bicycle dimensions

**Evidence needed:** Standard vehicle dimensions from NHTSA vehicle classes. Pedestrian mass (~70 kg), cyclist mass (~80 kg with bike).

### Task 2.2: Define collision condition per conflict type
For each conflict type, define the collision geometry:
- **Crossing:** path intersection point, time overlap within collision envelope
- **Rear-end:** x-distance below threshold when leading vehicle is slower
- **Sideswipe:** minimum lateral distance vs combined vehicle widths
- **Right-angle:** intersection collision with orthogonal approach

### Task 2.3: Define the severity spectrum
Severity depends on:
- **Speed differential** (ΔV) at impact
- **Impact angle** (0° = rear-end, 90° = T-bone)
- **Vehicle mass ratio** (heavy vs light vehicle)
- **Occupant protection** (pedestrian = zero protection, cyclist = minimal)
- **Impact location** (front, side, side-rear, roof)

**Evidence needed:** NHTSA crash severity data (BANSYSE, FARS) to link ΔV to injury severity probabilities. ES-28 or similar severity models.

### Task 2.4: Stochastic parameter distributions
For each scenario, define distributions for key parameters:
- Speed: normal or lognormal, with μ, σ per lane/type
- Cut-in distance: exponential or gamma distribution
- Reaction time: lognormal (1.0–2.5s typical)
- Braking delay: lognormal
- Deceleration capability: truncated normal (max ~8-10 m/s² for panic braking)
- Road friction coefficient: uniform or normal (μ = 0.7-0.9 dry, 0.3-0.5 wet)

**Evidence needed:** Literature values for reaction time distributions, braking capabilities, friction coefficients.

---

## Phase 3: Indicator Computation Engine

### Task 3.1: Implement all 42 indicators
Build a modular computation engine where each indicator is a standalone function:
```
src/evaluation/indicators/
  time_based/
    ttc.py
    mttc.py
    pet.py
    tet.py
    tit.py
    thw.py
    gap_time.py
    ...
  distance_based/
    dtc.py
    psd.py
    min_spatial_gap.py
    clearance_distance.py
    ...
  deceleration_based/
    drac.py
    rla.py
    madr.py
    cpi.py
    ...
  kinematic/
    delta_v.py
    closing_speed.py
    relative_accel.py
    ...
  severity/
    delta_v_impact.py
    expected_severity.py
    kinetic_energy.py
    csi.py
    pce.py
    ...
  probability/
    collision_probability.py
    crash_potential.py
    probabilistic_ttc.py
    risk_force.py
    ...
```

### Task 3.2: Indicator applicability matrix
Each indicator has metadata:
```json
{
  "name": "TTC",
  "applicable_to": ["crossing", "rear-end", "right-angle", "opposing-left-turn"],
  "unit": "seconds",
  "formula": "d(t) / (v1(t) - v2(t))",
  "references": ["Jia & Gerdes 2002", "Li et al. 2020"]
}
```

### Task 3.3: Real-time computation during simulation
Indicators computed at each simulation timestep, then aggregated:
- Worst-case (minimum TTC, maximum DRAC)
- Time-exposed (TET: how long TTC < threshold)
- Time-integrated (TIT: integrate 1/TTC over time)
- Statistics (mean, median, percentile)

---

## Phase 4: 3D Animation Engine

### Task 4.1: Technology selection
**Options:**
- **Three.js + JavaScript** — web-native, no backend needed, runs in browser
- **Blender + export** — high quality but static, not interactive
- **Unity WebGL** — powerful but heavy, large bundle
- **Babylon.js** — similar to Three.js, good physics
- **Custom canvas/WebGL** — maximum control but more work

**Recommendation:** Three.js (or Babylon.js) — runs in browser, integrates with portfolio site, allows parameterized animation.

### Task 4.2: 3D scene requirements per conflict type
Each scenario needs:
- **Road geometry** — lanes, markings, intersection shape, signage
- **Road users** — vehicles, pedestrians, cyclists (3D models or simplified meshes)
- **Environment** — weather, lighting (optional for initial version)
- **Animated trajectories** — computed from parameters, with collision or avoidance

### Task 4.3: Collision vs avoidance animation decision
Animation must reflect the computed collision probability:
- **High collision probability (>80%):** show crash (deformation, energy transfer)
- **Medium (20-80%):** show near-miss with evasive action
- **Low (<20%):** show safe pass
- **Stochastic output:** for a given parameter set, run N Monte Carlo sims → show distribution of outcomes (e.g., "72% show collision, 28% safe")

### Task 4.4: Animation fidelity requirements
- Vehicles: simplified but recognizable (box geometry with wheels)
- Road: lane markings, intersection approach geometry
- Pedestrian/cyclist: simplified stick figure or box
- Impact: flash/kinetic energy visualization, debris (optional)
- Labels: real-time indicator display overlaid on animation

---

## Phase 5: Bayesian Hierarchical EVT Risk Quantification

### Task 5.1: EVT framework design
For each conflict type and scenario:

**Likelihood:** Extreme values (near-minimum TTC or maximum DRAC) modeled with Generalized Pareto Distribution (GPD):
```
f(x; ξ, σ) = (1/ξ) * (1 + ξ(x-μ)/σ)^(-(1/ξ+1))
```

**Hierarchical structure:**
- Level 1: Scenario parameters (speed, distance, etc.) → distributions
- Level 2: Conflict type → hyperpriors on GPD parameters
- Level 3: Jurisdiction → hyperpriors on scenario-level priors

**Collision occurrence rate:**
```
λ_collision = P(min(TTC) < TTC_threshold | θ) × exposure_rate
```

**Collision severity distribution:**
```
Severity | Collision ~ GPD(ξ, σ | θ)
```

### Task 5.2: Implementation requirements
```
src/evaluation/bayesian_evt/
  gpd.py           — GPD fitting and sampling
  hierarchical.py  — Bayesian hierarchical model
  collision_rate.py — Occurrence likelihood estimation
  severity_model.py — Severity distribution fitting
  posterior_predictive.py — Validation checks
  crisis.py        — Full risk quantification pipeline
```

**Evidence needed:** Literature on EVT application to traffic conflicts (e.g., Benth et al., Gamage & Tay). Prior specifications from existing crash severity models.

### Task 5.3: Monte Carlo integration
For each scenario parameter set:
1. Sample parameter values from their distributions
2. Compute trajectories and collision outcomes (N ≥ 10,000)
3. Extract extreme values from each run
4. Fit GPD to extreme values
5. Estimate collision rate and severity distribution
6. Compute uncertainty intervals (credible intervals)

---

## Phase 6: Portfolio Integration

### Task 6.1: Playground interface design
- **Left panel:** Scenario selector (conflict type → sub-category → scenario)
- **Center:** 3D animation view with real-time indicator display
- **Right panel:** Parameter sliders, computed indicators, Bayesian results
- **Bottom:** Distribution plots (TTC histogram, severity CDF, posterior)

### Task 6.2: Technical architecture
```
┌─────────────────────────────────────────────────┐
│                  Portfolio Site                  │
├─────────────────────────────────────────────────┤
│              AV_Safety Playground               │
├──────────────┬──────────────────┬────────────────┤
│  Parameter   │   3D Animation   │  Indicator     │
│  Controls    │   (Three.js)     │  Panel         │
│              │                  │                │
│  Sliders:    │  Road geometry   │  TTC, PET,     │
│  - Speed     │  Animated users  │  DRAC, ΔV      │
│  - Distance  │  Collision/avoid │  CPI, PCE      │
│  - Angle     │  visualization   │  Bayesian:     │
│  - Reaction  │                  │  collision rate│
│              │                  │  severity dist │
├──────────────┴──────────────────┴────────────────┤
│              Distribution Plots                   │
│     TTC histogram │ Severity CDF │ Posterior      │
└──────────────────────────────────────────────────┘
```

### Task 6.3: Frontend implementation
- React or vanilla JS for UI
- Three.js or Babylon.js for 3D
- D3.js or plotly.js for plots
- pymc/PyMC for Bayesian computation (could run in browser via Pyodide, or pre-compute and serve results)

**Key decision:** Bayesian computation — run in-browser (Pyodide + PyMC-like) or pre-compute and serve? In-browser is more interactive but slower. Pre-computed is faster but less flexible.

---

## Phase 7: Validation & Quality Assurance

### Task 7.1: Scenario validation
Each scenario must be validated against:
- Published crash data (does it produce similar risk levels to real data?)
- Expert judgment (do traffic safety researchers find it reasonable?)
- Edge cases (what happens at 0 speed? infinite distance?)

### Task 7.2: Indicator validation
- Known analytical solutions where available (e.g., TTC for constant velocity approach)
- Cross-check implementations against published code/examples
- Sensitivity analysis for each indicator

### Task 3.3: Bayesian model validation
- Posterior predictive checks
- Prior sensitivity analysis
- Convergence diagnostics (R-hat > 1.01 = convergence failure)
- Cross-validate with real crash data where possible

### Task 7.4: Animation accuracy verification
- Trajectories match computed kinematics exactly
- Collision timing matches computed collision point
- Severity visualization corresponds to ΔV and impact angle
- No visual artifacts that mislead the viewer

---

## Phase 8: Build Plan (reusable skill tree development)

### Skill development order:
1. ✅ **project-setup** — Done
2. ✅ **standards-research** — Done (need to validate taxonomy)
3. ✅ **risk-metrics** — Done (need to validate indicator list)
4. ✅ **bayesian-analysis** — Done (need EVT extension)
5. 🔲 **scenario-taxonomy** — Build the full conflict type × scenario mapping
6. 🔲 **kinematics-engine** — Implement trajectory computation per conflict type
7. 🔲 **indicator-computation** — Implement all 42 indicators
8. 🔲 **3d-animation** — Three.js scene engine with parameterized scenarios
9. 🔲 **stochastic-simulation** — Monte Carlo framework for collision outcomes
10. 🔲 **bayesian-evt** — EVT + hierarchical Bayesian implementation
11. 🔲 **portfolio-ui** — Frontend integration
12. 🔲 **validation** — Cross-validation against real data

---

## Open Questions (need research to resolve)

1. **EVT threshold selection:** What threshold to use for extreme value modeling? (Need to determine using mean residual life plot or stability analysis)
2. **Prior specification:** What priors for GPD parameters? Need literature values for traffic conflict EVT studies
3. **3D model quality:** Level of detail acceptable for a portfolio project? (Simplified boxes vs detailed meshes)
4. **Computation location:** In-browser vs server-side Bayesian computation?
5. **Data sources for validation:** Which crash databases to use? (NHTSA FARS, CMFwiki, local jurisdiction data)
6. **Jurisdiction scope:** USA/Canada/UK only, or include EU/other for comparison?
7. **Animation scope:** Which scenarios are most important for the portfolio? (Need to prioritize)
8. **Performance:** Real-time computation of 42 indicators + Monte Carlo + Bayesian in browser is heavy. Need to determine what runs where.

---

## Immediate Next Steps

1. **Validate the conflict type taxonomy** against established literature (Task 1.2)
2. **Build the scenario-taxonomy skill** (Skill #5) — this is the foundation for everything else
3. **Start kinematics engine** (Skill #6) — compute trajectories for each conflict type
4. **Research EVT threshold selection methods** — critical for the Bayesian model
