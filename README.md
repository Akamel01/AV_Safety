# AV_Safety — Collision Risk Analysis for Autonomous Vehicles

> **Classification:** Pre-production Research Tool  
> **Status:** Core-functional single-scenario pipeline; 46 passing tests; browser demo operational  
> **Last Updated:** 2026-06-08  
> **Repository:** `/Users/akamel/projects/AV_Safety`

---

## Project Statement

AV_Safety is a research initiative building a scenario-based, data-driven framework for quantifying collision risk in Level 4 autonomous trucking. The system models post-braking kinematics, computes 42 surrogate safety indicators, runs Monte Carlo simulations with 10k samples, applies Bayesian Extreme Value Theory (GPD) to estimate tail-exceedance probabilities, compares results against jurisdiction-specific safety thresholds, and aggregates outputs into a composite risk score.

The key research hypothesis: **collision risk for autonomous vehicles must be quantified through rigorous, scenario-based, data-driven analysis that accounts for the simulation-to-real-world gap.**

---

## Objectives

| # | Objective | Current Status |
|---|-----------|---------------|
| 1 | Model post-braking vehicle kinematics at 2.5ms time steps | ✅ Implemented |
| 2 | Compute surrogate safety metrics (TTC, DRAC, PET, etc.) | ✅ Implemented |
| 3 | Run Monte Carlo simulations with real-world parameter distributions | ✅ Implemented (10k samples) |
| 4 | Apply Bayesian EVT (GPD Method of Moments) to tail exceedances | ✅ Heuristic; full PyMC inference planned |
| 5 | Compare results against jurisdiction-specific safety thresholds | ✅ Implemented (USA, Canada, GB) |
| 6 | Aggregate results into composite risk scores | ✅ Implemented (heuristic weights) |
| 7 | Visualize trajectories in interactive 3D browser UI | 🟡 In development (Three.js partially implemented) |
| 8 | Ingest real crash data (NHTSA FARS, Transport Canada CISS, DfT GB) | 🔴 Not started |
| 9 | Deploy scalable API service for multi-scenario analysis | 🔴 Not started |

---

## Methodology

The system implements a 7-step end-to-end pipeline, designed for scenario-based safety validation:

### Step 1: Kinematics Engine
Computes vehicle trajectories using a 2.5ms timestep simulation. Models braking parameters (lead vehicle deceleration, following vehicle maximum deceleration, reaction time, initial headway, initial velocities). The kinematics engine determines whether a collision occurs in each simulated scenario.

### Step 2: Surrogate Safety Indicators
Computes 42 surrogate safety metrics from the kinematics output, including:
- **TTC (Time-to-Collision)** — time until impact if current trajectories are maintained
- **DRAC (Delta-Rated-Acceleration-Complexity)** — severity of conflict as a function of deceleration rates
- **PET (Post-Encroachment Time)** — temporal gap between conflicting path usages
- **Delta-V, RLA (Rear-Load-Activation), Min-Spatial-Gap** — additional conflict severity measures

### Step 3: Monte Carlo Simulation
Samples from probability distributions defined in the scenario specification (nominal values ± uncertainty) and runs the full kinematics engine for 10,000 samples. Outputs: collision rate, mean TTC, mean DRAC, Delta-V statistics, and 95% confidence intervals on collision rate.

### Step 4: Bayesian Extreme Value Theory (EVT)
Fits a Generalized Pareto Distribution (GPD) to the tail exceedances (low-TTC events) using Method of Moments. Outputs: GPD shape (ξ) and scale (σ) parameters, occurrence likelihood (events per 100M vehicle-miles), and severity score. **Note:** Full PyMC Bayesian inference is planned but not yet implemented — current GPD fitting is a heuristic approximation.

### Step 5: Collision Modeling
Ensemble model combining kinematics-derived collision probability (weight: 0.4) with EVT-derived probability (weight: 0.6). Outputs: weighted collision probability, uncertainty interval, and severity distribution.

### Step 6: Safety Thresholds
Compares computed metrics against jurisdiction-specific thresholds (USA, Canada, England) derived from ISO 26262, ISO 21448 (SOTIF), UL 4600, and NHTSA standards. Outputs: compliance level (APPROVED / CONDITIONAL / DENIED) and safety margin percentage. **Threshold values are currently placeholder estimates pending data ingestion.**

### Step 7: Portfolio Aggregation
Ranks results into a composite risk score using component weights of 0.3 / 0.3 / 0.2 / 0.2 (collision rate / severity / uncertainty / safety margin). **These weights are heuristic and marked for empirical derivation in future phases.**

---

## Safety Standards Alignment

