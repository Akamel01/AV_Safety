# AV_Safety — Production Objectives List

**Created:** 2026-07-05  
**Driver:** Orchestrator Agent  
**Status:** Active

---

## Objective Framework

Derived from: `Project_Overview.md` strategic objectives, `Portfolio_Blueprint.md` architecture, `handoff.md` roadmap, and current blockers.

**Goal:** Drive AV_Safety from Phase 1 (25% complete) → Phase 5 (Production Ready) with measurable, verifiable outcomes.

---

## Objectives by Phase

### Phase 1: Critical Bug Fixes (In Progress — 25%)

#### O1.1: Single-Scenario Demo Functional [CRITICAL]
- **Goal:** `single-scenario-demo/index.html` runs without errors
- **Current:** Monte Carlo null-reference fixed, app.js missing, Bayesian EVT shows error
- **Definition of Done:**
  - [x] Monte Carlo simulation runs without crashes (null-reference fix)
  - [ ] `app.js` created with proper initialization and Monte Carlo execution
  - [ ] All demo buttons work (Monte Carlo, Bayesian EVT, Reset)
  - [ ] Zero console errors during full user journey
  - [ ] Scenario data loads via fetch() over HTTP
- **Validation:** Open demo in browser, run full simulation, verify zero errors
- **Dependencies:** None

#### O1.2: Python Backend Dependencies [HIGH]
- **Goal:** All runtime dependencies declared and consistent
- **Current:** uvicorn/fastapi missing from requirements.txt, Dockerfile misaligned
- **Definition of Done:**
  - [ ] `uvicorn` and `fastapi` added to `requirements.txt`
  - [ ] Dockerfile ENTRYPOINT matches CMD and packages
  - [ ] Docker build succeeds
  - [ ] Docker run succeeds
- [ ] Validation: `docker build -t av-safety . && docker run -p 9000:8000 av-safety`
- **Dependencies:** None

#### O1.3: CSV Exporter Working [MEDIUM]
- **Goal:** Results export to CSV successfully
- **Current:** Fieldnames reference error
- **Definition of Done:**
  - [ ] CSV exporter imports correct fieldnames
  - [ ] Export triggers on button click
  - [ ] CSV file downloads with expected columns
- **Validation:** Run simulation, click export, verify CSV content
- **Dependencies:** O1.1

### Phase 2: Core Pipeline Fix (Not Started)

#### O2.1: Monte Carlo Uses Real Kinematics [HIGH]
- **Goal:** Monte Carlo calls kinematics engine (not heuristic)
- **Current:** Returns summary stats from math approximations
- **Definition of Done:**
  - [ ] `monte_carlo.js` imports/calls `kinematics.js` functions
  - [ ] Parameter sampling feeds trajectory computation
  - [ ] Trajectory results feed indicator computation
  - [ ] Indicator values feed Monte Carlo collapse
- **Validation:** Compare MC results with/without kinematics, verify realistic distributions
- **Dependencies:** O1.1

#### O2.2: Bayesian EVT Schema Aligned [HIGH]
- **Goal:** Python/JS compatible output schemas
- **Current:** Python `{gpd_params: {xi}}`, JS expects `{xi: {estimate}}`
- **Definition of Done:**
  - [ ] Python output wraps GPD params in `{estimate, ci_lower, ci_upper, n_samples}`
  - [ ] JS handles both schemas (backward compatible)
  - [ ] Bayesian EVT button displays results without errors
  - [ ] GPD parameters displayed with confidence intervals
- **Validation:** Click Bayesian EVT button, verify parameters displayed with CI
- **Dependencies:** O2.1

#### O2.3: Risk Scoring Weights Derived [MEDIUM]
- **Goal:** Risk scoring weights have defensible derivation
- **Current:** Weights 0.3/0.3/0.2/0.2 are arbitrary
- **Definition of Done:**
  - [ ] Weight derivation methodology documented
  - [ ] Weights sum to 1.0
  - [ ] Sensitivity analysis shows weight impact
  - [ ] Weights configurable via scenario JSON
- **Validation:** Change weights, verify risk scores change proportionally
- **Dependencies:** O2.1

### Phase 3: Missing Infrastructure (Not Started)

#### O3.1: CI/CD Pipeline [HIGH]
- **Goal:** Automated testing and deployment
- **Current:** No `.github/workflows/`
- **Definition of Done:**
  - [ ] `.github/workflows/test.yml` — runs tests on push/PR
  - [ ] `.github/workflows/lint.yml` — runs linting
  - [ ] `.github/workflows/build.yml` — builds Docker on push to main
  - [ ] `.github/workflows/deploy.yml` — deploys on tag
- **Validation:** Create test PR, verify CI runs, verify build/deploy
- **Dependencies:** O3.2

#### O3.2: README and Documentation [HIGH]
- **Goal:** Project entry documentation for onboarding
- **Current:** No README
- **Definition of Done:**
  - [ ] `README.md` with overview, quickstart, architecture
  - [ ] `CONTRIBUTING.md` with development guidelines
  - [ ] `docs/` with architecture, API, deployment guides
  - [ ] All code files have docstrings
- **Validation:** New contributor can set up project from README alone
- **Dependencies:** None

