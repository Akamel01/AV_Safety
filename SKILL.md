# AV_Safety — Core Project Skill

This is the master skill for the **AV_Safety** project: building a robust, high-quality portfolio on quantifying collision risk and answering "How safe is safe enough for autonomous vehicles?"

## Project Structure

```
AV_Safety/
├── SKILL.md                  # This file
├── README.md                 # Project overview
├── docs/                     # Research notes, standards references, architecture
│   ├── standards/            # UL 4600, ISO, NHTSA, regulatory references
│   ├── research/             # Literature review summaries
│   └── architecture/         # System design docs
├── data/                     # Raw and processed datasets
│   ├── raw/                  # Ingested datasets (crash reports, NHTSA, etc.)
│   └── processed/            # Cleaned, analyzed, feature-engineered data
├── models/                   # Trained models, checkpoints
├── src/                      # Application code
│   ├── analysis/             # Statistical & risk analysis modules
│   ├── risk_models/          # Collision risk modeling
│   ├── standards/            # Standards compliance utilities
│   ├── data_pipeline/        # ETL / feature pipeline
│   └── evaluation/           # Model evaluation & safety metrics
├── ui/                       # Portfolio visualizations, dashboards
├── tests/                    # Unit, integration, and validation tests
├── scripts/                  # Reproducible analysis scripts
├── config/                   # Configuration files
├── notebooks/                # Jupyter notebooks for exploratory work
├── docker-compose.yml        # Local dev environment
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variable template
```

## Core Research Questions

1. **How safe is safe enough for autonomous vehicles?** — Define quantitative safety thresholds
2. **What metrics and standards define acceptable AV collision risk?** — Cross-reference UL 4600, ISO 21448 (SOTIF), ISO 26262, NHTSA guidance
3. **How do we model and quantify collision risk across USA, Canada, and England contexts?**

## Working Principles (evidence-first)

- **No assumptions.** Every claim must be backed by data, standards text, or code output.
- **Verifiable.** Every analysis script must produce reproducible results.
- **Rigorous.** Statistical methods must be documented and justified.
- **Traceable.** All data sources, transformations, and model decisions are versioned and logged.

## Skill Tree (reusable capabilities)

| Capability | Status | Dependency |
|---|-|-|
| project-setup | ✅ Built | — |
| standards-research | ✅ Built | — |
| risk-metrics | ✅ Built | — |
| bayesian-analysis | ✅ Built | — |
| scenario-taxonomy | ✅ Built | — |
| kinematics-engine | ✅ Built | — |
| indicator-computation | ✅ Built | kinematics-engine |
| stochastic-simulation | ✅ Built | kinematics-engine |
| bayesian-evt | ✅ Built | indicator + stochastic |
| 3d-animation | ✅ Built | kinematics + stochastic |
| data-ingest | 🔲 Pending | — |
| data-exploration | 🔲 Pending | data-ingest |
| statistical-validation | 🔲 Pending | bayesian-evt |
| collision-modeling | 🔲 Pending | bayesian-evt |
| safety-thresholds | 🔲 Pending | collision-modeling |
| risk-quantification | 🔲 Pending | safety-thresholds |
| portfolio-ui | 🔲 Pending | bayesian-evt + 3d |
| portfolio-deploy | 🔲 Pending | portfolio-ui |
| validation | 🔲 Pending | all above |

10/18 skills built. 8 remaining.

### Build Order

```
phase1 ──► phase2 ──► phase3 ──► phase4
foundation    analysis    modeling    portfolio
```

- **Phase 1 → Phase 2:** scenario-taxonomy and kinematics-engine must be complete before indicators
- **Phase 2 → Phase 3:** indicator-computation and stochastic-simulation must be complete before bayesian-evt
- **Phase 3 → Phase 4:** bayesian-evt and 3d-animation must be complete before portfolio-ui

## Technology Stack

- **Primary language:** Python 3.14+
- **Statistical:** numpy, scipy, pymc/arviz (Bayesian), statsmodels
- **ML:** scikit-learn, xgboost, torch (as needed)
- **Visualization:** matplotlib, seaborn, plotly, altair
- **Data:** pandas, geopandas
- **3D:** Three.js + GLTF models + PBR materials
- **2D:** Canvas 2D fallback mode
- **Bayesian:** PyMC, Pyodide (in-browser), pre-compute (server)
- **Containerization:** Docker, docker-compose
- **Documentation:** Jupyter, Markdown
- **Version control:** Git

## How to Use This Skill

When working on this project:
1. Read this SKILL.md for project context
2. Check the skill tree status (which capabilities are built)
3. Build missing subskills before attempting complex tasks
4. Follow evidence-first principles at every step
