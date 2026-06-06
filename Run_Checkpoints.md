# Run Checkpoints — AV_Safety

**Active Session:** 2026-06-06 (Orchestrator Agent)  
**Agent:** Orchestrator — Principal Systems Engineer  
**Status:** Phase 1 — Deep Investigation Complete, Implementation Starting

---

## Checkpoint Log

### CP-001: Deep Repository Discovery (2026-06-06)
- ✅ Read full file tree (210+ files)
- ✅ Read all 8 documentation/markdown files (Project_Overview, Blueprint, Roadmap, Ledger, Validation, Issues, Blockers, Checkpoints)
- ✅ Read single-scenario-demo/ (8 files: index.html, style.css, scenario JSON, 5 JS modules)
- ✅ Read src/ Python packages (pipeline.py, risk_scoring.py, threshold_checker.py, results_aggregator.py, output_formats.py, report_generator.py, pipeline_validation.py, standards.py, collision_rate_thresholds.py, baseline_estimator.py, deployment_criteria.py)
- ✅ Read deploy/ (Dockerfile, docker-compose.yml, docker-entrypoint.sh, ci/*.sh, nginx.conf, .env.production)
- ✅ Read root config (requirements.txt, .env.example, docker-compose.yml)
- ✅ Read skills/ (23 directories, 19 skill SKILL.md files assessed)
- ✅ Read tests/ (conftest.py, test_pipeline.py — 15 tests)
- **Decision:** Deep understanding complete. Phase 2 implementation begins now.

---

## Critical Findings

### Immediate Bugs (Block Runtime)
1. **`app.js` is MISSING** — `single-scenario-demo/index.html` references `<script src="app.js">` but the file does not exist. The demo is non-functional in any browser.
2. **Dockerfile ENTRYPOINT runs uvicorn but uvicorn is NOT in requirements.txt** — Python dependency list missing: uvicorn, fastapi
3. **No `__init__.py` in some package dirs** — `src/` lacks `__init__.py`, `src/risk_quantification/` and `src/safety_thresholds/` checked (appear present)
4. **Dockerfile COPY paths may not align** — Dockerfile copies `src/` but docker-compose maps volumes differently

### Architecture Gaps
5. **Monte Carlo in Python uses heuristic approximations, NOT the kinematics engine** — `_run_monte_carlo()` computes TTC analytically instead of calling the full kinematics simulation
6. **Bayesian EVT uses Method of Moments, NOT PyMC** — No actual Bayesian inference; profile likelihood is JS-only
7. **Risk scoring weights (0.3/0.3/0.2/0.2) are arbitrary** — No derivation or justification
8. **Pipeline does not produce real TTC/DRAC distributions** — Monte Carlo returns summary stats from heuristic math
9. **Bayesian EVT JSON schema mismatch** — JS `bayesian-evt.js` expects `{xi: {estimate}}` but Python pipeline returns `{gpd_params: {xi}}`

### Missing Implementations
10. **No portfolio UI** — `portfolio-ui/` skill exists but no implementation
11. **CI/CD: No GitHub Actions workflows** — deploy/ci/ scripts exist but no `.github/workflows/`
12. **No README.md** — Project has no entry-level documentation
13. **No `.github/` directory at all**
14. **No external data ingested** — All data directories empty
15. **Tests directory has only pipeline tests** — No tests for risk_scoring, threshold_checker, results_aggregator, output_formats, report_generator, pipeline_validation
16. **Skills `driver.py` files missing** — All skills lack executable driver scripts

### Quality Concerns
17. **Collision detection uses 0.01m tolerance** — 1cm tolerance may miss edge collisions
18. **Monte Carlo in demo uses sync loop** — 10k samples blocks UI thread
19. **Three.js post-processing commented out** — Bloom/film effects not working
20. **Visualization vehicle positions not using trajectory correctly** — updatePositions() sets absolute positions instead of relative trajectory
21. **CSV exporter references `_get_fieldnames()` on wrong class** — `CsvExporter._get_fieldnames()` should not call `JsonExporter._get_fieldnames()`
22. **No error handling in visualization animation loop** — Crash in animation loop crashes entire demo
23. **Pipeline doesn't write results to disk** — No persistence between runs

---

## Implementation Plan

### Phase 1: Fix Runtime Blockers (Priority CRITICAL)
- [ ] 1.1 Create `app.js` for single-scenario-demo
- [ ] 1.2 Add uvicorn + fastapi to requirements.txt
- [ ] 1.3 Fix Dockerfile ENTRYPOINT/CMD alignment
- [ ] 1.4 Fix CSV exporter fieldnames reference

### Phase 2: Improve Core Pipeline (Priority HIGH)
- [ ] 2.1 Replace Python Monte Carlo heuristic with actual kinematics calls
- [ ] 2.2 Align Python/JS Bayesian EVT output schema
- [ ] 2.3 Add risk scoring weight derivation methodology
- [ ] 2.4 Add error handling to visualization animation loop

### Phase 3: Add Missing Infrastructure (Priority HIGH)
- [ ] 3.1 Create GitHub Actions CI/CD workflow
- [ ] 3.2 Create README.md
- [ ] 3.3 Create skill `driver.py` files
- [ ] 3.4 Add comprehensive test coverage

### Phase 4: Portfolio UI (Priority MEDIUM)
- [ ] 4.1 Implement portfolio UI (multi-scenario support)
- [ ] 4.2 Add scenario comparison view
- [ ] 4.3 Add export/share functionality

### Phase 5: Hardening (Priority MEDIUM-LOW)
- [ ] 5.1 Add async Monte Carlo with progress UI
- [ ] 5.2 Fix Three.js post-processing
- [ ] 5.3 Add Monte Carlo result caching
- [ ] 5.4 External data ingestion pipeline

---

## Recovery Information

**How to resume after interruption:**
1. Check last completed checkpoint in this file
2. Resume at next checkpoint number
3. Re-read relevant files if context was lost
4. Verify test status: `python3 -m pytest tests/ -v`
5. Check demo: open `single-scenario-demo/index.html` in browser

**State to preserve:**
- Run_Checkpoints.md — this file, tracks progress
- Task_Ledger.md — tracks individual tasks
- Open_Issues.md — tracks active issues
- Blockers.md — tracks blocking items

---

*Updated: 2026-06-06*  
*Last deep scan: CP-001 (full repository audit)*  
*Next checkpoint: CP-002 — Fix runtime blockers (Phase 1)*
