# AV_Safety Production Roadmap — Phased Implementation Plan

> **Document purpose:** Master roadmap for hardening, validating, and deploying the AV_Safety portfolio UI until production-ready. Every phase maps to the 13 mandatory production layers.
>
> **Created:** 2026-06-06
> **Status:** Awaiting user approval
> **Author:** Forge (Orchestrator Agent)

---

## Executive Summary

The AV_Safety project is a portfolio piece demonstrating deep technical expertise in autonomous vehicle safety through quantitative collision risk modeling. It currently has **one working demo scenario (RE-CA-001)** across 42 defined, a 7-step Python pipeline, a Three.js/Pyodide frontend, and 22 skill packages — but lacks production readiness across most of the 13 required layers.

**Scope of this plan:** 6 phases spanning cleanup → pipeline hardening → portfolio UI → scalability to 42 scenarios → testing/stress → deployment. Each phase contains concrete, testable tasks mapped to layers.

**Estimated effort:** Sequential 6 phases. Phase 1 (cleanup) is the highest-risk foundation — it blocks all downstream work.

---

## Current State Evidence

### What Exists ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| `single-scenario-demo/` | 1 scenario working (RE-CA-001) | `index.html`, `app.js`, 4 JS modules |
| Python backend | 2 packages (risk_quantification, safety_thresholds) | 16 Python files |
| Scenario data | 42 conflict scenarios defined in taxonomy | `skills/scenario-taxonomy/` |
| Scenario spec file | RE-CA-001 fully parameterized | `data/scenario-RE-CA-001.json` |
| Tests | 15 passing pipeline tests | `tests/test_pipeline.py` |
| Docker setup | docker-compose.yml, Dockerfile, nginx.conf | `deploy/` |
| Skills | 22 skill packages | `skills/` |
| Documentation | Project overview, blueprint, architecture docs | `docs/`, `Project_Overview.md`, `Portfolio_Blueprint.md`, `STATUS.md` |
| Standards models | UL 4600, ISO 21448, ISO 26262 | `src/safety_thresholds/standards.py`, `docs/standards/` |

### What Is Broken 🔴

| Issue | Severity | Location | Evidence |
|-------|----------|----------|----------|
| **Dockerfile ENTRYPOINT conflict** | Critical | `deploy/Dockerfile` | ENTRYPOINT hardcoded to `uvicorn`; docker-compose.yml builds both UI and API from same image. docker-entrypoint.sh supports UI but Dockerfile never calls it. UI service cannot run from this container. |
| **Monte Carlo is heuristic** | Critical | `single-scenario-demo/modules/monte-carlo.js` | Does NOT call kinematics engine. Uses random parameter perturbation around nominal values without physical trajectory computation. Skips collision detection entirely. |
| **Risk scoring weights are arbitrary** | High | `risk-scoring.js` (JS) and `risk_scoring.py` (Python) | Both use hardcoded 0.3/0.3/0.2/0.2 with no empirical basis. No calibration against real crash data. JS `RiskScorer.compute()` differs from Python `RiskScorer.score()` — different method signatures and field names. |
| **app.js missing** | Critical | `single-scenario-demo/` | File exists but its first 5 lines show it's a stub. Full wiring code (DOM setup, Three.js initialization, scenario loader) is not present. Demo does not render. |
| **indicator-catalog.js referenced but missing** | High | `single-scenario-demo/modules/` | 42 indicators defined in skills but no JS module to compute or catalog them. |
| **Empty data directories** | High | `data/raw/`, `data/processed/`, `models/` | No crash data ingested (NHTSA FARS, CISS, Transport Canada, DfT GB). |
| **No frontend tests** | High | `single-scenario-demo/` | Zero JavaScript test coverage. |
| **No CI/CD** | Critical | Repository root | No `.github/workflows/`, no Makefile, no pre-commit hooks. |

### Partial / Needs Improvement 🟡

