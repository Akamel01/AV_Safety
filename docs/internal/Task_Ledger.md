# Task Ledger — AV_Safety

**Last Updated:** 2026-06-07
**Total Tasks:** 37 (27 from Session 1 + 10 updated/new)

---

## Phase 0: Discovery (Complete — 0 remaining)

All discovery tasks completed in Session 1: repository scan, code verification, test execution, documentation audit.

---

## Phase 1: Critical Fixes (3 items — 2 fixed, 1 re-evaluated, 0 remaining open)

### CRIT-004: Pipeline Input Validation ✅ FIXED
- **Title:** Add input validation to `pipeline.__init__`
- **Fix:** Added scenario key validation (`scenario_id`, `road_users.vehicle_a/b`, `road_geometry`), vehicle data validation (velocity, acceleration, speed), `n_mc_samples` (positive int), jurisdiction (case-insensitive, known values: usa/canada/england), seed (positive int). Normalizes jurisdiction to lowercase before storage. 21 new validation tests covering all error paths.
- **Status:** ✅ **FIXED** — 21 validation tests + 46 original = **67/67 passing (17.86s)**
- **Verification:** All invalid inputs produce clear ValueError with specific missing field info — **MET**.
- **File:** `src/risk_quantification/pipeline.py` lines 78-98 (validation added lines 99-160)

### CRIT-003: Animation Error Handling ✅ FIXED
- **Title:** Add try/catch to `animateNominal()`
- **Fix:** Wrapped `frame()` function body (lines 244-282) in try/catch, added trajectory data validation (t, x_a, x_b must not be null/undefined before use), graceful error logging (`console.error`), animation stop on error (`AppState.animRunning = false; AppState.vizEngine?.stopAnimation()`).
- **Status:** ✅ **FIXED** — frame function now validates data before using, catches errors, logs them, and stops animation gracefully.
- **File:** `single-scenario-demo/app.js` lines 235-285

### CRIT-005: JS Module API Mismatches 🔵 RE-EVALUATED — No Real Mismatches
- **Title:** Cross-reference method calls in `app.js` with actual module exports
- **Finding:** Old analysis flagged 5 mismatches, but re-examination with regex that properly handles ES class syntax shows all app.js calls match module methods:
  - `kinematics.run()` — EXISTS
  - `mcEngine.run(n, callback)` — EXISTS
  - `vizEngine.updateHUD()`, `updatePositions()`, `render()`, `init3D()`, `toggleMode()` — ALL EXISTS
  - `bayesianEVT.init()`, `fitGPD()`, `fitGPDProfileLikelihood()`, `posteriorPredictiveCheck()`, `selectThresholdMRL()` — ALL EXISTS
  - `riskScorer.compute()` — EXISTS
- **Note:** The old analysis regex was designed for `this.method = function` style and missed ES class methods (`methodName(args) {`), producing false positives.
- **Status:** 🔵 **Re-evaluated** — old flags were regex false positives on ES class syntax. All JS API calls match module methods.

---
---

## Phase 2: Architecture (0 tasks — start after Phase 1)

1. **ARCH-001:** Verify visualization.js at `modules/visualization.js` (currently file not found at root)
   - **Dependencies:** None
   - **Priority:** P2
   - **Status:** 🟡 In Progress (path verification needed)

2. **ARCH-002:** Verify `deploy/ci/test.sh` and `deploy/ci/lint.sh` exist and work
   - **Dependencies:** None
   - **Priority:** P2
   - **Status:** 🔴 Open

3. **ARCH-003:** Choose canonical Dockerfile location (root vs deploy/)
   - **Dependencies:** None
   - **Priority:** P3
   - **Status:** 🟡 Documented

---

## Phase 3: Hardening (0 tasks — start after Phase 2)

3. **HARD-001:** Add input validation to pipeline (already listed as CRIT-004 above)
4. **HARD-002:** Audit silent failure propagation (pipeline.py line 163-167 catches all exceptions with `{}`)
   - **Priority:** P2
   - **Status:** 🟡 Documented

---

## Phase 4: Testing (partial — 46 tests pass, integration needed)

4. **TEST-001:** Add integration tests for full pipeline execution
   - **Dependencies:** Phase 1 fixes applied
   - **Priority:** P2
   - **Status:** 🔴 Open

5. **TEST-002:** Enable coverage measurement (pyproject.toml targets 80%)
   - **Dependencies:** None
   - **Priority:** P2
   - **Status:** 🟡 Partial (CI has --cov flag but uses continue-on-error)

6. **TEST-003:** Add regression tests for known gap: Bayesian EVT Method of Moments
   - **Dependencies:** None
   - **Priority:** P3
   - **Status:** 🔴 Open

---

## Phase 5: CI/CD (partial)

5. **CI-001:** Implement container registry deployment (currently placeholder)
   - **Dependencies:** Phase 1 complete
   - **Priority:** P3
   - **Status:** 🔴 Open

---

## Phase 6: Deployment (0 tasks — start after Phase 1)

6. **DEP-001:** Create `/data/` directory structure for external data
   - **Dependencies:** Phase 1 complete
   - **Priority:** P2
   - **Status:** 🔴 Open

7. **DEP-002:** Create validation scripts for benchmark comparisons
   - **Dependencies:** Phase 1 complete
   - **Priority:** P2
   - **Status:** 🔴 Open

---

## Blockers

| # | Issue | Impact | Status |
|---|-------|--------|--------|
| BLK-001 | No external data source configured | Limits testing scope | Awaiting |
| BLK-002 | No deployment target specified | Can't plan rollout | Awaiting |

---

## Legend

| Status | Meaning |
|--------|---------|
| ✅ | Complete, verified |
| 🔄 | In progress |
| 🔴 | Open, not started |
| 🟡 | Partial / documented |
| P1/P2/P3 | Priority levels |

---

*This ledger is updated continuously. Last verified: 2026-06-07. CRIT-005 added as new critical finding from Session 2 re-verification.*