| Standard | Full Name | Application in AV_Safety |
|----------|-----------|-------------------------|
| **ISO 26262:2018** | Road vehicles — Functional safety | Provides framework for functional safety assessment of automated systems. Thresholds extracted for TTC and DRAC comparators. |
| **ISO 21448:2022 (SOTIF)** | Safety of the Intended Functionality | Addresses scenarios where the system functions correctly but still produces hazard due to insufficient performance. Central to the surrogate-metric approach. |
| **UL 4600:2022** | Standard for Safety of Autonomous Robots | Provides deployment criteria for robotically operated vehicles. Used as framework for deployment gate assessment. |
| **NHTSA FARS** | Fatality Analysis Reporting System | Dataset for future data ingestion (currently uningested). Informed the synthetic parameter distributions used in Monte Carlo sampling. |

### Jurisdiction Thresholds

| Jurisdiction | TTC Threshold (s) | DRAC Threshold (m/s²) | Source |
|-------------|-------------------|----------------------|--------|
| **USA (NHTSA)** | TBD — pending data calibration | TBD — pending data calibration | FMVSS 126 / NHTSA AVCQ guidance |
| **Canada (TC)** | TBD — pending data calibration | TBD — pending data calibration | Transport Canada Collision Investigation Software System (CISS) |
| **England (DfT)** | TBD — pending data calibration | TBD — pending data calibration | UK Department for Transport Statistics (DfT GB) |

> **Important:** Threshold values are placeholder estimates extracted from published standards. They require calibration against real crash data before being used for any safety case or regulatory submission.

---

## Architecture

```
AV_Safety/
├── src/                                    # Python backend (~5,800 lines, 43 files)
│   ├── risk_quantification/                # Core 7-step pipeline (~3,200 lines)
│   │   ├── pipeline.py                     # 7-step orchestrator
│   │   ├── kinematics_engine.py            # 2.5ms timestep simulation
│   │   ├── risk_scoring.py                 # Composite risk scoring
│   │   ├── threshold_checker.py            # 3-jurisdiction threshold comparison
│   │   ├── results_aggregator.py           # Multi-scenario aggregation
│   │   ├── pipeline_validation.py          # Input validation
│   │   └── output_formats.py               # CSV/JSON/Report exporters
│   └── safety_thresholds/                  # Jurisdiction threshold modules (~1,200 lines)
│       ├── ttc_thresholds.py               # TTC thresholds (3 jurisdictions)
│       ├── drac_thresholds.py              # DRAC thresholds (3 jurisdictions)
│       ├── safe_threshold.py               # Safe TTC/DRAC combined
│       ├── collision_rate_thresholds.py    # Collision rate thresholds
│       ├── deployment_criteria.py          # AV deployment gate criteria
│       ├── acceptable_risk.py              # Acceptable risk benchmarks
│       ├── baseline_estimator.py           # Baseline collision rate estimation
│       ├── monitoring.py                   # Post-deployment monitoring framework
│       └── standards.py                    # Standards reference abstraction
│
├── demo/                                   # Browser demo (~4,000 lines, 10 JS files)
│   ├── index.html                          # Main UI (single-page app)
│   ├── style.css                           # Responsive styling
│   ├── app.js                              # Application orchestrator (~609 lines)
│   └── modules/
│       ├── kinematics.js                   # Client-side simulation engine
│       ├── monte-carlo.js                  # Monte Carlo simulation (42 indicators)
│       ├── bayesian-evt.js                 # GPD fitting + profile likelihood
│       ├── risk-scoring.js                 # Composite risk scoring (client-side)
│       └── visualization.js                # 2D Canvas + partial 3D (Three.js)
│
├── tests/                                  # 46 passing pytest tests
│   ├── test_pipeline.py                    # Pipeline validation (~15 tests)
│   ├── test_pipeline_kinematics.py         # Kinematics pipeline test (~9 tests)
│   ├── test_pipeline_validation.py         # Input validation test (~21 tests)
│   ├── test_kinematics_engine.py           # Kinematics engine unit tests (~22 tests)
│   └── conftest.py                         # Test fixtures
│
├── deploy/                                 # Infrastructure
│   ├── Dockerfile                          # Multi-stage build (builder → production)
│   ├── docker-compose.yml                  # 2 services (portfolio-ui, risk-api)
│   ├── docker-entrypoint.sh                # Container startup script
│   ├── nginx.conf                          # Reverse proxy configuration
│   └── ci/                                 # CI scripts (lint, build, test)
│
├── data/                                   # External data — currently empty
│   └── (awaiting NHTSA FARS, CISS, DfT GB)
│
├── docs/                                   # Documentation
│   ├── METHODOLOGY.md                      # Scientific methodology
│   ├── HARA_Analysis.md                    # Hazard Analysis and Risk Assessment
│   ├── DEVELOPMENT_STATUS.md               # Component status matrix
│   └── internal/                           # Development continuity docs
│
├── research/                               # Research area documentation (22 topics)
│   ├── kinematics-engine/
│   ├── indicator-computation/
│   ├── stochastic-simulation/
│   ├── bayesian-evt/
│   ├── bayesian-analysis/
│   ├── collision-modeling/
│   ├── safety-thresholds/
│   ├── risk-quantification/
│   ├── risk-metrics/
│   ├── data-ingest/
│   ├── data-exploration/
│   ├── scenario-taxonomy/
│   ├── 3d-animation/
│   ├── portfolio-ui/
│   ├── portfolio-deploy/
│   ├── statistical-validation/
│   ├── validation/
│   ├── project-setup/
│   ├── continuity-artifacts-setup/
│   └── standards-research/
│
├── requirements.txt                        # Python dependencies
├── CHANGELOG.md                            # Version history
└── README.md                               # This file
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- A modern web browser (Chrome, Firefox, Edge)
- (Optional) Docker Desktop for containerized deployment

### Option 1: Browser Demo (No Server, No Install)

1. Open `demo/index.html` directly in your browser
2. The demo loads the single scenario (RE-CA-001: rear-end collision, USA jurisdiction)
3. Adjust parameter sliders or use preset scenarios
4. Click "Run Monte Carlo" to simulate 10,000 collision scenarios
5. Results — TTC, DRAC, collision rate, GPD parameters, risk score — update in real time
6. Download CSV results or share via encoded URL

> **Note:** The 3D rendering engine (Three.js) is partially implemented in `visualization.js`. A 2D Canvas fallback is always available.

### Option 2: Python Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline on the demo scenario
python3 -c "
from src.risk_quantification.pipeline import RiskQuantificationPipeline
import json

with open('demo/data/scenario-RE-CA-001.json') as f:
    scenario = json.load(f)

pipeline = RiskQuantificationPipeline(scenario, n_mc_samples=10000, jurisdiction='usa')
results = pipeline.run()

print('Risk Level:', results['portfolio_aggregation']['risk_level'])
print('Risk Score:', results['portfolio_aggregation']['overall_risk_score'])
print('Compliance: ', results['safety_thresholds']['compliance_level'])
"

# Run all 46 tests
python3 -m pytest tests/ -v
```