| Component | Gap | Location |
|-----------|-----|----------|
| Bayesian EVT threshold selection | Slope stability heuristic is fragile; MRL linear region detection may misclassify | `bayesian-evt.js` |
| Scenario JSON schema | Richly documented for RE-CA-001 but not validated as a schema (no JSON Schema definition) | `data/scenario-RE-CA-001.json` |
| Docker networking | docker-compose.yml runs UI and API in same container (no service-level isolation) | `deploy/docker-compose.yml` |
| API | FastAPI app exists but no OpenAPI docs, no health check endpoint visible in pipeline.py | `pipeline.py` |
| Documentation | 2 empty dirs (`docs/standards/`, `docs/research/`), empty `docs/architecture/handoff.md` | `docs/` |

### Missing Completley 🔴

| Component | Why It Matters |
|-----------|---------------|
| **Portfolio UI** (multi-scenario) | Single demo must become a full portfolio with scenario selector, comparison view, export |
| **3D animation pipeline** | Three.js exists in visualization.js but needs 3D scene rendering for conflict trajectories |
| **Persistent state / database** | No SQLite/Postgres; scenario runs can't be replayed, audited, or compared |
| **Workflow orchestration** | No task scheduling, event-driven execution, or durable workflow engine |
| **Monitoring / telemetry** | No metrics, logging, alerting |
| **Security hardening** | No auth, no input validation on API, no data encryption |

---

## 13-Layer Gap Analysis

| # | Layer | Current | Target | Gap |
|---|-------|---------|--------|-----|
| 1 | Interaction & Control Plane | Single demo HTML, stub app.js | Multi-scenario portfolio UI + FastAPI with OpenAPI | 🔴 Major |
| 2 | Core Application & Hosting Infrastructure | Broken Dockerfile, no service isolation | Clean multi-container compose, health checks | 🔴 Major |
| 3 | Data Ingestion & Semantic Data Foundation | Empty data dirs | Ingest NHTSA FARS, CISS, T-C, DfT GB | 🔴 Major |
| 4 | Business Context & Semantic Modeling | 42 indicators defined | Full implementation + validation against standards | 🟡 Partial |
| 5 | Memory & State Management | None | SQLite for scenario runs, execution history | 🔴 Major |
| 6 | Tools & Integration Layer | None | MCP adapter, external API connectors | 🔴 Major |
| 7 | Execution & Workflow Orchestration | None | Celery/RQ task queue or in-process workflow engine | 🔴 Major |
| 8 | Model Gateway & Semantic Caching | Pyodide in-browser only | Server-side model caching, fallback chains | 🟡 Partial |
| 9 | Safety & Guardrails | Threshold checker exists | Input validation, output verification, constraint enforcement | 🟡 Partial |
| 10 | Prompt & Interaction Design | None | Scenario selection UX, explanation panels, export dialogs | 🔴 Major |
| 11 | Evaluation & Telemetry | None | Metrics, logging, dashboard | 🔴 Major |
| 12 | Experimentation & Continuous Improvement | None | A/B scenario comparison, version tracking | 🔴 Major |
| 13 | Security, Compliance & Governance | Standards models exist | Auth, audit trails, data protection | 🟡 Partial |

---

## Phase 0: Foundation — Cleanup & Repair (Blocks Everything)

**Objective:** Fix the broken infrastructure so all downstream work has a stable foundation.

**Duration:** 1–2 days of execution

**Layers affected:** 2 (Core Infrastructure), 9 (Safety), 13 (Governance)

### Task 0.1: Fix Dockerfile ENTRYPOINT
- **Problem:** ENTRYPOINT hardcodes `uvicorn`, making UI deployment impossible from the same Dockerfile.
- **Fix:** Make the Dockerfile agnostic of service type. Entrypoint determines service at runtime via `SERVICE` env var.
- **Evidence:** `deploy/Dockerfile` line: `ENTRYPOINT ["python3", "-m", "uvicorn"]` + `docker-entrypoint.sh` already supports `api`/`ui`/`worker` modes.
- **Change:** Remove ENTRYPOINT from Dockerfile, use `ENTRYPOINT ["./docker-entrypoint.sh"]`, verify both services start.

