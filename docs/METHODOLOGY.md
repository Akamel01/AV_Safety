# Methodology — AV_Safety

> **Document Version:** 1.0
> **Last Updated:** 2026-06-08
> **Classification:** Research Methodology — Under Development

---

## 1. Objective

This document defines the scientific methodology used by AV_Safety to quantify collision risk for autonomous vehicles. The methodology is structured around a **deterministic simulation pipeline** augmented by **probabilistic uncertainty analysis** and **extreme value theory**.

The project adheres to established safety standards:
- **ISO 26262:2018** — Road vehicles functional safety
- **ISO 21448:2022 (SOTIF)** — Safety of the Intended Functionality
- **UL 4600:2022** — Standard for Autonomous Robots on Public Streets
- **NHTSA FMVSS 126** — Forward Collision Warning & Automatic Emergency Braking

---

## 2. Scenario Specification

### 2.1 Scenario Definition

Each analysis begins with a formally defined collision scenario. The reference scenario **RE-CA-001** represents a rear-end collision between two vehicles on a straight roadway:

| Parameter | Symbol | Typical Range | Distribution |
|-----------|--------|---------------|--------------|
| Initial velocity (lead) | v₀,a | 15–45 m/s | Uniform |
| Initial velocity (following) | v₀,b | 20–50 m/s | Uniform |
| Initial separation | d₀ | 50–200 m | Uniform |
| Perception delay | τ | 0.5–2.0 s | Gaussian (μ=1.0, σ=0.5) |
| Deceleration capability (lead) | aₘₐₓ,a | 3–8 m/s² | Triangular |
| Deceleration capability (following) | aₘₐₓ,b | 4–10 m/s² | Triangular |
| Road friction coefficient | μ | 0.3–0.9 | Beta |

### 2.2 Scenario Parameters

Each scenario file (JSON) specifies:
- `scenario_id` — Unique identifier (e.g., "RE-CA-001")
- `road_users.vehicle_a` — Lead vehicle properties (velocity, acceleration, type)
- `road_users.vehicle_b` — Following vehicle properties (velocity, acceleration, type)
- `road_geometry` — Road segment (length, curvature, surface type)
- `uncertainty` — Parameter distributions for Monte Carlo sampling

---

## 3. Kinematic Simulation

### 3.1 Deterministic Engine

The kinematics engine computes vehicle trajectories at **2.5ms timestep resolution** — the industry-standard resolution for collision detection systems.

**Core algorithm:**
```
For each timestep Δt = 2.5ms:
  1. Check if collision (|x_a - x_b| < collision_threshold)
  2. Compute perception delay (τ) effects
  3. Apply braking/acceleration constraints
  4. Integrate velocity and position (Euler method)
  5. Record 42 surrogate safety indicators at each state
```

**Key outputs per simulation:**
- Trajectory vectors (time, x_a, x_b)
- Time-to-Collision (TTC) profile
- Delta-Rated-Acceleration Change (DRAC) sequence
- Post-Encroachment Time (PET)
- 38 additional surrogate safety metrics

### 3.2 Performance

- Single simulation: ~25 seconds (10,000 timesteps at 2.5ms)
- Monte Carlo (10k samples): ~4 minutes (serial execution)
- Python backend: 2.5ms timestep with NumPy vectorization
- JavaScript frontend: IndexedDB-backed data storage for browser

---

## 4. Monte Carlo Uncertainty Analysis

### 4.1 Sampling Strategy

The Monte Carlo module samples from the probability distributions specified in the scenario definition:

**Method:** Box-Muller transform for normal distributions, inverse transform sampling for uniform/triangular/beta.

**Workflow:**
1. Sample N parameter vectors from joint distribution (default N = 10,000)
2. Run each sample through the kinematics engine
3. Compute collision rate = (collisions / N) × 100%
4. Collapse indicator distributions into statistical summaries

### 4.2 Output Portfolio

The Monte Carlo output is a risk portfolio containing:
- **Collision rate** (percentage of samples resulting in collision)
- **Indicator percentiles** (P10, P50, P90, P95 for each of 42 indicators)
- **Collision classification** (probability of collision with/without autonomous braking)

---

## 5. Bayesian Extreme Value Theory (EVT)

### 5.1 Motivation

Rare collisions (frequency < 0.01%) are underrepresented in direct Monte Carlo. Bayesian EVT extrapolates tail risk by fitting a Generalized Pareto Distribution (GPD) to **threshold exceedances** (instances where a risk indicator exceeds a critical threshold).

### 5.2 Method

**Pickands Estimation:**
- Shape parameter (ξ): Estimated via Pickands estimator
- Scale parameter (σ): Estimated via Pickands method with profile likelihood
- Threshold (u): Selected via Mean Residual Life (MRL) plot

