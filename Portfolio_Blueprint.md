# AV_Safety Portfolio Blueprint

**Version:** 1.0  
**Date:** June 4, 2026  
**Author:** Ahmed (Portfolio Owner)  
**Reviewer:** Claude Code  
**Repository:** https://github.com/Akamel01/AV_Safety.git  

---

## Executive Summary

This blueprint defines the complete production-level architecture and implementation plan for the AV_Safety portfolio — an interactive web-based "collision risk playground" that quantifies autonomous vehicle collision risk using Bayesian extreme value theory and 3D simulation.

**Production Target:** An evidence-based, standards-compliant, continuously validated risk quantification tool that enables regulatory bodies and safety engineers to make deployment decisions.

---

## 1. Product Vision

### 1.1 Mission Statement

> "How safe is safe enough for autonomous vehicles?"

Provide quantitative, defensible safety thresholds for AV deployment through:
- Bayesian extreme value theory for tail-risk estimation
- Monte Carlo simulation for parameter uncertainty propagation
- International standards alignment (UL 4600, ISO 21448, ISO 26262)

### 1.2 Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Regulators** | Evidence-based deployment thresholds with quantified uncertainty |
| **AV Developers** | Self-service risk assessment tool for design validation |
| **Researchers** | Reproducible analysis framework with open methodology |
| **Policy Makers** | Cross-jurisdictional comparison of safety standards |

### 1.3 Success Criteria

1. **Statistical rigor:** R-hat < 1.01, ESS > 400 per parameter across all scenarios
2. **Coverage:** 20+ scenarios across 8 conflict types, 3+ jurisdictions
3. **Performance:** Monte Carlo results in <30s for 10,000 samples
4. **Compliance:** Meets UL 4600 and ISO 21448 threshold requirements
5. **Reproducibility:** All analysis produces verifiable, repeatable results

---

## 2. Target Users

### 2.1 Primary Personas

| Persona | Role | Needs |
|---------|------|-------|
| **Dr. Sarah Chen** | NHTSA Safety Analyst | Threshold compliance, standards alignment |
| **Alex Rivera** | AV Safety Engineer | Real-time parameter exploration, risk scoring |
| **Prof. James Okafor** | Academic Researcher | Methodology validation, data access |
| **Policy Committee** | UK Parliament | Cross-jurisdiction comparison |

### 2.2 Technical Profile

- **Highly technical** — understand Bayesian statistics, kinematics, and safety standards
- **Safety-critical** — require defensible, auditable results
- **Policy-aware** — need regulatory context and citations
- **Expect rigorous evidence** — no assumptions, only data-backed conclusions

---

## 3. Core Capabilities

### 3.1 Collision Risk Quantification

| Capability | Description | Priority |
|------------|-------------|----------|
| **GPD Fitting** | Bayesian hierarchical GPD for exceedances | P1 |
| **MRL Threshold Selection** | Mean Residual Life plot + Coles stability | P1 |
| **Posterior Prediction** | Full posterior distribution for P(collision) | P1 |
| **Severity Estimation** | GPD-based severity with ΔV correlation | P1 |

### 3.2 Monte Carlo Simulation

| Capability | Description | Priority |
|------------|-------------|----------|
| **Parameter Sampling** | Normal distributions from NHTSA/UK/CA data | P1 |
| **10,000+ Sample Runs** | Parallelizable via Web Workers | P2 |
| **Result Caching** | Offline storage for reproducibility | P2 |
| **Sensitivity Analysis** | Pearson correlation per parameter | P3 |

### 3.3 Safety Indicators

| Capability | Description | Priority |
|------------|-------------|----------|
| **42 Indicators** | Time, distance, decel, kinematic, severity, probability | P1 |
| **TTC/DRAC Tracking** | Per-timestep temporal metrics | P1 |
| **RLA Computation** | Required deceleration to avoid collision | P1 |
| **CPI Estimation** | Collision probability index | P2 |

### 3.4 Standards Compliance

| Capability | Description | Priority |
|------------|-------------|----------|
| **UL 4600 Compliance** | Individual and societal risk thresholds | P1 |
| **ISO 21448 (SOTIF)** | Performance degradation tolerance | P1 |
| **ISO 26262** | Functional safety assessment | P2 |
| **NHTSA Alignment** | FARS/CISS threshold comparison | P1 |

### 3.5 Visualization

| Capability | Description | Priority |
|------------|-------------|----------|
| **3D Animation** | Three.js with high-poly GLTF models | P1 |
| **2D Canvas Fallback** | Canvas 2D for mobile/offline | P1 |
| **Monte Carlo Results** | Interactive histograms, percentiles | P1 |
| **Risk Scoring** | Composite visualization with components | P1 |
| **GPD Posteriors** | Bayesian posterior visualization | P2 |