### Task 0.2: Split Docker Compose into Proper Services
- **Problem:** `docker-compose.yml` builds UI and API from the same container — no service-level isolation.
- **Fix:** Create separate service definitions. UI service uses static file server or nginx directly. API service uses uvicorn.
- **Architecture decision:** Use a single Dockerfile for API (Python), separate lightweight nginx:alpine image for UI.

### Task 0.3: Validate Docker Compose Stack
- **Change:** `docker-compose up -d` → verify all 4 services (`dev`, `risk-api`, `portfolio-ui`, `nginx`) start.
- **Verify:** `http://localhost:8000` responds (API), `http://localhost:80` serves static files (UI), `http://localhost:8080` routes `/api/` to upstream.
- **Evidence:** curl responses, container status via `docker ps`.

### Task 0.4: Establish Pre-commit & Git Hooks
- **Change:** Create `.pre-commit-config.yaml` with basic hooks (black/isort for Python, eslint for JS).
- **Evidence:** `pre-commit run --all-files` succeeds.

### Task 0.5: Create `.github/workflows/ci.yml`
- **Change:** CI pipeline with Python tests + JS lint + Docker build test.
- **Evidence:** GitHub Actions workflow runs on `git push`.

**Phase 0 acceptance criteria:**
- [ ] `docker-compose up -d` starts API and UI services without errors
- [ ] API responds at `localhost:8000` with JSON
- [ ] UI serves static files at `localhost:80`
- [ ] Nginx proxy routes `/api/` correctly at `localhost:8080`
- [ ] `pre-commit run --all-files` passes
- [ ] GitHub Actions CI trigger exists

---

## Phase 1: Backend Pipeline Hardening

**Objective:** Repair the Python backend so the 7-step pipeline computes real values, not heuristics.

**Duration:** 3–5 days of execution

**Layers affected:** 1 (API), 2 (Infrastructure), 3 (Data), 4 (Business Context), 5 (State), 9 (Safety)

### Task 1.1: Audit Python Pipeline Flow End-to-End
- **Action:** Read every Python file in `src/risk_quantification/` and `src/safety_thresholds/`.
- **Map:** Trace `pipeline.py::run()` → step 1 (kinematics) → step 2 (indicators) → step 3 (Monte Carlo) → step 4 (EVT) → step 5 (collision) → step 6 (thresholds) → step 7 (portfolio).
- **Verify:** Each step actually calls the previous step's output, or identify where data flows are broken.
- **Evidence:** Document the actual data flow in `docs/architecture/pipeline-flow.md`.

### Task 1.2: Implement Real Kinematics Engine in Python
- **Problem:** JS kinematics.js exists but Python has no equivalent. The pipeline references kinematics but may not compute trajectories.
- **Action:** Create `src/risk_quantification/kinematics.py` with proper rear-end collision kinematics equations (relative motion, TTC, time-to-braking, collision detection).
- **Classes:** `RearEndKinematics`, `CrossingKinematics`, etc. per conflict type.
- **Tests:** Unit tests in `tests/test_kinematics.py` validating known scenarios (e.g., RE-CA-001 nominal case avoids collision at 30m headway).

### Task 1.3: Fix Monte Carlo to Use Real Kinematics
- **Problem:** `monte-carlo.js` uses heuristic perturbation, not kinematics-based simulation.
- **Action:** Replace with Python Monte Carlo that calls `kinematics.py` for each simulation run. Sample parameters from distributions (reaction time, headway, friction, speed).
- **Implementation:** `src/risk_quantification/monte_carlo.py` — 10,000 samples, collision detection, TTC/ΔV extraction.
- **Tests:** Validate that collision rate converges to expected range (2-5% for RE-CA-001 nominal).

