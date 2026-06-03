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

**3D Engine:**
- **Three.js + JavaScript** — web-native, no backend needed, runs in browser
- **High-fidelity rendering:** PBR materials, shadows, physically-based lighting
- **Asset quality:** High-poly vehicle meshes (GLTF/GLB format), detailed road geometry with lane markings, signage, curb, sidewalk
- **Pedestrian/cyclist models:** Detailed human/cyclist meshes (not stick figures)
- **Post-processing:** Bloom on collision flash, motion blur, particle effects for crash debris

**2D Animation (fallback/lite mode):**
- Canvas 2D rendering with smooth interpolation
- Top-down orthographic view with scale markers
- Color-coded conflict zones and trajectories
- Toggle 3D/2D via UI control

**Recommendation:** Three.js for 3D, Canvas 2D for lightweight mode. Toggle in UI.

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

**3D Mode (high-fidelity):**
- **Vehicles:** High-poly GLTF models with PBR materials (metallic, roughness, normal maps)
- **Roads:** Detailed road geometry with lane markings, centerlines, edge lines, curbs, sidewalks, medians
- **Signage:** Stop signs, traffic lights, crosswalk markings, yield signs
- **Lighting:** Physically-based lighting with shadows (sun position based on scenario time of day)
- **Environment:** Optional time-of-day lighting, weather (dry/wet road surface effects)
- **Pedestrians:** Detailed human mesh with walking animation
- **Cyclists:** Detailed bicycle + cyclist mesh
- **Collision:** Kinetic energy visualization (energy release effect), vehicle deformation, debris particles, sound (optional)
- **Camera:** Auto-tracking camera + free-look mode

**2D Mode (lite):**
- Top-down orthographic view
- Smooth animated trajectories
- Color-coded indicators (green → yellow → red)
- Scale reference bar
- Real-time TTC/DRAC overlay

**Critical requirement:** Animation must be visually polished — this is a portfolio piece. Every frame should be presentable.

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

### Task 5.4: EVT threshold selection — Mean Residual Life Plot

**Method:** Mean Residual Life (MRL) plot

1. **Compute the empirical mean residual life function:**
   For a threshold `u`, compute: `e(u) = E[X - u | X > u]` estimated from the data

2. **Plot e(u) vs u:**
   - If the GPD assumption is valid, e(u) should be approximately linear for large u
   - The threshold is the point where linearity begins

3. **Implementation:**
   - Sort extreme values in descending order
   - For each candidate threshold u_i, compute mean of values above u_i minus u_i
   - Plot with uncertainty bands (bootstrap confidence intervals)
   - Threshold = first point where the plot becomes approximately linear

4. **Validation:**
   - Stability analysis: fit GPD above multiple thresholds, check if ξ and σ stabilize
   - Visual confirmation: QQ-plot of GPD fit against empirical extremes

**Evidence needed:** 
- Coles (2001) "An Introduction to Statistical Modeling of Extreme Values" — Chapter 3
- Niermann et al. (2020) "Practical guide to threshold selection for EVT" 
- Traffic conflict literature: Lord & Mannering (2010), Gamage & Tay (2008)