---

## 4. Architecture Overview

### 4.1 System Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  EXTERNAL                                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│  │ NHTSA FARS │ │ Transport  │ │   UK DfT   │ │  CMFwiki   │ │   JACArP   │ │
│  │   USA      │ │   Canada   │ │  England   │ │   Canada   │ │   England  │ │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ │
│         ▼               ▼               ▼               ▼               ▼     │
└─────────────────────────────────────────────────────────────────────────────┘
                 │              │              │              │              │
                 ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 AV_SAFETY                                     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          PORTFOLIO LAYER                                 ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────────────┐ ││
│  │  │   Portfolio   │  │   Portfolio   │  │       Bayesian               │ ││
│  │  │     UI        │  │   Deploy      │  │       EVT API                 │ ││
│  │  │ Interactive   │  │ CI/CD Pipeline │  │     Risk Computation          │ ││
│  │  │ Playground    │  │ Multi-target    │  │     Collision Modeling       │ ││
│  │  └──────┬────────┘  └──────┬─────────┘  └───────────────┬──────────────┘ ││
│  │         │                      │                          │                ││
│  │         ▼                      ▼                          ▼                ││
│  │  ┌──────────────────────────────────────────────────────────────────────┐ ││
│  │  │                          ANALYSIS LAYER                               │ ││
│  │  │  Kinematics → Indicators → Monte Carlo → Bayesian EVT → Collision   │ ││
│  │  └──────────────────────────────────────────────────────────────────────┘ ││
│  │  ┌──────────────────────────────────────────────────────────────────────┐ ││
│  │  │                          FOUNDATION LAYER                             │ ││
│  │  │  Data Ingest → Scenario Taxonomy → Standards Research → Risk Metrics│ ││
│  │  └──────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Visualization** | Three.js + Canvas 2D | Industry standard for 3D, fallback support |
| **Computation** | Pyodide (Python in browser) | Seamless integration with PyMC, in-browser computation |
| **Bayesian Inference** | PyMC (Stan backend) | Hierarchical modeling, well-documented |
| **Data Processing** | Pandas, NumPy, SciPy | Standard Python data science stack |
| **Storage** | IndexedDB (browser) + file system | Offline capability, simple persistence |
| **Deployment** | Docker + cloud provider | Reproducible builds, multi-environment |

---

## 5. Data Flow Architecture

### 5.1 Raw Data → Model → Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA INGESTION                                   │
│                                                                              │
│  External Data (FARS/CISS, Canada, England)                                  │
│          │                                                                    │
│          ▼                                                                    │
│  Data Processing Pipeline:                                                    │
│  ├─► Validation & Cleaning                                                    │
│  ├─► Schema Alignment                                                         │
│  └─► Versioning                                                               │
│          │                                                                    │
│          ▼                                                                    │
│  Processed Data Store:                                                        │
│  ├─► Collision databases (crash, injury, fatality)                           │
│  ├─► Vehicle characteristics (weight, dimensions)                            │
│  └─► Environmental factors (weather, road type)                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODELING LAYER                                     │
│                                                                              │
│  Kinematics Engine:                                                          │
│  ├─► Vehicle trajectory computation                                          │
│  ├─► 8 conflict type implementations                                         │
│  └─► Time-stepping simulation                                                │
│          │                                                                    │
│          ▼                                                                    │
│  Indicator Computation:                                                       │
│  ├─► 42 surrogate safety indicators                                          │
│  ├─► Per-timestep metrics (TTC, DRAC, RLA)                                   │
│  └─► Aggregated statistics                                                    │
│          │                                                                    │
│          ▼                                                                    │
│  Monte Carlo Simulation:                                                      │
│  ├─► Parameter sampling from NHTSA distributions                           │
│  ├─► 10,000+ independent simulations                                          │
│  └─► Aggregated results (distributions, percentiles)                         │
│          │                                                                    │
│          ▼                                                                    │
│  Bayesian Extreme Value Theory:                                               │
│  ├─► MRL threshold selection                                                 │
│  ├─► GPD parameter fitting (PyMC)                                             │
│  ├─► Posterior distribution                                                    │
│  └─► Posterior predictive checks                                               │
│          │                                                                    │
│          ▼                                                                    │
│  Collision Risk Quantification:                                               │
│  ├─► P(collision) estimation                                                  │
│  ├─► Severity estimation                                                      │
│  ├─► Risk scoring (composite metrics)                                         │
│  └─► Uncertainty quantification                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VISUALIZATION LAYER                                 │
│                                                                              │
│  Portfolio UI:                                                                │
│  ├─► Scenario explorer (conflict type navigation)                           │
│  ├─► Parameter controls (speed, gap, reaction time)                         │
│  ├─► Real-time Monte Carlo simulation                                        │
│  ├─► Risk score visualization                                                  │
│  ├─► 3D animation + HUD                                                        │
│  └─► Jurisdiction comparison                                                   │
│                                                                              │
│  Generated Artifacts:                                                         │
│  ├─► Executive summary (markdown)                                            │
│  ├─► Raw data (JSON, CSV)                                                      │
│  └─► Reports (PDF, slides)                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Testing Strategy