### Task 1.4: Fix Risk Scoring Weight Calibration
- **Problem:** Arbitrary 0.3/0.3/0.2/0.2 weights. JS and Python have different method signatures.
- **Action:** Harmonize JS and Python `RiskScorer` APIs. Replace weights with calibration methodology based on NHTSA injury data or UL 4600 criteria.
- **Implementation:** Add weight documentation + optional calibration function. Keep defaults but add `from_calibration()` factory method.
- **Tests:** `tests/test_risk_scoring.py` validates both JS (via Pyodide) and Python scorers produce equivalent results.

### Task 1.5: Implement Safety Threshold Validation
- **Action:** Ensure `threshold_checker.py` validates all 42 indicators against UL 4600 / ISO 21448 / ISO 26262 thresholds.
- **Output:** Per-indicator compliance pass/fail + safety margin percentage.
- **Tests:** `tests/test_threshold_checker.py` for all 3 jurisdictions.

### Task 1.6: Add API Health Check + OpenAPI Docs
- **Action:** Ensure FastAPI app in `pipeline.py` has `/health` endpoint, `/docs` enabled, request validation via Pydantic.
- **Evidence:** `curl localhost:8000/health` returns `{"status": "ok"}`. `http://localhost:8000/docs` renders Swagger UI.

### Task 1.7: Add Scenario Schema Validation
- **Action:** Create JSON Schema for scenario specs. Validate all 42 scenario JSONs against it.
- **Implementation:** `src/risk_quantification/scenario_schema.py` — Pydantic model matching scenario JSON structure.
- **Evidence:** `python -m py_compile` passes, schema validates RE-CA-001 and rejects malformed input.

### Task 1.8: SQLite Database for Scenario Runs
- **Action:** Create SQLite database for persisting scenario runs, execution history, and results.
- **Schema:**
  - `scenarios` table: id, scenario_id, name, conflict_type, jurisdiction, created_at
  - `scenario_runs` table: id, scenario_id, parameters_json, results_json, status, created_at, duration_seconds
  - `indicators` table: run_id, indicator_name, value, percentile, threshold
- **Implementation:** `src/risk_quantification/database.py` — SQLite operations with connection pooling.
- **Tests:** `tests/test_database.py` validates CRUD operations.

**Phase 1 acceptance criteria:**
- [ ] Pipeline runs end-to-end with real kinematics (not heuristics)
- [ ] Monte Carlo calls kinematics for each sample
- [ ] Risk scoring produces calibrated scores with documented methodology
- [ ] API health check responds
- [ ] Scenario runs persist to SQLite
- [ ] All tests pass (`pytest tests/`)
- [ ] `coverage pytest` ≥ 60% coverage

---

## Phase 2: Frontend Repair & Demo Operationalization

**Objective:** Make the `single-scenario-demo` fully functional and visually accurate.

**Duration:** 3–5 days of execution

**Layers affected:** 1 (UI), 8 (Model Gateway), 10 (Prompt Design)

### Task 2.1: Diagnose and Fix app.js
- **Problem:** app.js exists but is incomplete. The demo "does not run."
- **Action:** Read current app.js in full. Identify missing DOM setup, Three.js scene initialization, scenario loader, and animation controller.
- **Fix:** Write complete `app.js` that:
  1. Loads scenario JSON
  2. Initializes Three.js 3D scene
  3. Runs kinematics + Monte Carlo + EVT pipeline
  4. Renders vehicle trajectories in 3D
  5. Displays indicator values, risk scores, and plots
- **Tests:** Manual browser test + automated Puppeteer/Playwright test.

