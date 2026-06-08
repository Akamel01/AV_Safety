# Architecture Gaps — AV_Safety

**Last Updated:** 2026-06-07

---

## Confirmed Architecture Gaps (from evidence)

### Critical Gaps (Phase 1 Priority)

| ID | Gap | Impact | Risk | Status |
|----|-----|--------|------|--------|
| **AG-001** | `pipeline.__init__` has NO input validation | Silent failures from missing scenario keys | P1 | 🔴 Open (CRIT-004) |
| **AG-002** | `animateNominal()` has NO try/catch | Demo crashes on any visualization error | P1 | 🔴 Open (CRIT-003) |
| **AG-003** | 5 JS module API mismatches | Broken functionality in browser demo | P1 | 🔴 Open (CRIT-005) |

### High Gaps (Phase 2 Priority)

| ID | Gap | Impact | Risk | Status |
|----|-----|--------|------|--------|
| **AG-004** | No test coverage measurement (pyproject.toml targets 80% but unmeasured) | Cannot verify code quality | P2 | 🟡 Partial |
| **AG-005** | No integration tests (only unit tests exist) | Cannot verify end-to-end behavior | P2 | 🔴 Open |
| **AG-006** | Pipeline catches ALL exceptions and continues with `{}` (silent failure propagation) | Bug hiding, false confidence | P2 | 🟡 Documented (HIGH-004) |
| **AG-007** | No external data ingestion (all synthetic) | Cannot validate against real-world | P2 | 🔴 Open (HIGH-003) |
| **AG-008** | Bayesian EVT uses Method of Moments (full PyMC commented out) | Limited statistical rigor | P2 | 🟡 Documented (HIGH-002) |
| **AG-009** | Risk scoring weights (0.3/0.3/0.2/0.2) arbitrary | No empirical validation of weights | P2 | 🟡 Documented (HIGH-001) |

### Medium Gaps (Phase 3 Priority)

| ID | Gap | Impact | Risk | Status |
|----|-----|--------|------|--------|
| **AG-010** | No caching layer (Model Gateway & Semantic Caching at 60%) | Performance limit at scale | P3 | 🟡 Documented |
| **AG-011** | Multiple Dockerfile locations (root vs deploy/) | Confusion about canonical location | P3 | 🟡 Documented |
| **AG-012** | No deployment target / registry (Phase 6) | Cannot plan production rollout | P3 | 🟡 Documented |
| **AG-013** | No external data source (data tier at 40%) | Cannot validate risk models | P3 | 🔴 Open |

---

## Architecture Observations (Not Gaps, Just Notes)

1. **Pipeline is well-structured** — 7 clear steps, modular (risk_scoring, threshold_checker, results_aggregator)
2. **JS modules follow clean class-based architecture** — Each module exports one class (RearEndKinematics, MonteCarloEngine, BayesianEVT, RiskScorer, VisualizationEngine)
3. **Safety thresholds per jurisdiction** — 10 modules covering multiple jurisdictions (USA, EU, JP)
4. **Docker Compose well-designed** — 4 services (dev, API, UI, nginx)
5. **CI/CD includes coverage instrumentation** — `--cov` flag present (but not enforced)

---

## 13-Layer Architecture Status

| Layer | Status | Gap Level | Gap IDs |
|-------|--------|-----------|---------|
| 1. Interaction & Control | 85% | MEDIUM | — |
| 2. Core Application & Hosting | 90% | LOW | — |
| 3. Data Ingestion & Semantic Foundation | 40% | HIGH | AG-007, AG-013 |
| 4. Business Context & Semantic Modeling | 85% | MEDIUM | AG-009 |
| 5. Memory & State Management | 90% | LOW | — |
| 6. Tools & Integration Layer | 80% | MEDIUM | — |
| 7. Execution & Workflow Orchestration | 90% | LOW | AG-006 |
| 8. Model Gateway & Semantic Caching | 60% | HIGH | AG-010 |
| 9. Safety & Guardrails | 85% | MEDIUM | — |
| 10. Prompt & Interaction Design | 85% | LOW | — |
| 11. Evaluation & Telemetry | 65% | HIGH | AG-004, AG-005 |
| 12. Experimentation & CI/CD | 80% | MEDIUM | AG-011, AG-012 |
| 13. Security, Compliance & Governance | 75% | MEDIUM | — |

---

*This file is updated continuously. Last verified: 2026-06-07.*