### 6.1 Test Pyramid

```
                    ┌─────────────┐
                    │   Integration│
                    │   (20 tests)  │
                    └──────┬──────┘
                           │
                  ┌────────┴────────┐
                  │    Unit Tests    │
                  │   (200 tests)    │
                  └────────┬────────┘
                           │
             ┌─────────────┴─────────────┐
             │    Component Tests         │
             │    (50 tests per skill)    │
             └───────────────────────────┘
```

### 6.2 Test Coverage Targets

| Layer | Coverage Target | Test Types |
|-------|-----------------|------------|
| **Kinematics** | 95% | Unit (trajectory correctness), component (collision detection) |
| **Indicators** | 90% | Unit (each indicator), component (aggregation) |
| **Monte Carlo** | 85% | Unit (sampling), component (convergence) |
| **Bayesian EVT** | 90% | Unit (GPD), component (MCMC diagnostics) |
| **Risk Scoring** | 85% | Unit (weights), component (compliance) |
| **Portfolio UI** | 75% | Component (buttons, controls), integration |

### 6.3 Validation Strategy

1. **Against analytical cases** — closed-form solutions for simple scenarios
2. **Against published data** — NHTSA FARS fatality rates, Transport Canada rates
3. **Cross-jurisdictional consistency** — same scenario, different jurisdictions
4. **Convergence checks** — increasing sample size shows stabilization
5. **Prior sensitivity** — multiple priors yield similar posteriors

---

## 7. Deployment Strategy

### 7.1 Target Environments

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| **Development** | Active development | Local docker container |
| **Staging** | Pre-production validation | AWS EC2 + RDS |
| **Production** | Public access | AWS ECS + CloudFront |
| **Research** | Off-site analysis | Institutional VM |

### 7.2 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 PRODUCTION                                    │
│                                                                              │
│                        ┌─────────────────────────────────┐                   │
│                        │            CloudFront CDN        │                   │
│                        │     Static assets: CSS, JS, 3D  │                   │
│                        └──────────────────┬──────────────┘                   │
│                                           │                                   │
│  ┌───────────────────────────────────────┼──────────────────────────────────┐│
│  │                                       ▼                                   ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │                    ECS Cluster (5 tasks)                              │││
│  │  │                                                                       │││
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────┐ ││
│  │  │  │   API Task   │  │   Workers   │  │        Pre-computed          │ ││
│  │  │  │ (FastAPI)    │  │ (Monte Carlo │  │         Grid Storage          │ ││
│  │  │  │ - Token auth  │  │   10k+ runs)  │  │     (S3 + DynamoDB)         │ ││
│  │  │  │ - Auth        │  │               │  │     for featured scenarios) │ ││
│  │  │  │ - Rate limit  │  │               │  └─────────────────────────────┘ ││
│  │  │  │ - Telemetry   │  │               │                                 ││
│  │  │  └──────┬────────┘  └──────────────┘  ┌───────────────────────────────┐ ││
│  │  │         │                              │      Bayesian EVT Gateway     │ ││
│  │  │         ▼                              │ (PyMC model serving)           │ ││
│  │  │  ┌─────────────────────────────────────┴───────────────────────────────┘ ││
│  │  │  │           Data Lake: S3 + Parquet + Iceberg                             │ ││
│  │  │  │   - Raw collision data                                                   │ ││
│  │  │  │   - Processed datasets                                                   │ ││
│  │  │  │   - Scenario version history                                             │ ││
│  │  │  └────────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                              │                                                   │
│                              ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                           Observability                                      ││
│  │  CloudWatch (logs)  │  X-Ray (traces)  │  GuardDuty (security)             ││
│  │  Lambda (alarming)  │  Synthetics (health)  │  WAF (request filtering)      ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 CI/CD Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   GitHub    │───►│   Trigger   │───►│    Build   │───►│    Deploy   │
│  (events)   │    │ (workflow)  │    │   stage    │    │   stage     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                        │                    │                    │
                        ▼                    ▼                    ▼
                  ┌────────────┐    ┌────────────┐    ┌────────────┐
                  │  PR Check  │    │  Tests     │    │  Staging   │
                  │            │    │            │    │  validation│
                  │  - lint    │    │  - unit    │    │            │
                  │  - type    │    │  - integ   │    │  - manual  │
                  │  - fmt     │    │  - perf    │    │  review    │
                  │  - doc     │    │            │    │            │
                  └────────────┘    └────────────┘    └────────────┘
                                                             │
                                                             ▼
                                                          ┌────────────┐
                                                          │  Production│
                                                          │            │
                                                          │  - canary  │
                                                          │  - fully   │
                                                          │  - rollback│
                                                          └────────────┘
