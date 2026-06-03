# AV_Safety — Session Handoff

**Date:** 2026-06-02 20:12 PDT
**Current State:** Skills 10/18 built, ready for portfolio UI
**Next Task:** Build `portfolio-ui` skill

---

## Project Overview

**Goal:** Interactive web-based "collision risk playground" quantifying AV collision risk using Bayesian EVT + 3D animations

**Jurisdictions:** USA, Canada, England (use DfT GB, JACArP for England)

**Standards:** UL 4600, ISO 21448 (SOTIF), ISO 26262, ISO 21002, NHTSA publications

**Core Tech:**
- Three.js 3D + Canvas 2D fallback
- Pyodide in-browser computation
- PyMC for Bayesian EVT
- Surrogate safety indicators (42 total)
- 8 conflict types × 62+ scenarios

---

## Current Progress

### ✅ Built (10/18)
1. `project-setup` — Repo, git identity, workflow rules
2. `standards-research` — UL 4600, ISO, NHTSA data access
3. `risk-metrics` — Collision risk quantification
4. `scenario-taxonomy` — 8 conflict types × 62 scenarios
5. `kinematics-engine` — Trajectory computation per conflict
6. `indicator-computation` — 42 surrogate safety indicators
7. `stochastic-simulation` — Monte Carlo framework
8. `bayesian-evt` — EVT + hierarchical Bayesian (PyMC)
9. `3d-animation` — Three.js + Canvas 2D, collision FX, HUD
10. `bayesian-analysis` — General Bayesian workflows

### 🔄 Next (5/18)
1. **`portfolio-ui`** (DEPENDENCIES: bayesian-evt ✅, 3d-animation ✅)
2. `portfolio-deploy`
3. `validation`
4. `data-ingest` + `data-exploration`
5. `statistical-validation`, `collision-modeling`, `safety-thresholds`, `risk-quantification`

---

## Key Decisions

- **EVT threshold:** Mean Residual Life (MRL) plot with Coles (2001) stability analysis
- **Animation:** Three.js for 3D, Canvas 2D toggle, collision FX + HUD
- **Computation:** Hybrid — pre-computed 2-param grids for 16 featured scenarios, Pyodide for dynamic
- **Scenario coverage:** 2 featured per conflict type (16 total) + "View All" for 62+

---

## Critical Paths

### Must-Have for MVP
1. `portfolio-ui` skill → Portfolio landing page
2. `portfolio-deploy` skill → Docker + deployment

### Validation (Phase 2)
3. `data-ingest` + `data-exploration` → Load NHTSA/Transport Canada/DfT datasets
4. `statistical-validation` → Compare EVT outputs to real crash data
5. `risk-quantification` → Risk thresholds per jurisdiction

---

## Workflow Discipline (MUST FOLLOW)

- Max 2 file ops/turn
- Max 1 git cmd/turn (add + commit together)
- Response ≤ 15 lines
- One goal per turn
- Error recovery: stop → assess → adapt → retry once max
- Git: one commit per logical unit, never push without permission
- Skill tree first: check existing skills before building new ones
- Evidence-first: no assumptions, cite sources
- AV_Safety: only publicly available data (NHTSA FARS/CISS, Transport Canada, DfT GB, CMFwiki, JACArP)

---

## Technical Setup

**Project Location:** `/Users/akamel/projects/AV_Safety`
**Workspace:** `/Users/akamel/.openclaw/workspace`
**Git Remote:** `upstream` → `https://github.com/Akamel01/AV_Safety.git`

**Session Recovery:**
- Previous session failed 14× due to context bloat, massive batching, no error recovery
- All failures documented in `session-failures-analysis.md` and `fixing_operational_issues_plan.md`
- Workflow discipline rules now enforced in `AGENTS.md` and `SOUL.md`

---

## Session-Specific Notes

- Ahmed is a researcher/engineer specializing in Road Safety, Bayesian Analysis, RAG, Applied AI
- Evidence-first rigor at every step
- Portfolio audience: technical, safety-critical, regulatory stakeholders
- 3D quality: high-fidelity (high-poly GLTF, PBR materials, post-processing)

---

**Ready to proceed with `portfolio-ui` skill.**