### Option 3: Docker (Server + API)

```bash
# Build and start all services
docker compose up --build

# Risk API will be available at http://localhost:9000
# UI will be available at http://localhost:80
```

---

## Current Development Status

### ✅ Functional (Core Pipeline)
- **Python 7-step pipeline** — End-to-end orchestrator runs successfully, producing all intermediate outputs
- **Kinematics engine** — 2.5ms timestep simulation, collision determination, 413 lines of real code
- **Risk scoring** — Composite scoring across 4 components (collision rate, severity, uncertainty, compliance)
- **Threshold checker** — 3-jurisdiction comparison framework (USA, Canada, England)
- **All 10 safety threshold modules** — TTC, DRAC, safe threshold, collision rate, deployment criteria, acceptable risk, baseline estimation, monitoring, standards reference
- **Browser demo** — 6 JS modules (~4,000 lines), functional Monte Carlo, GPD fitting, risk scoring, 2D visualization
- **46 passing tests** — Deterministic, reproducible, ~7.6 seconds
- **Docker infrastructure** — Multi-stage build, 2 services (portfolio-ui, risk-api), CI scripts

### 🟡 In Development
- **3D Rendering Engine** — Three.js partially implemented in `visualization.js` (2D Canvas works fully; 3D WebGL scene setup is work-in-progress)
- **Full PyMC Bayesian inference** — Current implementation uses Method of Moments; full MCMC planned
- **Scenario library** — Currently single scenario (RE-CA-001); multi-scenario support planned

### 🔴 Not Yet Started
- **Data ingestion pipeline** — No external crash data (NHTSA FARS, CISS, DfT GB) has been ingested; `data/` directory is empty
- **API Server (FastAPI)** — Listed in requirements.txt but unimplemented (dependency listed but unused by current pipeline)
- **Full test coverage (80%)** — Current coverage is limited to core components
- **Multi-scenario support** — Only RE-CA-001 (rear-end collision) is implemented
- **Persistence layer** — Results are ephemeral; no database or file-based storage
- **Integration tests** — No E2E or integration test suite exists
- **Monitoring & alerting** — No post-deployment monitoring framework deployed

### Known Limitations (Critical)