### Task 2.2: Implement Missing indicator-catalog.js
- **Problem:** 42 indicators defined but no JS module exists.
- **Action:** Create `single-scenario-demo/modules/indicator-catalog.js` implementing all 42 indicators in JavaScript (parallel to Python `indicator-computation` skill).
- **Categories:** TTC, DTTC, PET, DeltaV, DRAC, PACJ, RLA, CP, CRI, PCE, etc.
- **Tests:** Unit tests for each indicator category.

### Task 2.3: Fix 3D Visualization Pipeline
- **Problem:** `visualization.js` exists but may not render 3D scenes. Need to verify Three.js + Canvas 2D rendering.
- **Action:** Audit `visualization.js`. Ensure it:
  1. Creates Three.js scene with road, vehicles, obstacles
  2. Animates vehicle trajectories from kinematics output
  3. Highlights collision points, critical moments
  4. Supports camera controls (orbit, zoom, timeline scrub)
- **Tests:** Render RE-CA-001, verify vehicles follow correct trajectories, collision animation plays.

### Task 2.4: Implement Monte Carlo Result Visualization
- **Action:** Add histogram/charts for Monte Carlo results: collision rate, TTC distribution, ΔV distribution, severity breakdown.
- **Technology:** Plotly.js or D3.js for interactive charts.
- **Tests:** Charts render with realistic data ranges.

### Task 2.5: Add Sensitivity Analysis UI
- **Action:** Build UI for sensitivity analysis (collision risk vs. severity). Sliders for headway, reaction time, speed. Real-time recalculation.
- **Evidence:** Moving sliders updates risk score, 3D scene, and charts in real time.

### Task 2.6: Frontend Test Suite
- **Action:** Set up Jest + Puppeteer for frontend tests.
- **Tests:** Load page → verify DOM elements render → verify 3D canvas initializes → verify scenario loads → verify charts render.
- **Coverage:** ≥ 50% JS test coverage.

**Phase 2 acceptance criteria:**
- [ ] `single-scenario-demo/index.html` loads and renders 3D scene in browser
- [ ] RE-CA-001 scenario runs end-to-end (kinematics → indicators → Monte Carlo → EVT → risk score → visualization)
- [ ] 3D animation shows vehicle trajectories with collision/non-collision states
- [ ] Sensitivity analysis UI responds to parameter changes
- [ ] All charts render correctly
- [ ] Frontend tests pass

---

## Phase 3: Portfolio UI — Multi-Scenario Experience

**Objective:** Transform single-scenario demo into full portfolio UI with 42-scenario support.

**Duration:** 5–7 days of execution

**Layers affected:** 1 (UI), 5 (State), 10 (Prompt Design), 12 (Experimentation)

### Task 3.1: Portfolio UI Architecture
- **Action:** Design portfolio UI with:
  1. **Scenario Browser** — grid/list of all 42 scenarios, filterable by conflict type, jurisdiction, severity
  2. **Scenario Detail** — click a scenario → loads full analysis (3D + charts + risk score + indicators)
  3. **Comparison View** — select 2-4 scenarios → side-by-side analysis
  4. **Export/Share** — download scenario results as JSON/HTML, shareable URL
- **Structure:** SPA with client-side routing (vanilla JS or lightweight framework). No React needed — keep it lightweight for portfolio demo.

### Task 3.2: Scenario Data Pipeline
- **Action:** Create a script to generate all 42 scenario JSON files from the taxonomy.
- **Implementation:** `scripts/generate-scenarios.py` — iterates 8 conflict types × sub-types × 3 jurisdictions × severity levels → outputs `data/scenario-*.json`.
- **Evidence:** 42 JSON files created, all validated against schema.

### Task 3.3: Scenario Loader
- **Action:** JavaScript module that loads any scenario JSON by ID, validates it, and populates the UI state.
- **Implementation:** `modules/scenario-loader.js` — fetches `data/scenario-{id}.json`, parses, sets global state, triggers UI update.
- **Tests:** Load all 42 scenarios, verify no parse errors.

