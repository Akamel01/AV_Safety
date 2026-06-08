# Portfolio Blueprint — AV_Safety

**Last Updated:** 2026-06-07  
**Target State:** Production-grade collision risk analysis system

---

## Architecture Target

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AV_Safety Architecture                           │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 1: Interaction & Control Plane                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Single-Scenario Demo (Browser-based)                         │  │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐  │  │
│  │  │Kinematics │ │Monte Carlo│ │ Bayesian  │ │Visualization │  │  │
│  │  │  Engine   │ │  Engine   │ │   EVT     │ │  Engine      │  │  │
│  │  └───────────┘ └───────────┘ └───────────┘ └──────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 2: Core Application & Hosting                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (optional)                                     │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │  RiskQuantificationPipeline (7-step orchestrator)        │  │  │
│  │  │  ┌──────┐ ┌────────┐ ┌─────────┐ ┌──────────┐         │  │  │
│  │  │  │Kine. │→│Indic.  │→│MC       │→│Bayesian  │         │  │  │
│  │  │  └──────┘ └────────┘ └─────────┘ └──────────┘         │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 3: Data Ingestion & Semantic Foundation                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Scenario Definition (.json)                                  │  │
│  │  Risk Scoring Weights (configurable)                          │  │
│  │  Jurisdiction Thresholds (USA/CAN/GB)                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 4: Business Context & Semantic Modeling                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Risk Classification (5 levels: LOW/MODERATE/IMPORTANT/HIGH/CRITICAL) │  │
│  │  FC-Level Taxonomy (functional collision risk categories)       │  │
│  │  Compliance Level (COMPLIANT/PARTIAL/NON-COMPLIANT/UNKNOWN)     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 5: Memory & State Management                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  AppState (browser) — scenario, kinematics, mcResults, gpdParams  │  │
│  │  PipelineLog — step tracking, timing, warnings                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 6: Tools & Integration Layer                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  23 Skills (Hermes workflow automation)                         │  │
│  │  CSV/JSON/Report Exporters                                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 7: Execution & Workflow Orchestration                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Pipeline.run() — sequential 7-step execution                  │  │
│  │  PipelineStep — per-step timing, status, records             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 8: Model Gateway & Semantic Caching                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Scenario cache (load by ID from data/)                        │  │
│  │  Pre-computed benchmarks (against literature)                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 9: Safety & Guardrails                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  TTC thresholds (2.0/2.5/1.5s)                                 │  │
│  │  DRAC thresholds (4.0/3.5/5.0 m/s²)                           │  │
│  │  Deployment criteria (≥2s TTC, ≤3.5m/s² DRAC)                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 10: Evaluation & Telemetry                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  42 Monte Carlo indicators per sample                          │  │
│  │  Collision rate + 95% CI                                       │  │
│  │  TTC distribution (median, P5)                                 │  │
│  │  Severity distribution (PDO/minor/moderate/fatal %)           │  │
│  │  KSTest for GPD fit validation                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 11: Experimentation & Continuous Improvement                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Scenario parameter customization                              │  │
│  │  Jurisdiction switching (usa/canada/gb)                        │  │
│  │  Monte Carlo sample count tuning                               │  │
│  │  Pre-computed benchmarks (from literature)                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  LAYER 12: Security, Compliance & Governance                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ISO 26262, ISO 21448, UL 4600, NHTSA compliance              │  │
│  │  Jurisdiction-specific thresholds                              │  │
│  │  Documentation of methodology assumptions                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Operational Model

### Development Workflow
1. Code → Tests → Commit → CI Pipeline → Deploy
2. Each pipeline run validates: lint, tests, coverage, Docker build
3. Branch protection on `main` + required CI pass

### Deployment Targets
- **Static hosting** (Nginx, S3, GitHub Pages) — single-scenario-demo
- **Server deployment** (FastAPI on Docker) — pipeline as API
- **Edge deployment** (containerized) — lightweight Python runtime

### Monitoring
- Console logging (current)
- PipelineStep timing (partial)
- Planned: structured logging, metrics endpoint, alerting

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Kinematics engine inaccuracy | Low | High | Validated against literature benchmarks |
| Monte Carlo sample size | Medium | Medium | User-configurable sample count |
| Bayesian EVT approximation | High | Medium | Documented as Method of Moments (not full) |
| Jurisdiction threshold drift | Medium | High | Configurable per-deployment |
| Browser compatibility (Three.js) | Medium | Low | 2D Canvas fallback |
| No external data source | Low | High | Data ingestion pipeline planned |

---

*This blueprint evolves as the project matures.*