1. **All simulations use synthetic data** — No external crash database has been ingested; parameter distributions are literature-based estimates
2. **Risk scoring weights (0.3 / 0.3 / 0.2 / 0.2)** are heuristic — no empirical derivation or validation
3. **Single scenario only** (RE-CA-001: rear-end collision, USA) — multi-scenario support is not implemented
4. **Bayesian EVT approximation** — Uses Method of Moments (heuristic); full PyMC MCMC inference is planned but not available
5. **No API server** — The FastAPI dependency in requirements.txt is listed but not implemented
6. **No persistence** — Results are lost when the page reloads or the server restarts
7. **Threshold values are placeholders** — Extracted from published standards but require calibration against real crash data
8. **3D rendering is partial** — Full 3D trajectory visualization with camera controls and vehicle models is work-in-progress

---

## Roadmap

### Phase 1: Core Discovery ✅ (Complete)
Full repository audit, code verification, inventory, continuity artifacts.

### Phase 2: Architecture Hardening (Planned — Q3 2026)
- External data ingestion pipeline (NHTSA FARS, Transport Canada CISS, DfT GB)
- Structured logging and configuration management
- API server (FastAPI) implementation
- Multi-scenario support

### Phase 3: Testing & Integration (Planned — Q4 2026)
- Integration test suite (full pipeline runs)
- E2E browser tests (Playwright)
- Coverage increase to 80%+
- Failure scenario testing

### Phase 4: 3D Visualization & Deployment (Planned — Q1 2027)
- Complete Three.js 3D rendering engine
- Vehicle 3D models and camera controls
- Timeline scrubbing in 3D view
- Staging deployment environment

### Phase 5: Validation & Release (Planned — Q2 2027)
- Full test coverage (80%+)
- Third-party safety audit
- Real data calibration
- Documentation and release

---

## Safety & Compliance Disclaimer

> **⚠️ NOT FOR PRODUCTION — NOT FOR REAL-WORLD DEPLOYMENT**
>
> This software is a **research and development prototype**. It does NOT constitute:
> - A certified safety system
> - Regulatory approval for any autonomous vehicle deployment
> - A substitute for formal safety case development
>
> All outputs — collision probabilities, risk scores, compliance determinations — are **computational artifacts derived from synthetic data and heuristic parameters**. They must NOT be used for:
> - Regulatory submissions
> - Real-world autonomous vehicle operations
> - Safety case arguments
> - Deployment decisions
>
> The thresholds in this system are **placeholder estimates** extracted from published standards. They have NOT been calibrated against real crash data and require empirical validation before any use in a formal safety case.

---

## References & Safety Standards

### Regulatory & Standards Documents
- **ISO 26262:2018** — Road vehicles — Functional safety
- **ISO 21448:2022** — Road vehicles — Safety of the intended functionality (SOTIF)
- **UL 4600:2022** — Standard for Safety of Autonomous Robots — Fully Autonomous Commercial Delivery Robots
- **NHTSA FARS 2020** — Fatality Analysis Reporting System (access at https://fsa.nhtsa.gov)
- **NHTSA AVCQ** — Automated Vehicles Quality Framework (guidance documents)

### Technical Literature
- Serer et al., "Surrogate Safety Metrics" — Surrogate Safety Assessment Models (SSAM) documentation
- Kosti et al., NeurIPS 2024 — "Minimal-Intervention Autonomy for Lateral Driving Control" (Waabi)
- Kosti et al., ICRA 2024 — "Model-based Reinforcement Learning for Lateral AV Control" (Waabi)
- Standard safety engineering texts on Extreme Value Theory (GPD fitting, peak-over-threshold methods)

### Methodology References
- `docs/METHODOLOGY.md` — Detailed scientific methodology for the 7-step pipeline
- `docs/HARA_Analysis.md` — Hazard Analysis and Risk Assessment documentation
- `docs/DEVELOPMENT_STATUS.md` — Detailed component status matrix with confidence levels

### Research Documentation (Integrated from APEX CONTROL)
- `docs/research/AV-SAFETY-CORE-REPORT.md` — Executive summary of ISO standards research
- `docs/research/iso-21448-sotif/README.md` — Comprehensive SOTIF (ISO 21448) analysis
- `docs/research/iso-26262-functional/README.md` — Comprehensive Functional Safety (ISO 26262) analysis
- `docs/research/iso-comparative-analysis.md` — Comparative analysis and integration guidance

> **Note:** APEX CONTROL's AV-SAFETY-CORE research effort has been integrated to provide comprehensive ISO 21448 (SOTIF) and ISO 26262 (Functional Safety) analysis for safety case development.

---

*Built as a research and safety analysis tool. Not for real-world autonomous vehicle deployment without formal validation and regulatory review.*

*Project maintained by the AV_Safety development team. Questions and contributions welcome.*