### Task 5.2: Implementation requirements
```
src/evaluation/bayesian_evt/
  gpd.py           — GPD fitting and sampling
  hierarchical.py  — Bayesian hierarchical model
  collision_rate.py — Occurrence likelihood estimation
  severity_model.py — Severity distribution fitting
  posterior_predictive.py — Validation checks
  threshold_selection.py — Mean residual life plot + stability analysis
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
- Three.js for 3D rendering (high-fidelity GLTF models, PBR materials, post-processing)
- Canvas 2D for 2D lightweight mode
- D3.js or plotly.js for distribution plots
- **Bayesian computation options:**

  **Option A — In-browser (Pyodide):**
  - Pyodide (Python in WebAssembly) runs PyMC/NumPy in browser
  - Full interactivity: user adjusts parameters → Bayesian re-runs in real-time
  - **Pros:** True real-time interactivity, no backend needed
  - **Cons:** Slower computation (~10-30s per full Bayesian run in browser), large WASM bundle (~50MB+), memory constraints
  - **Mitigation:** Use NumPy via Pyodide (fast), limit MC samples during interaction, warm-start with cached results

  **Option B — Pre-computed + served:**
  - Bayesian results pre-computed on build server for each scenario's parameter grid
  - Results served as JSON: collision rate grid, severity CDF grid, posterior samples
  - **Pros:** Instant load, no WASM dependency, full precision
  - **Cons:** Limited to pre-defined parameter grid (not fully continuous), rebuild needed for new scenarios
  - **Hybrid approach:** Pre-compute for base scenarios, compute on-demand for user-adjusted parameters (cached)

  **Recommended approach:** Hybrid.
  - Base scenarios have pre-computed Bayesian results for instant display
  - When user adjusts parameters beyond the base grid, trigger in-browser Pyodide computation
  - Cache results locally (IndexedDB) to avoid re-computation
  - Document both approaches in `docs/architecture/computation-strategy.md` for reference

---

## Phase 7: Validation & Quality Assurance

### Task 7.1: Scenario validation
Each scenario must be validated against:

**Data sources:**
- **USA:** NHTSA FARS (Fatality Analysis Reporting System), NHTSA Crash Investigation Sampling System (CISS), NASS-CRS (National Automotive Sampling System), NHTSA 4-Star Safety Rating publications, NHTSA AV guidance documents
- **Canada:** Transport Canada Transportation Statistics, CMFwiki Canada entries, provincial data (ICBC BC, SAAQ Quebec)
- **England:** Department for Transport (DfT) Road Casualties Great Britain, Highways England data, JACArP (JCA Road Safety Database)

**Standards frameworks:**
- **UL 4600** — Standard for UAS Destination Guidance and AV safety requirements (relevant clauses on collision avoidance, risk management)
- **ISO 21448 (SOTIF)** — Safety of the Intended Functionality (scenario coverage, edge cases, performance limits)
- **ISO 26262** — Road vehicles functional safety (hazard classification, ASIL levels relevant to collision scenarios)
- **ISO 21002** — ITS (Intelligent Transport Systems) data access for traffic conflict analysis
- **NHTSA publications:** "Autonomous Vehicles Safety Framework", "Crash Avoidance Methodology", vehicle crashworthiness publications

**Validation criteria:**
1. Published crash data alignment (does it produce similar risk levels to real data?)
2. Expert judgment (do traffic safety researchers find it reasonable?)
3. Edge cases (what happens at 0 speed? infinite distance?)
4. **Standards alignment:** Each scenario must map to relevant UL 4600/ISO/NHTSA clauses where applicable

**Evidence constraint:** Only use publicly available documents. If a document requires purchase/subscription, note it as "access restricted" and use available summaries or publicly cited extracts instead.

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

### Task 8.3: Scenario coverage strategy

**Featured scenarios (2 per conflict type = 16 featured):**
Each conflict type has 2 featured scenarios that users see immediately:
- One "typical" scenario (common real-world instance)
- One "edge" scenario (worst-case or unusual instance)

**View All Scenarios:**
When users click "View All Scenarios":
- All 62+ scenarios across all 8 conflict types become accessible
- Organized as expandable categories
- Filter by conflict type, road user type, severity level
- Each scenario opens with its own parameterized playground

**Priority scenario list (featured first):**
1. **Crossing:** (1) Intersection perpendicular crossing, (2) Mid-block jaywalking
2. **Merging:** (1) Highway on-ramp merge, (2) Cut-in lane change
3. **Diverging:** (1) Highway off-ramp exit, (2) Lane change outbound
4. **Weaving:** (1) Short weave closely-spaced ramps, (2) Long weave distant ramps
5. **Rear-end:** (1) Following constant gap, (2) Sudden braking + cut-under
6. **Sideswipe:** (1) Lane-change induced, (2) Same-direction sideswipe
7. **Right-angle:** (1) Intersection cross-traffic (red light), (2) T-bone at stop sign
8. **Opposing LT:** (1) Unprotected left across opposing, (2) Multi-lane opposing turn

---

## Resolved Decisions (June 2, 2026)

1. **EVT threshold selection:** Mean Residual Life (MRL) plot with stability analysis ✅
2. **3D model quality:** Highest possible — high-poly GLTF models, PBR materials, detailed road/signage/environment ✅
3. **2D animation:** Also available as lightweight toggle (Canvas 2D top-down) ✅
4. **Computation location:** Primary = in-browser Pyodide. Documented pre-compute + serve as fallback/hybrid ✅
5. **Validation data:** NHTSA FARS/CISS, Transport Canada, DfT GB, CMFwiki Canada, JACArP England ✅
6. **Standards:** UL 4600, ISO 21448 (SOTIF), ISO 26262, ISO 21002, NHTSA publications ✅
7. **Data access:** Only publicly available documents; note restricted ones as "access restricted" ✅
8. **Jurisdiction:** USA, Canada, England (not UK — use England-specific DfT/JACArP data) ✅
9. **Scenario coverage:** 2 featured per conflict type (16 featured total) + "View All Scenarios" for all 62+ ✅
10. **Featured scenario strategy:** One typical + one edge case per conflict type ✅

## Immediate Next Steps

1. **Build computation-strategy document** — Document both Pyodide and pre-compute approaches in detail
2. **Build the kinematics engine skill** — Trajectory computation per conflict type
3. **Start standard literature review** — Extract relevant clauses from publicly available UL 4600/ISO/NHTSA docs
4. **Build scenario-taxonomy scenarios** — Define the 16 featured scenarios with full parameter specs
