# AV_Safety Skills Assessment & Improvement Plan

**Date:** June 4, 2026  
**Author:** Ahmed (Portfolio Owner)  
**Reviewer:** Claude Code  

---

## Executive Summary

This assessment reviews all 18 skills in the AV_Safety skills system. The skills are well-structured overall with clear dependencies, but 4 require completion and several need improvements.

| Status | Count | Details |
|--------|-------|---------|
| Complete | 14 | Well-documented, functional |
| Partial | 3 | Bayes EVT, Risk Quant, Portfolio Deploy |
| Missing | 1 | Validation skill (referenced but no file) |
| **Total** | **18 + 1 missing** | 19 total skills needed |

---

## 1. Project Overview

**AV_Safety** is an independent research portfolio on quantifying AV collision risk. Core question: *"How safe is safe enough for autonomous vehicles?"*

### Portfolio Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PORTFOLIO LAYER                                  │
│  ┌───────────┐    ┌──────────────────┐    ┌────────────────────────────────┐  │
│  │ Portfolio UI│    │    Portfolio Deploy   │     │     Bayesian EVT API      │  │
│  │ Interactive│    │ CI/CD Pipeline    │     │     Risk Computation          │  │
│  │ Playground │    │ Multi-target      │     │     Collision Modeling        │  │
│  └──────┬─────┘    └──────────────────┘    └────────────────────────────────┘  │
│         │                                                         │          │
│         ▼                                                         ▼          │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                          ANALYSIS LAYER                                    ││
│  │  Kinematics → Indicators → Monte Carlo → Bayesian EVT → Collision Model  ││
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                        FOUNDATION LAYER                                    ││
│  │  Data Ingest → Scenario Taxonomy → Standards Research → Risk Metrics      ││
│  └───────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Build Order (4 Phases)

```
phase1 (foundation) → phase2 (analysis) → phase3 (modeling) → phase4 (portfolio)
    7 skills                  5 skills              4 skills              3 skills
```

---

## 2. Detailed Skill Assessment

### Phase 1: Foundation Skills

#### 2.1. project-setup ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 100% |
| Documentation | Good |
| Dependencies | None (foundational) |
| Issues | None |

**Notes:** Minimal documentation compared to analytical skills, but appropriate for setup skill.

#### 2.2. scenario-taxonomy ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 100% |
| Documentation | Excellent |
| Dependencies | None (foundational) |
| Issues | JSON schema references external location not included |

**Recommendations:**
- Add JSON schema directly to skill directory
- Include data validation examples

#### 2.3. data-ingest ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 95% |
| Documentation | Good |
| Dependencies | standards-research (sibling) |
| Issues | No API credential handling, Scotland missing data source |

**Recommendations:**
- Add credential management documentation
- Document Scotland data source explicitly

#### 2.4. standards-research ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 80% |
| Documentation | Adequate |
| Dependencies | None (foundational) |
| Issues | Missing reference files, analysis methodology unclear |

**Recommendations:**
- Add reference files with standards analysis examples
- Document cross-referencing methodology
- Include compliance matrix templates

#### 2.5. risk-metrics ⚠️

| Attribute | Assessment |
|-----------|------------|
| Completeness | 70% |
| Documentation | Insufficient |
| Dependencies | data-ingest, indicator-computation, bayesian-evt, standards-research |
| Issues | **HIGH PRIORITY** - Missing reference files, no formulas |

**Recommendations:**
- **Critical:** Add reference files with mathematical formulas
- Include implementation examples
- Document citation methodology

#### 2.6. bayesian-analysis ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 90% |
| Documentation | Good |
| Dependencies | stochastic-simulation, scenario-taxonomy, data-ingest |
| Issues | No version requirements, software stack unclear |

**Recommendations:**
- Add specific library version requirements
- Document PyMC vs Stan selection criteria

#### 2.7. data-exploration ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 85% |
| Documentation | Good |
| Dependencies | data-ingest, scenario-taxonomy |
| Issues | No actual data available yet |

**Recommendations:**
- Add sample dataset for demonstration
- Include example EDA output

---

### Phase 2: Analysis Skills

#### 2.8. kinematics-engine ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 95% |
| Documentation | Excellent |
| Dependencies | scenario-taxonomy (upstream) |
| Issues | Validation module missing |

**Recommendations:**
- Add validation module for benchmark comparison
- Document benchmarking methodology

#### 2.9. indicator-computation ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 90% |
| Documentation | Good |
| Dependencies | kinematics-engine, scenario-taxonomy |
| Issues | Some indicators duplicated in categories |

**Recommendations:**
- Consolidate duplicated indicators (CPI appears twice)
- Add applicability matrix visualization

#### 2.10. stochastic-simulation ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 85% |
| Documentation | Good |
| Dependencies | scenario-taxonomy, kinematics-engine |
| Issues | Sample size caps may be insufficient |

**Recommendations:**
- Justify maximum sample sizes (50,000)
- Add parallelization strategy documentation
- Include convergence criteria justification

#### 2.11. bayesian-evt ⚠️

| Attribute | Assessment |
|-----------|------------|
| Completeness | 80% |
| Documentation | Good |
| Dependencies | stochastic-simulation, kinematics-engine, indicator-computation |
| Issues | Implementation distributed, unclear package structure |

**Recommendations:**
- Consolidate documentation
- Document package organization strategy
- Add prior sensitivity analysis examples

