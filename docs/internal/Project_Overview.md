# Project Overview — AV_Safety

**Last Updated:** 2026-06-07  
**Version:** 0.1.0 (Development)  
**Project Type:** Collision Risk Analysis Tool for Autonomous Vehicles

---

## What This Project Is

AV_Safety is a collision risk quantification system for autonomous vehicles, implementing the RE-CA-001 scenario analysis pipeline. It computes rear-end collision risk using:

- **Kinematics engine** — Real 2.5ms timestep trajectory simulation
- **Monte Carlo simulation** — Parameter sampling with full trajectory computation
- **Bayesian Extreme Value Theory** — GPD fitting for tail risk estimation
- **Risk scoring** — Multi-component composite scoring (collision + severity + uncertainty + compliance)
- **Jurisdiction compliance** — TTC/DRAC thresholds for USA, Canada, GB

**Target Standard:** ISO 26262 (SOTIF), UL 4620, NHTSA autonomous vehicle guidelines

---

## What Exists (Verified)

### Python Backend (src/)
| Module | Lines | Status | Notes |
|--------|-------|--------|-------|
| `pipeline.py` | 398 | ✅ Real | Full 7-step orchestrator |
| `kinematics_engine.py` | 413 | ✅ Real | 2.5ms timestep simulation |
| `risk_scoring.py` | 182 | ✅ Real | Weighted composite scoring |
| `threshold_checker.py` | 227 | ✅ Real | Multi-jurisdiction compliance |
| `results_aggregator.py` | 156 | ✅ Real | Multi-scenario aggregation |
| `output_formats.py` | 124 | ✅ Real | CSV/JSON/Report exporters |
| `safety_thresholds/` | 10 modules | ✅ Real | TTC/DRAC/deployment criteria |

### JavaScript Frontend (single-scenario-demo/)
| Module | Lines | Status | Notes |
|--------|-------|--------|-------|
| `app.js` | 609 | ✅ Real | Full application orchestration |
| `kinematics.js` | 344+ | ✅ Real | Client-side kinematics engine |
| `monte-carlo.js` | 344+ | ✅ Real | Box-Muller + 42 indicators |
| `bayesian-evt.js` | 286+ | ✅ Real | MRL selection + GPD fitting |
| `risk-scoring.js` | 234+ | ✅ Real | Multi-component scoring |
| `visualization.js` | 486 | ✅ Real | Three.js 3D + 2D Canvas fallback |

### Infrastructure
| Item | Status | Notes |
|------|--------|-------|
| `requirements.txt` | ✅ Real | FastAPI + uvicorn + numpy + scipy + pandas |
| `Dockerfile` | ✅ Real | Multi-stage build (builder + slim runtime) |
| `.github/workflows/ci.yml` | ✅ Real | Python 3.10-3.12, pytest, ruff (NEW) |
| `tests/` | ✅ 46 tests pass | Pipeline + kinematics + safety thresholds |
| `deploy/ci/` | ✅ Real | build.sh, test.sh, lint.sh |
| `skills/` | ✅ 23 dirs | Knowledge base for reusable workflows |

---

## What Is Missing

| Category | Item | Priority | Notes |
|----------|------|----------|-------|
| **Documentation** | README.md | ✅ Done | Created (CP-002) |
| **CI/CD** | GitHub Actions | ✅ Done | Created (CP-003) |
| **Validation** | Input validation | P1 | Pipeline __init__ needs validation |
| **Error Handling** | animateNominal() | P1 | Needs try/catch wrapper |
| **Data** | External data ingestion | P2 | All data currently synthetic |
| **Tests** | Integration tests | P2 | Only unit tests exist |
| **Monitoring** | Observability | P3 | No logging/metrics beyond console |

---

## What Matters

### Safety-Relevant
- **Kinematics engine accuracy** — 2.5ms timestep is standard for collision detection
- **Monte Carlo sample count** — 10,000 samples with 2.5ms timestep per sample = ~25 seconds runtime
- **Bayesian EVT tail risk** — Method of Moments approximation documented as limitation
- **Jurisdiction thresholds** — USA (2.0s TTC, 4.0 DRAC), Canada (2.5s, 3.5), GB (1.5s, 5.0)

### Technical
- **Pure client-side demo** — No server required for single-scenario-demo
- **Client-server parity** — Python backend and JS frontend share same algorithms
- **Multi-jurisdiction support** — 3 jurisdictions with configurable thresholds

### Quality
- **46 passing tests** — Pipeline, kinematics, safety thresholds
- **Pytest + coverage** — Configured, needs expansion
- **Docker multi-stage** — Builder + slim runtime (debian-based)

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Single-Scenario Demo (Browser)                                        │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────┐│
│  │ kinematics.js│  │monte-carlo.js │  │bayesian-evt.js│ │visualization││
│  └──────────────┘  └───────────────┘  └──────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                │
                    (optional server-side pipeline)
                                │
┌─────────────────────────────────────────────────────────────────────────┐
│  Python Backend (src/risk_quantification/)                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  pipeline.py (7-step orchestrator)                                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐           │  │
│  │  │kinematics│→│indicators│→│Monte Carlo│→│  Bayesian │           │  │
│  │  └──────────┘ └──────────┘ └───────────┘ └──────────┘           │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐          │  │
│  │  │Collision Mdl│→│Safety Thty  │→│Portfolio Scoring  │          │  │
│  │  └─────────────┘ └──────────────┘ └──────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────┐  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  kinematics_engine.py (2.5ms timestep simulation)                 │  │
│  │  safety_thresholds/ (10 modules)                                  │  │
│  │  risk_scoring.py, threshold_checker.py                            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Standards & Compliance

- **ISO 26262** — Road vehicles functional safety
- **ISO 21448 (SOTIF)** — Safety of the Intended Functionality
- **UL 4600** — Standard for Autonomous Vehicles
- **NHTSA** — Guidelines for Automated Driving Systems
- **Transport Canada** — Autonomous Vehicle Framework
- **DfT GB** — Department for Transport Great Britain guidelines

---

*This file is updated continuously as the project evolves.*
