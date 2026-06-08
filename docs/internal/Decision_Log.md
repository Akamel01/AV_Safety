# Decision Log — AV_Safety

**Last Updated:** 2026-06-07

---

## Decisions Made (Verified from Source)

### DEC-001: Backend Uses Real Kinematics (Not Heuristics)
- **Date:** 2026-06-07 (Session 1 discovery)
- **Decision:** Pipeline step 3 (Monte Carlo) calls `kinematics_engine.run_monte_carlo_samples()` — full 2.5ms timestep simulation, not heuristic approximation.
- **Evidence:** `pipeline.py` line 221-258: `from src.risk_quantification.kinematics_engine import run_monte_carlo_samples; mc_results = run_monte_carlo_samples(n_samples, distributions, seed)`
- **Why:** Real simulation is required for safety-critical research. Heuristics insufficient for regulatory compliance.
- **Status:** ✅ Verified (code read + tests pass)

### DEC-002: Bayesian EVT Uses Method of Moments
- **Date:** 2026-06-07 (Session 1 discovery)
- **Decision:** Use Method of Moments approximation for GPD parameters (not full PyMC inference). Full PyMC commented out in requirements.txt.
- **Evidence:** `requirements.txt` comments: "pymc/pystan/arviz removed — unused by current pipeline. Re-enable for server-side full Bayesian inference"
- **Why:** Method of Moments is sufficient for research-grade demo. Full inference adds dependency complexity.
- **Status:** ✅ Verified (code read), documented as known gap (HIGH-002)

### DEC-003: Client-Side Only for Demo
- **Date:** 2026-06-07 (Session 1 design)
- **Decision:** Browser demo runs entirely client-side via Pyodide. No server required.
- **Evidence:** `index.html` loads 5 module JS files + app.js, initializes all engines in browser.
- **Why:** Lowers barrier to entry for researchers, enables offline use.
- **Status:** ✅ Verified (code read)

### DEC-004: Safety Thresholds Per Jurisdiction
- **Date:** 2026-06-07 (Session 1 design)
- **Decision:** TTC/DRAC thresholds defined per UL 4600 and ISO 21448 (SOTIF), not generic values.
- **Evidence:** `safety_thresholds/ttc_thresholds.py`: 4 levels (critical: 1.0s, dangerous: 2.0s, warning: 3.0s, safe: 5.0s)
- **Why:** Regulatory compliance requires jurisdiction-specific thresholds.
- **Status:** ✅ Verified (code read)

### DEC-005: Old Documentation Was Stale (Session 2)
- **Date:** 2026-06-07 (Session 2 re-verification)
- **Finding:** 5 out of 5 claims in old STATUS.md were incorrect.
  1. "app.js is MISSING" → app.js EXISTS (609 lines)
  2. "uvicorn NOT in requirements.txt" → uvicorn>=0.29.0 present
  3. "Tests directory empty" → 46 tests, all passing
  4. "Monte Carlo generates random data" → real `run_monte_carlo_samples()`
  5. "Pipeline does NOT use kinematics" → imports & calls kinematics
- **Lesson:** Always verify from source code, never trust prior summaries.

---

## Recent Decisions (Session 2)

### DEC-006: CRIT-005 Added as New Critical Finding
- **Date:** 2026-06-07 (Session 2)
- **Finding:** 5 JS module API mismatches identified from source analysis:
  1. `vizEngine.updateHUD()` → `updateHUDValues()`
  2. `animateFrame()` → `animate()`
  3. `collapseResults` as property not method
  4. `bayesianEVT.fitGPDProfileLikelihood()` → internal only
  5. `bayesianEVT.posteriorPredictiveCheck()` → internal only
- **Decision:** Add CRIT-005 to critical fix list (P1 priority)

---

*This decision log is updated continuously. Last verified: 2026-06-07.*
