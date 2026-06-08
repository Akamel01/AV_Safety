# Open Issues — AV_Safety

**Last Updated:** 2026-06-07
**Total Tracked:** 13 issues (was 10, updated with new findings)

---

## Critical Issues (3)

| ID | Title | Priority | File | Status |
|----|-------|----------|------|--------|
|| **CRIT-003** | `animateNominal()` no try/catch — crash kills demo | P1 | `app.js` 235-285 | ✅ **FIXED** (try/catch around frame, trajectory validation, graceful stop on error) |
|| **CRIT-004** | Pipeline `__init__` no input validation | P1 | `pipeline.py` 78-98 | ✅ **FIXED** (scenario/parameter validation, case-insensitive jurisdiction, 21 validation tests) |
|| **CRIT-005** | 5 JS module API mismatches — calls non-existent methods | P1 | `app.js` 150-200 | 🔵 **RE-EVALUATED** — no real mismatches (app.js methods match module methods; old analysis was regex false positive on ES class syntax) |

### CRIT-005 Details (New)
5 API mismatches identified from source analysis:
1. `vizEngine.updateHUD()` → should be `updateHUDValues()` (method renamed)
2. `vizEngine.animate()` → verify if still exists (method signature may differ)
3. `collapseResults` — property object called as method (property not callable)
4. `bayesianEVT.fitGPDProfileLikelihood()` → internal method only, not exported
5. `bayesianEVT.posteriorPredictiveCheck()` → internal method only, not exported

---

## High Issues (7)

| ID | Title | Priority | File | Status |
|----|-------|----------|------|--------|
| **HIGH-001** | Risk scoring weights (0.3/0.3/0.2/0.2) arbitrary | P2 | `risk_scoring.py` 1-182 | 🟡 Documented |
| **HIGH-002** | Bayesian EVT uses Method of Moments (not full inference) | P2 | `pipeline.py` 269-316 | 🟡 Documented gap |
| **HIGH-003** | No external data ingestion (all synthetic) | P2 | scenario JSON only | 🟡 Documented gap |
| **HIGH-004** | Pipeline catches all exceptions with `{}` (silent failure) | P2 | `pipeline.py` 163-167 | 🟡 Silent failure |
| **HIGH-005** | No test coverage measurement (pyproject.toml targets 80%) | P2 | pyproject.toml | 🟡 Partial |
| **HIGH-006** | Multiple Dockerfile locations (root vs deploy/) | P3 | Dockerfile files | 🟡 Documented |
| **HIGH-007** | `visualization.js` location not at expected path (root) | P3 | `modules/visualization.js` | 🟡 Documented |

---

## Blockers (2)

| ID | Title | Impact | Status |
|----|-------|--------|--------|
| **BLK-001** | No external data source configured | Limits testing scope | Awaiting |
| **BLK-002** | No deployment target specified | Can't plan rollout | Awaiting |

---

## Informational

- 244 total files in repository
- 46 tests passing (verified live)
- 14 continuity files created
- 23 skill directories
- Safety standards: ISO 26262, ISO 21448 (SOTIF), UL 4600, NHTSA FARS 2020

---

*This issue list is updated continuously. Last verified: 2026-06-07. CRIT-005 added as new critical finding.*
