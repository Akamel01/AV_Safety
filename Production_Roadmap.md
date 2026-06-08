# Production Roadmap — AV_Safety

**Last Updated:** 2026-06-07  
**Target:** Production-ready collision risk analysis system

---

## Phase 0: Discovery ✅ (Complete)

**Objective:** Full code audit, inventory, and gap analysis.

**Completed:**
- Full repository audit (157 files)
- 3 Python packages verified (pipeline, kinematics, scoring)
- 5 JavaScript modules verified (app.js, kinematics, monte-carlo, bayesian-evt, visualization)
- 46 tests verified passing
- 23 skill directories inventoried
- Infrastructure documented (Dockerfile, requirements.txt, CI scripts)
- All continuity artifacts created/updated

**Validation:** All files verified against codebase (not just docs).

---

## Phase 1: Critical Fixes 🔄 (In Progress)

**Objective:** Fix critical bugs, create missing infrastructure, add validation.

**Items:**

| # | Task | Priority | Status | Dependencies |
|---|------|----------|--------|-------------|
| P1-01 | Create README.md | P0 | ✅ Done | — |
| P1-02 | Clean requirements.txt (remove unused) | P0 | ✅ Done | — |
| P1-03 | Add input validation to pipeline.__init__ | P1 | 🔴 Open | — |
| P1-04 | Fix visualizeNominal() error handling | P1 | 🔴 Open | — |
| P1-05 | Create .github/workflows/ci.yml | P0 | ✅ Done | — |
| P1-06 | Create/update continuity files | P0 | ✅ Done | — |

**Exit Criteria:** All P1 tasks completed, 46 tests still pass, no regressions.

---

## Phase 2: Architecture Hardening

**Objective:** Strengthen the system architecture — remove brittleness, add safeguards.

**Items:**

| # | Task | Priority | Status | Dependencies |
|---|------|----------|--------|-------------|
| P2-01 | Create data directory structure | P1 | 🔴 Not Started | — |
| P2-02 | Add external data ingestion module | P2 | 🔴 Not Started | P2-01 |
| P2-03 | Add structured logging (not just print) | P1 | 🔴 Not Started | — |
| P2-04 | Create API documentation (OpenAPI/Swagger) | P2 | 🔴 Not Started | — |
| P2-05 | Add configuration management | P1 | 🔴 Not Started | — |
| P2-06 | Create .env.example | P2 | 🔴 Not Started | P2-05 |

**Exit Criteria:** System accepts external data, has structured logging, configurable via .env.

---

## Phase 3: Testing & Integration

**Objective:** Comprehensive testing — unit, integration, E2E, failure handling.

**Items:**

| # | Task | Priority | Status | Dependencies |
|---|------|----------|--------|-------------|
| P3-01 | Add integration tests (full pipeline run) | P1 | 🔴 Not Started | — |
| P3-02 | Add E2E browser tests (Playwright) | P2 | 🔴 Not Started | — |
| P3-03 | Add failure handling tests (bad input, missing files) | P1 | 🔴 Not Started | — |
| P3-04 | Add performance tests (large MC sample counts) | P2 | 🔴 Not Started | — |
| P3-05 | Increase coverage to 80%+ | P1 | 🔴 Not Started | P3-01 |
| P3-06 | Add cross-browser compatibility testing | P2 | 🔴 Not Started | P3-02 |

**Exit Criteria:** 80%+ coverage, integration tests passing, failure scenarios documented.

---

## Phase 4: Deployment

**Objective:** Production-ready deployment pipeline.

**Items:**

| # | Task | Priority | Status | Dependencies |
|---|------|----------|--------|-------------|
| P4-01 | Configure container registry | P1 | 🔴 Not Started | — |
| P4-02 | Create staging deployment target | P1 | 🔴 Not Started | P4-01 |
| P4-03 | Add rollout/rollback procedures | P2 | 🔴 Not Started | P4-02 |
| P4-04 | Configure monitoring/alerting | P2 | 🔴 Not Started | — |
| P4-05 | Create deployment runbook | P2 | 🔴 Not Started | — |
| P4-06 | Security audit | P1 | 🔴 Not Started | — |

**Exit Criteria:** Staging environment operational, deployment runbook documented, security audit passed.

---

## Phase 5: Validation & Release

**Objective:** Final validation, documentation, and release.

**Items:**

| # | Task | Priority | Status | Dependencies |
|---|------|----------|--------|-------------|
| P5-01 | End-to-end validation with real data | P1 | 🔴 Not Started | P3-01 |
| P5-02 | Safety documentation review | P1 | 🔴 Not Started | — |
| P5-03 | Third-party security audit | P2 | 🔴 Not Started | — |
| P5-04 | Release notes & changelog | P2 | 🔴 Not Started | P5-03 |
| P5-05 | User documentation (end-user) | P2 | 🔴 Not Started | — |
| P5-06 | Mark as production-ready | P0 | 🔴 Not Started | P5-04 |

**Exit Criteria:** All tests pass, safety audit documented, users can run full pipeline end-to-end.

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kinematics engine accuracy | High | Literature-validated benchmarks |
| Bayesian EVT approximation | Medium | Documented as Method of Moments limitation |
| Browser compatibility | Low | 2D Canvas fallback |
| No external data source | High | Data ingestion pipeline in Phase 2 |
| Deployment complexity | Medium | Containerized deployment (single Docker image) |

---

## Timeline Estimate

| Phase | Estimated Time | Current Status |
|-------|---------------|----------------|
| Phase 0: Discovery | 1 session | ✅ Complete |
| Phase 1: Critical Fixes | 1-2 sessions | 🔄 ~50% complete |
| Phase 2: Architecture Hardening | 3-4 sessions | 🔴 Not started |
| Phase 3: Testing & Integration | 4-6 sessions | 🔴 Not started |
| Phase 4: Deployment | 2-3 sessions | 🔴 Not started |
| Phase 5: Validation & Release | 2-3 sessions | 🔴 Not started |

**Total Estimated:** 13-19 sessions (can be parallelized)

---

*This roadmap is updated continuously as work progresses.*