### Task 3.4: Multi-Scenario API Endpoint
- **Action:** Add FastAPI endpoints for portfolio operations:
  - `GET /api/scenarios` — list all scenarios
  - `GET /api/scenarios/{id}` — get scenario detail
  - `POST /api/scenarios/{id}/run` — execute scenario analysis
  - `GET /api/scenarios/compare?ids=a,b,c` — comparison view
  - `GET /api/runs/{id}` — get execution history
- **Evidence:** curl all endpoints, Swagger UI shows them.

### Task 3.5: Scenario Browser UI
- **Action:** Build scenario browser with cards showing: scenario name, conflict type, jurisdiction, color-coded risk level, thumbnail 3D preview.
- **Evidence:** Browser renders all 42 scenario cards. Filtering by type/jurisdiction works.

### Task 3.6: Comparison View
- **Action:** UI for selecting multiple scenarios and comparing risk scores, collision rates, severity distributions side-by-side.
- **Evidence:** Select 3 scenarios → table shows comparative metrics → charts render side-by-side.

**Phase 3 acceptance criteria:**
- [ ] Portfolio UI lists all 42 scenarios
- [ ] Clicking a scenario loads full analysis (3D + charts + indicators)
- [ ] Comparison view works for 2-4 scenarios
- [ ] API supports all portfolio endpoints
- [ ] Scenario browser filters work
- [ ] Export generates valid downloadable file

---

## Phase 4: Data Ingestion & External Validation

**Objective:** Ingest real crash data and validate scenario models against it.

**Duration:** 5–7 days of execution

**Layers affected:** 3 (Data), 4 (Business Context), 11 (Evaluation), 13 (Governance)

### Task 4.1: Ingest NHTSA FARS Data
- **Action:** Download/process NHTSA FARS 2020 dataset. Parse CSV → clean → load into SQLite.
- **Mapping:** Map FARS collision types to AV_Safety conflict types. Compute baseline collision rates per type.
- **Evidence:** SQLite populated with FARS records. Baseline rates computed per conflict type.

### Task 4.2: Ingest CISS Data
- **Action:** Process California Integrated Highway Safety System (CISS) microsecond-level trajectory data.
- **Mapping:** Extract TTC, DTTC, PET values from CISS trajectories. Validate against indicator computations.
- **Evidence:** CISS statistics match indicator ranges.

### Task 4.3: Ingest Transport Canada & DfT GB Data
- **Action:** Process Canadian and UK crash databases. Validate scenario parameters against real-world distributions.
- **Evidence:** Jurisdiction-specific parameters (speed distributions, friction coefficients) calibrated.

### Task 4.4: Scenario Validation Against Real Data
- **Action:** For each of the 42 scenarios, compute validation metrics:
  - Collision rate similarity (simulated vs. real)
  - ΔV distribution fit (K-S test)
  - Severity classification accuracy
- **Output:** Validation report per scenario with pass/fail/needs-calibration.

### Task 4.5: Baseline Rate Calculator
- **Action:** Python function that computes baseline collision rates from ingested data, calibrated by jurisdiction, road type, and conflict type.
- **Output:** `baseline_rates.json` — used by threshold checker and risk scorer.

**Phase 4 acceptance criteria:**
- [ ] NHTSA FARS data ingested and validated
- [ ] CISS trajectory data processed
- [ ] Transport Canada + DfT GB data ingested
- [ ] All 42 scenarios validated against real data
- [ ] Baseline rates computed per jurisdiction/type

---

## Phase 5: Orchestration, Monitoring & Governance

**Objective:** Add production-grade infrastructure: workflow orchestration, monitoring, security, governance.

**Duration:** 5–7 days of execution

**Layers affected:** 5 (State), 6 (Tools), 7 (Orchestration), 8 (Model Gateway), 11 (Evaluation), 13 (Security)