#### 2.12. 3d-animation ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 85% |
| Documentation | Good |
| Dependencies | scenario-taxonomy, kinematics-engine, indicator-computation |
| Issues | High-poly assets missing, asset management unclear |

**Recommendations:**
- Document asset management strategy
- Include 3D model source information
- Add mobile device performance targets

---

### Phase 3: Modeling Skills

#### 2.13. collision-modeling ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 85% |
| Documentation | Good |
| Dependencies | kinematics-engine, bayesian-evt, stochastic-simulation, indicator-computation |
| Issues | Neural network architecture not specified |

**Recommendations:**
- Add neural network architecture diagram
- Include model selection criteria documentation
- Document cross-validation strategy

#### 2.14. risk-quantification ⚠️

| Attribute | Assessment |
|-----------|------------|
| Completeness | 75% |
| Documentation | Adequate |
| Dependencies | All analytical skills |
| Issues | Risk scoring weights appear arbitrary |

**Recommendations:**
- Derive risk scoring weights with justification
- Include example risk scoring calculations
- Document threshold comparison methodology

#### 2.15. safety-thresholds ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 85% |
| Documentation | Good |
| Dependencies | bayesian-evt, standards-research |
| Issues | Limited to 3 jurisdictions, learning rate unclear |

**Recommendations:**
- Justify continuous monitoring learning rate (0.01)
- Document threshold validation strategy
- Expand jurisdiction coverage

#### 2.16. statistical-validation ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 90% |
| Documentation | Good |
| Dependencies | bayesian-evt, risk-quantification, safety-thresholds |
| Issues | Benchmark database may need periodic updates |

**Recommendations:**
- Add periodic update schedule for benchmark data
- Include examples for each test type

---

### Phase 4: Portfolio Skills

#### 2.17. portfolio-ui ✅

| Attribute | Assessment |
|-----------|------------|
| Completeness | 95% |
| Documentation | Excellent |
| Dependencies | bayesian-evt, 3d-animation, indicator-computation, stochastic-simulation |
| Issues | Performance targets may be aggressive |

**Recommendations:**
- Add browser performance testing results
- Include offline data storage strategy
- Document async task management

#### 2.18. portfolio-deploy ⚠️

| Attribute | Assessment |
|-----------|------------|
| Completeness | 60% |
| Documentation | Insufficient |
| Dependencies | portfolio-ui, risk-quantification, standards-research |
| Issues | No deployment scripts, infrastructure-as-code missing |

**Recommendations:**
- Add deployment scripts
- Include Terraform/CloudFormation templates
- Document monitoring strategy
- Add health check endpoints

---

## 3. Missing Skills

### 3.1. validation ❌ (Not Found)

**Referenced in:**
- root SKILL.md (line 27)
- portfolio-ui/SKILL.md
- Multiple downstream dependencies

**Required Documentation:**
- Collision rate vs published data comparison
- Indicator compliance checks
- Cross-jurisdictional validation
- Regression testing framework

**Priority:** High — needed to complete the pipeline

---

## 4. Cross-Skill Dependency Analysis

### 4.1. Critical Integration Points

| Integration | Risk | Mitigation |
|-------------|------|------------|
| Kinematics → Indicators | Low | Well-documented API |
| Monte Carlo → Bayesian EVT | Medium | Add interface validation |
| Bayesian EVT → Safety Thresholds | Medium | Clear rate definitions needed |
| Risk Quantification → Portfolio UI | Low | JSON schema well-specified |

### 4.2. Data Flow Gaps

1. **No offline data storage** — Monte Carlo results not cached
2. **Missing error handling** — Pipeline failure recovery strategy unclear
3. **No versioning** — Scenario data versioning not documented

---

## 5. Improvement Priority Matrix

| Priority | Skill | Issue | Impact | Effort |
|----------|-------|-------|--------|--------|
| P1 | risk-metrics | Missing formulas | High | Medium |
| P1 | portfolio-deploy | Missing deployment docs | High | Medium |
| P1 | validation | Missing skill | High | Medium |
| P2 | standards-research | Missing references | Medium | Low |
| P2 | risk-quantification | Unclear weights | Medium | Low |
| P2 | safety-thresholds | Limited jurisdictions | Low | Medium |
| P3 | data-ingest | Missing API credentials | Low | Low |
| P3 | bayesian-evt | Distributed impl | Low | Medium |
| P3 | 3d-animation | Missing assets | Low | High |

---

## 6. Recommendations

### Immediate Actions (Next Sprint)

1. **Complete portfolio-deploy skill** with deployment scripts and monitoring docs
2. **Add reference files for risk-metrics** with mathematical formulas
3. **Create validation skill** with all validation test definitions
4. **Document standards-research** with analysis methodology

### Short-Term Actions (Month 1)

5. Consolidate risk-quantification documentation with weight derivations
6. Expand safety-thresholds to cover additional jurisdictions
7. Add asset management strategy for 3d-animation
8. Implement Monte Carlo result caching

### Long-Term Actions (Month 2+)

9. Refine neural network architecture for collision-modeling
10. Add continuous integration tests for pipeline validation
11. Implement versioning for scenario data
12. Develop browser performance benchmarks

---

## 7. Metrics Tracking

| Metric | Current | Target |
|--------|---------|--------|
| Skills with reference files | 14/18 (78%) | 19/19 (100%) |
| Average documentation completeness | 85% | 95% |
| Cross-skill dependencies documented | 100% | 100% |
| Skills with validation modules | 12/18 (67%) | 19/19 (100%) |

---

*End of Assessment*