#### O3.3: Skill Driver Files [MEDIUM]
- **Goal:** All 18 skills have executable `driver.py`
- **Current:** All skills lack driver.py
- **Definition of Done:**
  - [ ] Each skill has `driver.py` entry point
  - [ ] Drivers runnable standalone: `python skills/X/driver.py`
  - [ ] Drivers accept CLI arguments
  - [ ] Drivers produce documented output
- **Validation:** Run each skill driver, verify output
- **Dependencies:** O2.1-O2.3

#### O3.4: Test Coverage [HIGH]
- **Goal:** 80% test coverage
- **Current:** 15 tests pass (pipeline only), 0% coverage
- **Definition of Done:**
  - [ ] `tests/` directory with pytest config
  - [ ] Unit tests for: kinematics, indicators, monte_carlo, bayesian_evt, collision_modeling, safety_thresholds
  - [ ] Integration tests for: pipeline, CSV export, demo data
  - [ ] Coverage >= 80% (pytest-cov)
  - [ ] Tests run in CI (O3.1)
- **Validation:** `pytest tests/ -v --cov=src` shows 80%+
- **Dependencies:** O2.1

### Phase 4: Portfolio UI (Not Started)

#### O4.1: Multi-Scenario Support [MEDIUM]
- **Goal:** Demo supports 20+ scenarios, 8 conflict types
- **Current:** 1 scenario (RE-CA-001)
- **Definition of Done:**
  - [ ] Scenario selector UI
  - [ ] 20+ scenario JSON files
  - [ ] Scenario data follows defined schema
  - [ ] Demo loads any scenario dynamically
  - [ ] Scenario comparison feature
- **Validation:** Switch between 5 scenarios, verify each loads
- **Dependencies:** O3.4

#### O4.2: Comparison View [LOW]
- **Goal:** Compare multiple scenarios' risk profiles
- **Current:** Single scenario view
- **Definition of Done:**
  - [ ] Multi-select scenario picker
  - [ ] Side-by-side or overlaid risk visualization
  - [ ] Export comparison to CSV/PDF
  - [ ] Shareable comparison URL
- **Validation:** Select 3 scenarios, compare, export
- **Dependencies:** O4.1

### Phase 5: Hardening (Not Started)

#### O5.1: Async Monte Carlo [MEDIUM]
- **Goal:** Monte Carlo runs without blocking UI
- **Current:** Synchronous execution blocks UI
- **Definition of Done:**
  - [ ] Monte Carlo in Web Worker (browser) or async task (Python)
  - [ ] Progress bar shows simulation progress
  - [ ] UI remains responsive
  - [ ] Results displayed when complete
- **Validation:** Run simulation, verify UI not blocked
- **Dependencies:** O2.1

#### O5.2: Data Ingestion [HIGH]
- **Goal:** External crash data ingested for validation
- **Current:** All data directories empty
- **Definition of Done:**
  - [ ] NHTSA FARS data ingested
  - [ ] Transport Canada data ingested
  - [ ] DfT GB data ingested
  - [ ] Data validation pipeline
  - [ ] Ingested data used for GPD comparison
- **Validation:** Compare GPD predictions vs real crash data
- **Dependencies:** O2.2

#### O5.3: Production Deployment [LOW]
- **Goal:** Demo and API deployed to production
- **Current:** Local development only
- **Definition of Done:**
  - [ ] Demo deployed (GitHub Pages/Vercel)
  - [ ] API deployed (AWS/GCP)
  - [ ] HTTPS configured
  - [ ] Monitoring/logging enabled
  - [ ] Deployment documented
- **Validation:** Access deployed demo via public URL
- **Dependencies:** O4.1

---

## Summary Metrics

| Objective | Phase | Priority | Status | Progress |
|-----------|-------|----------|--------|----------|
| O1.1 Demo Functional | 1 | CRITICAL | In Progress | 10% |
| O1.2 Python Backend | 1 | HIGH | Not Started | 0% |
| O1.3 CSV Exporter | 1 | MEDIUM | Not Started | 0% |
| O2.1 MC Real Kinematics | 2 | HIGH | Not Started | 0% |
| O2.2 Bayesian Schema | 2 | HIGH | Not Started | 0% |
| O2.3 Risk Weights | 2 | MEDIUM | Not Started | 0% |
| O3.1 CI/CD | 3 | HIGH | Not Started | 0% |
| O3.2 README | 3 | HIGH | Not Started | 0% |
| O3.3 Skill Drivers | 3 | MEDIUM | Not Started | 0% |
| O3.4 Test Coverage | 3 | HIGH | Not Started | 0% |
| O4.1 Multi-Scenario | 4 | MEDIUM | Not Started | 0% |
| O4.2 Comparison View | 4 | LOW | Not Started | 0% |
| O5.1 Async MC | 5 | MEDIUM | Not Started | 0% |
| O5.2 Data Ingestion | 5 | HIGH | Not Started | 0% |
| O5.3 Production Deploy | 5 | LOW | Not Started | 0% |

**Total:** 15 objectives  
**Phase 1:** 0/3 complete (0%)  
**Phase 2-5:** 0/12 complete (0%)  
**Overall:** 0/15 complete (0%)

---

*This objectives list drives the project to production. Update progress after every work session.*