### Task 5.1: Workflow Orchestration
- **Action:** Implement Celery or in-process async task queue for scenario analysis jobs.
- **Schema:** Task definition → execution → result storage → notification.
- **Features:** Job queuing, retry on failure, execution history, result caching.
- **API:** `POST /api/jobs` — submit analysis job; `GET /api/jobs/{id}` — check status.

### Task 5.2: Monitoring & Telemetry
- **Action:** Add structured logging (JSON), metrics collection (Prometheus-compatible), request tracing.
- **Implementation:** `src/risk_quantification/monitoring.py` — metrics for:
  - Pipeline duration per step
  - Monte Carlo sample count
  - Error rates
  - API latency percentiles
- **Dashboard:** Simple HTML dashboard or Grafana panel spec.

### Task 5.3: Semantic Caching
- **Action:** Cache expensive computations (Monte Carlo + EVT runs) by scenario ID + parameter hash.
- **Implementation:** SQLite-based cache with TTL. Skip recomputation for identical parameter sets.
- **API:** `GET /api/cache` — list cache; `DELETE /api/cache` — clear.

### Task 5.4: Security Hardening
- **Action:** Add:
  - Input validation (all API endpoints validate via Pydantic)
  - Rate limiting (simple token bucket)
  - CORS configuration
  - API key auth (for production deployment)
- **Evidence:** `curl` with/without API key → 401 without, 200 with.

### Task 5.5: Audit Trail
- **Action:** Log all scenario runs, API calls, and parameter changes to audit table in SQLite.
- **Schema:** `audit_log` — timestamp, action, user (api_key), entity_type, entity_id, changes_json.

### Task 5.6: Documentation — Architecture, Dependencies, Risks
- **Action:** Update/create all required documentation:
  - `docs/architecture/system-design.md` — full architecture diagram (ASCII/Markdown)
  - `docs/dependencies.md` — all external dependencies
  - `docs/risks.md` — technical risks, dependency risks, mitigations
  - `docs/testing-approach.md` — test strategy, coverage goals
  - `docs/deployment-approach.md` — staging → production pipeline

**Phase 5 acceptance criteria:**
- [ ] Workflow orchestration submits and tracks analysis jobs
- [ ] Monitoring logs structured JSON metrics
- [ ] Cache skips recomputation for identical inputs
- [ ] API validates all inputs, returns 401 without auth
- [ ] Audit trail records all operations
- [ ] All documentation files created/updated

---

## Phase 6: Stress Testing & Deployment Readiness

**Objective:** Validate production readiness through comprehensive testing and deploy to staging.

**Duration:** 3–5 days of execution

**Layers affected:** 1 (UI), 2 (Infrastructure), 11 (Evaluation), 12 (Experimentation)

### Task 6.1: Performance Testing
- **Action:** Load test the API:
  - 100 concurrent scenario analysis requests
  - Measure p50/p95/p99 latency
  - Verify no memory leaks in long-running processes
- **Evidence:** Benchmark script output with latency percentiles.

### Task 6.2: Stress Test the 3D Pipeline
- **Action:** Load all 42 scenarios in browser. Measure:
  - Time to first 3D render
  - Frame rate during animation
  - Memory usage over time
  - Chrome DevTools performance profile
- **Target:** First render < 2s, sustained 60fps, memory stable < 200MB.

### Task 6.3: Regression Test Suite
- **Action:** Comprehensive test suite covering:
  - All 13 pipeline steps
  - All 42 scenarios (automated computation)
  - UI interaction tests (scenario load, compare, export)
  - Edge cases (zero headway, infinite reaction time, negative speed)
- **Coverage:** ≥ 80% Python, ≥ 70% JavaScript.

### Task 6.4: Deployment Pipeline
- **Action:** Create staging → production deployment:
  - Staging: `docker-compose -f deploy/docker-compose.staging.yml up`
  - Production: Single-VM deployment with nginx reverse proxy
  - Zero-downtime deployment strategy (rolling restart)
- **Evidence:** Deploy to staging, verify all endpoints work.

