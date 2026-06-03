# AV_Safety — Core Project Skill

14/18 skills built. 4 remaining.

## Skill Tree

| Capability | Status | Dependency |
|---|-|-|
| ✅ project-setup | — |
| ✅ standards-research | — |
| ✅ risk-metrics | — |
| ✅ bayesian-analysis | — |
| ✅ scenario-taxonomy | — |
| ✅ kinematics-engine | — |
| ✅ indicator-computation | kinematics-engine |
| ✅ stochastic-simulation | kinematics-engine |
| ✅ bayesian-evt | indicator + stochastic |
| ✅ 3d-animation | kinematics + stochastic |
| ✅ data-ingest | — |
| ✅ data-exploration | data-ingest |
| ✅ statistical-validation | bayesian-evt |
| ✅ collision-modeling | bayesian-evt |
| 🔲 safety-thresholds | collision-modeling |
| 🔲 risk-quantification | safety-thresholds |
| 🔲 portfolio-ui | bayesian-evt + 3d |
| 🔲 portfolio-deploy | portfolio-ui |
| 🔲 validation | collision-modeling + risk-quantification |

### Build Order
```
phase1 ──► phase2 ──► phase3 ──► phase4
foundation    analysis    modeling    portfolio
```