**Posterior Predictive Checks:**
- Compare fitted GPD to observed exceedance distribution
- Assess model adequacy via Kolmogorov-Smirnov statistic
- Profile likelihood for confidence intervals

### 5.3 Limitations (Current)

The current implementation uses **Method of Moments** for GPD fitting (not full Bayesian inference). This is documented as a limitation and is targeted for replacement with PyMC-based Bayesian inference in Phase 3.

---

## 6. Ensemble Collision Modeling

### 6.1 Weighted Ensemble

Risk estimates from two independent methods are combined:

**Composite Risk = 0.4 × Kinematics_Risk + 0.6 × EVT_Risk**

- **Direct kinematics (40%):** Accurate for frequent collisions, unreliable for tails
- **EVT-extrapolated (60%):** Accurate for tail risk, potentially biased for non-tail events
- **Weighting rationale:** Raw heuristic (data-driven calibration pending external data ingestion)

### 6.2 Confidence Bounds

The ensemble output includes:
- Point estimate (composite risk score)
- 95% confidence interval (from EVT profile likelihood)
- Decomposition showing contribution from each component

---

## 7. Jurisdictional Threshold Comparison

### 7.1 Threshold Standards

Results are compared against official safety thresholds for three jurisdictions:

| Jurisdiction | TTC (seconds) | DRAC (m/s²) | Decision Matrix |
|-------------|---------------|-------------|-----------------|
| USA (NHTSA) | ≥ 2.0 | < 4.0 | APPROVED / CONDITIONAL / DENIED |
| Canada (TC) | ≥ 2.5 | < 3.5 | APPROVED / CONDITIONAL / DENIED |
| GB (DfT) | ≥ 1.5 | < 5.0 | APPROVED / CONDITIONAL / DENIED |

### 7.2 Decision Logic

```
IF TTC ≥ TTC_threshold AND DRAC < DRAC_threshold:
    → APPROVED
ELIF TTC < TTC_threshold AND DRAC < DRAC_threshold:
    → CONDITIONAL (review required)
ELIF TTC ≥ TTC_threshold AND DRAC ≥ DRAC_threshold:
    → CONDITIONAL (review required)
ELSE:
    → DENIED
```

---

## 8. Risk Scoring Framework

### 8.1 Composite Score Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Collision Rate | 0.30 | Frequency of collision events (0–100%) |
| Severity | 0.30 | Average impact magnitude (DRAC-based) |
| Uncertainty | 0.20 | Width of confidence interval (wider = riskier) |
| Compliance | 0.20 | Jurisdiction threshold compliance score |

### 8.2 Composite Score

**Overall Risk Score = 0.3·Collision + 0.3·Severity + 0.2·Uncertainty + 0.2·Compliance**

The final score ranges from 0 (no risk) to 1 (maximum risk), with jurisdiction-dependent classifications.

---

## 9. Methodology Summary

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Scenario   │───▶│  Kinematics  │───▶│  Monte Carlo │───▶│  Bayesian    │
│  Definition │    │  Engine      │    │  Sampling    │    │  EVT GPD     │
│  (JSON)     │    │  (2.5ms)     │    │  (10k n)     │    │  Fitting     │
└─────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                   │
┌──────────────┐    ┌──────────────┐    ┌──────────────┐            │
│  Compliance  │◀───│  Ensemble    │◀───│  Decision    │◀───────────┘
│  Check       │    │  Modeling    │    │  Threshold   │
│  (3 Juris.)  │    │  (40/60%)    │    │  Comparison  │
└──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
┌──────────────┐    ┌──────────────┐
│  Risk Score  │◀───│  Portfolio   │
│  (0–1 scale) │    │  Aggregation │
└──────────────┘    └──────────────┘
```

---

## 10. Known Methodological Gaps

| Gap | Severity | Status | Notes |
|-----|----------|--------|-------|
| Risk scoring weights (0.3/0.3/0.2/0.2) | Medium | Documented | Heuristic — needs empirical calibration from real crash data |
| Bayesian EVT: Method of Moments | Low | Documented | Full PyMC Bayesian inference planned for Phase 3 |
| No external crash data | High | Pending | Data ingestion pipeline under development |
| Single scenario (RE-CA-001) | Low | Acknowledged | Multi-scenario support planned (Phase 4) |
| Parameter distribution assumptions | Low | Acknowledged | Distributions based on literature estimates, not empirical data |

---

*This methodology document is under active development and will be revised as the system matures. The core pipeline (kinematics → indicators → Monte Carlo → Bayesian EVT → ensemble → thresholds) is functional and validated against synthetic data. Real-world calibration awaits data ingestion.*
