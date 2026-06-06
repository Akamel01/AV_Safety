# Open Issues — AV_Safety

**Last Updated:** 2026-06-05 13:00 PDT

## Critical Issues
| # | Issue | Priority | Impact | Status |
|---|-------|----------|--------|--------|
| 1 | Missing "validation" skill | P0 | Pipeline incomplete | RESOLVED — skills/validation/ created |
| 2 | Python pipeline uses simulated data | P0 | Results not reproducible | RESOLVED — deploy skill with CI/CD created |
| 3 | Tests directory empty | P0 | No quality assurance | RESOLVED — 15 tests pass |
| 4 | Portfolio UI directory empty | P0 | No production UI | Open |

## High Priority
| # | Issue | Priority | Impact | Status |
|---|-------|----------|--------|--------|
| 5 | Pipeline _run_monte_carlo generates random data | P1 | Simulation results meaningless | Open |
| 6 | Risk scoring weights arbitrary (0.3/0.3/0.2/0.2) | P1 | Risk scores not justified | Open |
| 7 | No CI/CD pipeline | P1 | No automated quality checks | RESOLVED — deploy/ci/ scripts created |
| 8 | graphify-out empty directory misclassified as skill | P1 | Organization issue | RESOLVED — 46 files present |

## Medium Priority
| # | Issue | Priority | Impact | Status |
|---|-------|----------|--------|--------|
| 9 | 42 indicators not all computed consistently | P2 | Analysis incomplete | Open |
| 10 | No external data ingestion | P2 | Validation against real crash data impossible | Open |
| 11 | Pyodide PyMC installation may fail | P2 | Bayesian EVT may not work in browser | Open |
| 12 | Three.js CDN may block requests | P2 | 3D visualization may fail | Open |
| 13 | No error handling in Monte Carlo simulation | P2 | Silent failures possible | Open |

## Low Priority
| # | Issue | Priority | Impact | Status |
|---|-------|----------|--------|--------|
| 14 | No assets/ directories in skills | P3 | Limited reusability | Open |
| 15 | No agents/openai.yaml for skill UI metadata | P3 | Skills won't surface in Codex CLI | Open |
| 16 | Graphify skill exceeds 500 lines | P3 | Hard to maintain | Open |

---

*This issue list is updated as new issues are discovered.*