```

---

## 8. Security & Privacy

### 8.1 Data Handling

| Aspect | Treatment | Justification |
|--------|-----------|---------------|
| **Raw crash data** | Public domain (NHTSA, etc.) | No PII, no privacy concerns |
| **Model outputs** | Public | Analytical, aggregated |
| **User data** | None stored | Client-side computation only |
| **Telemetry** | Minimal | Session stats only |

### 8.2 Access Control

- **Public read access** — all portfolio content
- **Research access** — authenticated for raw data/API
- **Admin access** — repository owners only

### 8.3 Compliance

- **GDPR** — No personal data collected
- **Data sovereignty** — data from jurisdiction-appropriate sources
- **Auditability** — all computations reproducible

---

## 9. Observability Strategy

### 9.1 Monitoring Targets

| Metric | Alert Condition | Response |
|--------|-----------------|----------|
| **Bayesian convergence** | R-hat > 1.01 | Flag scenario, halt updates |
| **Monte Carlo error** | Rate CI width > 20% | Increase samples |
| **P(collision) drift** | >50% from baseline | Review with lead researcher |
| **Server latency** | >200ms p95 | Scale cluster |
| **Error rate** | >1% of requests | Investigate root cause |

### 9.2 Telemetry

- **Application metrics** — requests, latencies, errors
- **Business metrics** — scenarios explored, simulations run
- **Statistical metrics** — convergence diagnostics, prior sensitivity

---

## 10. Maintenance Strategy

### 10.1 Cadence

| Task | Frequency | Owner |
|------|-----------|-------|
| **Data refresh** | Monthly | Research team |
| **Model retraining** | Quarterly | Lead researcher |
| **Standards review** | Bi-annually | Compliance team |
| **Benchmark update** | Annual | Technical team |
| **Full validation** | Annual | QA team |

### 10.2 Versioning

```
Scenario data:   vYYYY.MM
Model versions:  vX.Y.Z
Skill versions:  vX.Y.Z (semantic)
Portfolio releases:  vX.Y.Z
```

---

## 11. Rollout Strategy

### 11.1 Phase Plan

| Phase | Scope | Criteria |
|-------|-------|----------|
| **Alpha** | Single scenario (RE-CA-001) | Demo works, tests pass, GPD converges |
| **Beta** | 2 featured scenarios per type (16) | All 8 conflict types, 3 jurisdictions |
| **RC** | 50+ scenarios, full dataset | External data loaded, full validation |
| **Production** | 62+ scenarios, regulatory search | 20+ scenarios available, CI/CD active |

### 11.2 Success Gates

1. **Alpha gate:** Demo works locally, tests pass, GPD convergence diagnostics pass
2. **Beta gate:** All 8 conflict types have 2+ scenarios each, cross-jurisdictional validation
3. **RC gate:** External data loaded, analysis reproducible, performance targets met
4. **Production gate:** CI/CD active, monitoring configured, regression tests pass

---

## 12. Risk Mitigation

### 12.1 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Statistical errors** | Medium | High | Multiple reviewers, diagnostic checks |
| **Data access restricted** | Medium | Medium | Public data only, document restrictions |
| **Performance bottleneck** | Low | Low | Pre-computed grids, browser Web Workers |
| **Regulatory changes** | Medium | Medium | Quarterly standards review |
| **Scope creep** | Medium | High | Strict 4-phase build order |
| **Dependency failures** | Low | Low | Lock dependencies, quarterly audits |

### 12.2 Rollback Plan

1. **Immediate:** Revert to previous tagged commit
2. **Short-term:** Restore from last passing CI build
3. **Long-term:** Full data/mode/source restoration from version history

---

## 13. Summary of Remaining Work

| Category | Estimated Effort | Dependencies |
|----------|------------------|--------------|
| Complete validation skill | 1 sprint | None |
| Complete 4 pending skills | 2 sprints | Validation skill |
| Implement data ingestion | 2 sprints | Skills complete |
| Add 3 more demo scenarios | 2 sprints | Data available |
| Implement unit tests | 2 sprints | Skills complete |
| Implement CI/CD | 1 sprint | Tests implemented |
| Implement full portfolio UI | 4 sprints | 20+ scenarios |
| Production deployment | 2 sprints | All above |
| **Total** | **~18 sprints** | **Sequential dependency** |

---

*Last updated: June 4, 2026*
*Next review: After validation skill completed*
*Handoff task: Complete portfolio-deploy skill with deployment scripts and monitoring*