### Task 6.5: GitHub Repository Hygiene
- **Action:** Update repository with:
  - `README.md` — project overview, setup instructions, demo link
  - `CONTRIBUTING.md` — contribution guidelines
  - `CHANGELOG.md` — version history
  - `.gitignore` — proper exclusions
  - `LICENSE` — MIT license
- **Evidence:** Repository clean, README renders correctly on GitHub.

### Task 6.6: Production Readiness Declaration
- **Action:** Final validation checklist (from IDENTITY.md):
  - [ ] Main conflict scenario (RE-CA-001) works end-to-end with 3D
  - [ ] Portfolio UI functional with multi-scenario support
  - [ ] Architecture covers all 13 layers
  - [ ] Tests exist and pass
  - [ ] Key flows verified with evidence
  - [ ] Stress tests run
  - [ ] Deployment readiness confirmed
  - [ ] Documentation updated
  - [ ] Open risks in Blockers.md
  - [ ] Remaining work in STATUS.md and Task_Ledger.md

**Phase 6 acceptance criteria:**
- [ ] API handles 100 concurrent requests
- [ ] Browser renders 42 scenarios without crashing
- [ ] Test coverage ≥ 80% Python, ≥ 70% JavaScript
- [ ] Deploy to staging succeeds
- [ ] All production readiness checklist items pass

---

## Task Ledger

See `Task_Ledger.md` for detailed task breakdown with IDs, dependencies, assignee, and status.

## Validation Log

See `Validation_Log.md` for test results, validation evidence, and benchmark data.

## Open Issues

See `Open_Issues.md` for active issues and their status.

## Blockers

See `Blockers.md` for items blocking progress.

## Run Checkpoints

See `Run_Checkpoints.md` for checkpoint logs of major operations.

---

## Dependencies & Ordering

```
Phase 0 (Foundation)
  ├── Phase 1 (Backend Pipeline) ← blocked by 0.1, 0.2
  ├── Phase 2 (Frontend Repair) ← blocked by 0.3, 1.1
  ├── Phase 3 (Portfolio UI) ← blocked by 2.1, 2.3, 1.4, 3.4
  ├── Phase 4 (Data Ingestion) ← blocked by 1.2, 1.3
  ├── Phase 5 (Orchestration) ← blocked by 3.2, 3.4, 1.8
  └── Phase 6 (Stress & Deploy) ← blocked by 3.1, 4.4, 5.1, 5.4
```

**Critical path:** Phase 0 → Phase 1 → Phase 3 → Phase 6

**Parallelizable:** Phase 2 (frontend) can run alongside Phase 1 (backend) once Phase 0 is done. Phase 4 (data) can run alongside Phase 3 once Phase 1 is done.

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Pyodide in-browser performance too slow for 10K MC samples | Latency > 30s | Pre-compute on server, cache results |
| 42 scenario JSONs too large for client-side loading | Memory > 500MB | Paginated loading, lazy-load 3D |
| Monte Carlo results diverge from real data | Invalid analysis | Calibrate parameters in Phase 4 |
| Docker multi-service compose unstable | Deployment failure | Test each service independently first |
| Three.js 3D rendering crashes on complex scenes | UX failure | Add loading indicators, graceful degradation |
| Python 3.14.5 dependency conflicts | Build failure | Pin all versions, test in clean virtualenv |

---

## Approval & Next Steps

**This plan requires user approval before execution.**

Upon approval, I will:

1. **Begin Phase 0 immediately** — fixing the Dockerfile, docker-compose, and CI/CD foundation
2. **Maintain checkpoints** — recording progress in `Run_Checkpoints.md` and `STATUS.md`
3. **Report milestones** — after each phase, providing evidence-based status updates
4. **Continue in closed loop** — discovering, planning, implementing, verifying, improving, persisting

---

_Document version: 1.0 | Created: 2026-06-06 | Author: Forge_
