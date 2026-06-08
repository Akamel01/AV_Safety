# Deployment Readiness — AV_Safety

**Created:** 2026-06-07  
**Last Updated:** 2026-06-07

---

## Layer Readiness Matrix (13 Enterprise Layers)

| # | Layer | Status | Confidence | Notes |
|---|-------|--------|------------|-------|
| 1 | Interaction & Control Plane | 🟡 Partial | 70% | Demo works in browser; no API server deployed |
| 2 | Core Application & Hosting Infrastructure | 🟡 Partial | 60% | Dockerfile exists but no docker-compose.yaml at root; CI scripts in deploy/ci/ but no GitHub Actions |
| 3 | Data Ingestion & Semantic Data Foundation | 🔴 Not Ready | 20% | No external data ingested; all synthetic parameters |
| 4 | Business Context & Semantic Modeling | 🟡 Partial | 50% | Risk taxonomy exists in skills; no data linkage |
| 5 | Memory & State Management | 🔴 Not Ready | 15% | No persistence; results lost between runs |
| 6 | Tools & Integration Layer | 🟡 Partial | 60% | 23 skills documented but no driver.py scripts |
| 7 | Execution & Workflow Orchestration | 🟢 Ready | 85% | Pipeline orchestrates 7 steps; 46 tests pass |
| 8 | Model Gateway & Semantic Caching | 🔴 Not Ready | 10% | No caching; no model serving infrastructure |
| 9 | Safety & Guardrails | 🟡 Partial | 40% | Scenario constraints exist but no input validation |
| 10 | Prompt & Interaction Design | 🟢 Ready | 75% | Demo has UI controls; parameter sliders work |
| 11 | Evaluation & Telemetry | 🔴 Not Ready | 15% | No monitoring; no test coverage for risk_scoring/threshold_checker modules |
| 12 | Experimentation & Continuous Improvement | 🟡 Partial | 40% | Validation framework exists; no automated benchmarking |
| 13 | Security, Compliance & Governance | 🔴 Not Ready | 20% | No CSP headers; no security review; no compliance evidence |

---

## Prerequisites for Safe Deployment

### Must-Have (P0)

| # | Item | Status | Details |
|---|------|--------|---------|
| P0-01 | README.md | ❌ Missing | Project entry documentation required |
| P0-02 | Dependency cleanup | ❌ Missing | Remove pymc/pystan from requirements.txt (unused in pipeline) |
| P0-03 | Error handling | 🟡 Partial | Animation loop has no try/catch; visualization crashes kill demo |
| P0-04 | GitHub Actions CI/CD | ❌ Missing | No `.github/workflows/` directory |
| P0-05 | Input validation | ❌ Missing | Pipeline accepts arbitrary scenario dict |

### Should-Have (P1)

| # | Item | Status | Details |
|---|------|--------|---------|
| P1-01 | Risk scoring weight derivation | ❌ Missing | 0.3/0.3/0.2/0.2 arbitrary — needs justification |
| P1-02 | Full Bayesian inference on server | ❌ Missing | Pipeline uses heuristic GPD MoM |
| P1-03 | External data pipeline | ❌ Missing | Validation against real crash data required |
| P1-04 | Portfolio UI | ❌ Missing | Multi-scenario comparison not implemented |
| P1-05 | Security headers | ❌ Missing | No CSP, no input sanitization |

### Nice-to-Have (P2)

| # | Item | Status | Details |
|---|------|--------|---------|
| P2-01 | Docker Compose at root | 🟡 Partial | `deploy/docker-compose.yml` exists but not at root |
| P2-02 | Docker compose up with API server | ❌ Missing | No compose file runs uvicorn by default |
| P2-03 | Monitoring/logging system | ❌ Missing | No observability beyond console.log |
| P2-04 | Accessibility audit | ❌ Missing | No ARIA labels, keyboard navigation |
| P2-05 | Type hints on all Python APIs | ❌ Missing | Only pipeline.py has type hints |

---

## Known Deployment Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R-001 | Pyodide load failure on slow networks | Medium | Demo never initializes | Lazy-load Pyodide; show loading spinner |
| R-002 | Three.js WebGL not available (no GPU device) | High | 3D visualization fails | 2D Canvas fallback exists (tested) |
| R-003 | Large MC runs (10k+) freeze UI on mobile | High | Poor UX on phones | Already using async with progress callback |
| R-004 | Safari iOS Pyodide support incomplete | Medium | Demo broken on iPhone | Safari compatibility testing needed |
| R-005 | No rollback procedure | High | Bad deployment takes forever | Docker multi-stage allows quick redeploy |

---

## Deployment Checklist

### Pre-Deployment
- [ ] Create README.md with architecture overview
- [ ] Remove unused dependencies from requirements.txt
- [ ] Add error handling to visualization animation loop
- [ ] Create `.github/workflows/ci.yml` for automated testing
- [ ] Add input validation to pipeline `__init__()`
- [ ] Run full test suite: `python3 -m pytest tests/ -v`
- [ ] Verify demo works in Chrome, Firefox, Safari

### Deployment
- [ ] Build Docker image: `docker build -t av-safety:latest .`
- [ ] Run container: `docker run -p 8000:8000 av-safety:latest`
- [ ] Verify demo loads: open `http://localhost:8000`
- [ ] Run MC simulation (10k samples) — verify completion
- [ ] Verify EVT triggers correctly when collisions >= 10

### Post-Deployment
- [ ] Monitor console for JS errors (DevTools)
- [ ] Load test: 10k MC runs in succession
- [ ] Verify memory leaks (Chrome Task Manager)
- [ ] Document deployment procedure

---

## Final Readiness Score

| Category | Score (0-100) |
|----------|--------------|
| Code Quality | 75 (46 tests pass, some gaps in coverage) |
| Documentation | 30 (no README.md) |
| Testing | 60 (pipeline tests only; no risk_scoring/threshold_checker tests) |
| Security | 20 (no CSP, no input validation) |
| Deployment | 40 (Dockerfile exists; no CI/CD) |
| Observability | 15 (no monitoring) |
| **Overall** | **46** |

*Status: NOT READY FOR PRODUCTION — requires addressing all P0 items.*

---

*This document is updated as deployment readiness changes.*
