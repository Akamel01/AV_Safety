# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AV_Safety** — Independent research portfolio on quantifying autonomous vehicle collision risk. Core question: "How safe is safe enough for autonomous vehicles?" Grounded in real-world crash data, Bayesian analysis, and international safety standards (UL 4600, ISO 21448 SOTIF, ISO 26262, NHTSA guidance). Focus jurisdictions: USA, Canada, UK.

## Working Directory

`/Users/akamel/projects/AV_Safety`

## Quick Start

```bash
pip3 install -r requirements.txt        # Install dependencies
jupyter notebook notebooks/              # Launch exploratory analysis
docker-compose up -d                    # Build dev container (python:3.14-slim)
```

## Top-Level Structure

```
AV_Safety/
├── src/                 # Python source code (the active codebase)
├── skills/              # 18 skill definitions (SKILL.md + references/ + modules/)
├── single-scenario-demo/  # Standalone HTML/JS demo for single scenario visualization
├── docs/                # Architecture plans and research notes
├── config/              # Configuration files
├── models/              # Trained model checkpoints
├── data/                # Raw (empty) and processed (empty) data directories
├── notebooks/           # Exploratory Jupyter notebooks
├── scripts/             # Reproducible analysis scripts
├── tests/               # Test directory (currently empty)
├── ui/                  # UI directory (currently empty)
├── memory/              # Session memory (daily notes)
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Dev container
├── SKILL.md            # Master skill tree with build order
├── AGENTS.md           # Agent workspace rules and workflow discipline
├── SOUL.md             # Agent behavior guidelines
└── USER.md             # User context (Ahmed, PDT timezone)
```

## Python Source Architecture

Two active packages under `src/`:

### `src/risk_quantification/` — End-to-end pipeline
- `pipeline.py` — Main orchestrator: 7-step pipeline (kinematics → indicators → Monte Carlo → Bayesian EVT → collision modeling → safety thresholds → portfolio output)
- `risk_scoring.py` — Risk scoring logic
- `threshold_checker.py` — Threshold compliance checking
- `results_aggregator.py` — Aggregates scenario results
- `report_generator.py` — Generates risk reports
- `output_formats.py` — JSON, CSV, Markdown exporters
- Subpackages: `output_formats/`, `validation/`

### `src/safety_thresholds/` — Threshold definitions
- `baseline_estimator.py` — Baseline risk estimation
- `acceptable_risk.py` — Acceptable risk definitions
- `safe_threshold.py` — Safe threshold quantification
- `collision_rate_thresholds.py` — Collision rate thresholds
- `ttc_thresholds.py` — Time-to-collision thresholds
- `drac_thresholds.py` — Deceleration-rate-at-collision thresholds
- `standards.py` — UL 4600 and ISO 21448 threshold constants
- `deployment_criteria.py` — AV deployment criteria
- `monitoring.py` — Continuous monitoring logic

### Stubs (directories exist but empty)
- `src/analysis/`, `src/data_pipeline/`, `src/evaluation/`, `src/risk_models/`, `src/standards/`

## Skills System

18 skills under `skills/`, organized in a 4-phase build order:

```
phase1 (foundation) → phase2 (analysis) → phase3 (modeling) → phase4 (portfolio)
```

**Built (14/18):** project-setup, standards-research, risk-metrics, bayesian-analysis, scenario-taxonomy, kinematics-engine, indicator-computation, stochastic-simulation, bayesian-evt, 3d-animation, data-ingest, data-exploration, statistical-validation, collision-modeling

**Pending (4):** safety-thresholds, risk-quantification, portfolio-ui, portfolio-deploy

Each skill is a directory with a `SKILL.md` and optional `references/`, `modules/`, `templates/`. Read `SKILL.md` in each skill directory for its capability definition. Master skill tree is in `SKILL.md` at the root.

## Key Conventions

- **Evidence-first**: Every claim must be backed by data or verified sources. Note when evidence is missing.
- **No assumptions**: Cite sources. When evidence is missing, say so and ask.
- **Public data only**: For AV_Safety, only use publicly available documents. Note restricted ones as "access restricted".
- **Concise by default**: Responses ≤ 20 lines. Technical details go in files.
- **One goal per turn**: No juggling unrelated tasks.
- **Max 2 file operations per turn**: Never mix file writes, web searches, exec, and git in the same turn.
- **Git hygiene**: One commit per logical unit. No push without permission.
- **Skill tree discipline**: Check existing skills before building new ones. Update skill tree status when skills are built.
