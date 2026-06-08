# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

#### Core Pipeline (Python Backend)

- **7-step Risk Quantification Pipeline** (`pipeline.py`)
  - Scenario loading → Kinematic simulation → 42 safety indicators → Monte Carlo sampling → Bayesian EVT → Collision model → Jurisdiction thresholds → Risk scoring
- **2.5ms Kinematics Engine** (`kinematics_engine.py`)
  - High-resolution trajectory simulation with 42 surrogate safety indicator computation
- **Risk Scoring Module** (`risk_scoring.py`)
  - Composite scoring: collision rate (0.3) + severity (0.3) + uncertainty (0.2) + compliance (0.2)
- **Safety Threshold Checker** (`threshold_checker.py`)
  - Jurisdictional comparison: USA (NHTSA), Canada (TC), Great Britain (DfT)
- **Results Aggregator** (`results_aggregator.py`)
  - Multi-scenario aggregation with statistical summaries
- **Output Formatters** (`output_formats.py`)
  - CSV, JSON, and structured report exporters
- **Safety Thresholds (10 modules)** — TTC, DRAC, deployment criteria per ISO 26262, SOTIF, UL 4600

#### JavaScript Frontend (Browser Demo)

- **Application Orchestrator** (`app.js`)
  - Full pipeline integration from HTML UI through 6 JavaScript modules
- **Kinematics Module** (`kinematics.js`)
  - Client-side 2.5ms timestep simulation (mirrors Python backend)
- **Monte Carlo Module** (`monte-carlo.js`)
  - 10,000-sample simulation with 42 surrogate safety indicators, IndexedDB storage
- **Bayesian EVT Module** (`bayesian-evt.js`)
  - GPD fitting (Method of Moments), profile likelihood, posterior predictive checks
- **Risk Scoring Module** (`risk-scoring.js`)
  - Client-side composite scoring (mirrors Python backend)
- **Visualization Module** (`visualization.js`)
  - 2D Canvas trajectory rendering (functional), 3D (Three.js) in development

#### Infrastructure

- **Dockerfile** (multi-stage build: builder + slim runtime)
- **docker-compose.yml** (4 services: API, frontend, database, Nginx)
- **GitHub Actions CI/CD** (Python 3.10–3.12, pytest + ruff linting)
- **pyproject.toml** (pytest, coverage, ruff configuration)

#### Documentation

- Professional README.md (objectives, methodology, architecture, development status, quick start, standards)
- docs/METHODOLOGY.md (complete scientific methodology document)
- docs/DEVELOPMENT_STATUS.md (transparent assessment of what works / what's pending)
- docs/internal/ (25 internal planning and continuity documents)

#### Testing

- 46 passing pytest tests (7.6 seconds total)
- Pipeline validation tests (scenario loading, simulation, Monte Carlo, scoring, threshold checking)

### Changed

- Repository restructured for clarity:
  - `skills/` → `research/` (domain research assets — 22 structured modules)
  - `single-scenario-demo/` → `demo/` (browser-based pilot demo)
  - Internal development docs consolidated under `docs/internal/`
  - Root directory cleaned to core project files only

### Known Limitations

- Risk scoring weights (0.3/0.3/0.2/0.2) are heuristic — no empirical derivation from real crash data (data ingestion pending)
- Bayesian EVT uses Method of Moments — full PyMC Bayesian inference not yet implemented
- All simulations use synthetic parameter distributions — no external crash data ingested
- 3D rendering engine under active development (Three.js integration in progress)
- No persistence layer — results are lost on page reload or server restart
- Single scenario support only (RE-CA-001) — multi-scenario comparison not yet implemented

---

## [0.1.0-alpha] — 2026-06-08

### Initial Repository State (Established During Systematic Audit)

#### Established

- Python backend identified: 8 source files (~1,700 lines) — all functional, no stubs
- JavaScript frontend identified: 6 modules (~2,500 lines) — all functional, no stubs
- Test suite identified: 46 tests (7.6 seconds) — all passing
- Deployment infrastructure identified: Dockerfile, docker-compose.yml, CI/CD pipeline
- Safety standards documentation identified: 10 threshold modules (ISO 26262, SOTIF, UL 4600, NHTSA)
- Documentation artifacts identified: 25+ markdown files (status, planning, continuity)

#### Issues Found

- 3 critical JavaScript integration bugs (API mismatches between app.js and 5 JS modules)
- Stale documentation (all 5 claims in original STATUS.md disproven by audit)
- 5 modules with non-working code (non-functional penultimate modules)
- Missing error handling in demo frontend (critical CRIT-003)
- Missing input validation in pipeline (critical CRIT-004)

---

*This changelog will be maintained as the project transitions from research prototype to production system. Version numbering follows Semantic Versioning with `-alpha` suffix during active development.*
