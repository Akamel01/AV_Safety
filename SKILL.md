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
3. **How do we model and quantify collision risk across USA, Canada, and UK contexts?**

## Working Principles (evidence-first)

- **No assumptions.** Every claim must be backed by data, standards text, or code output.
- **Verifiable.** Every analysis script must produce reproducible results.
- **Rigorous.** Statistical methods must be documented and justified.
- **Traceable.** All data sources, transformations, and model decisions are versioned and logged.

## Skill Tree (reusable capabilities)

This project's work breaks into these reusable skills — each with its own SKILL.md:

### Phase 1: Foundation
- [x] **project-setup** — Initialize AV_Safety workspace (this skill)
- [x] **standards-research** — Search, extract, and organize UL 4600, ISO, NHTSA standards
- [x] **risk-metrics** — Define and implement collision risk metrics
- [x] **bayesian-analysis** — Bayesian modeling of risk and uncertainty
- [ ] **data-ingest** — Ingest NHTSA crash datasets, traffic safety databases
- [ ] **data-exploration** — EDA workflows for collision risk data

### Phase 2: Analysis
- [ ] **statistical-validation** — Statistical validation of safety claims

### Phase 3: Modeling
- [ ] **collision-modeling** — Build collision risk prediction models
- [ ] **safety-thresholds** — Quantify "safe enough" thresholds
- [ ] **risk-quantification** — End-to-end risk quantification pipeline

### Phase 4: Portfolio
- [ ] **visualization** — Portfolio-grade visualizations and dashboards
- [ ] **portfolio-deploy** — Build and deploy portfolio presentation

## Technology Stack

- **Primary language:** Python 3.14+
- **Statistical:** numpy, scipy, pymc/arviz (Bayesian), statsmodels
- **ML:** scikit-learn, xgboost, torch (as needed)
- **Visualization:** matplotlib, seaborn, plotly, altair
- **Data:** pandas, geopandas
- **Containerization:** Docker, docker-compose
- **Documentation:** Jupyter, Markdown
- **Version control:** Git

## How to Use This Skill

When working on this project:
1. Read this SKILL.md for project context
2. Check the skill tree status (which capabilities are built)
3. Build missing subskills before attempting complex tasks
4. Follow evidence-first principles at every step
