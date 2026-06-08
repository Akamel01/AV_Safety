# TOOLS.md - AV_Safety Project Tooling

_Project-specific tooling, environment details, and operational notes._

---

## Runtime Environment

| Component | Version | Path |
|-----------|---------|------|
| **Python** | 3.14.5 | `/opt/homebrew/bin/python3` |
| **pip** | (via pip3) | `/opt/homebrew/bin/pip3` |
| **Node.js** | v26.0.0 | `/opt/homebrew/bin/node` |
| **npm** | 11.12.1 | `/opt/homebrew/bin/npm` |
| **Git** | 2.50.1 | `/usr/bin/git` |
| **Docker** | 29.4.3 | `/usr/local/bin/docker` |
| **GitHub CLI** | `gh` | `/opt/homebrew/bin/gh` |

> Python `python` (no version suffix) is NOT installed — always use `python3`.

---

## Project Paths

| Item | Path |
|------|------|
| **Project root** | `/Users/akamel/projects/AV_Safety/` |
| **Git repo** | `git@github.com:Akamel01/AV_Safety.git` |
| **Source code** | `src/` — split into `risk_quantification/` and `safety_thresholds/` |
| **Single-scenario demo** | `single-scenario-demo/` — Three.js + Canvas 2D + Pyodide |
| **Skills (project-local)** | `skills/` — 8+ skill packages |
| **Tests** | `tests/` |
| **Data directories** | `data/raw/`, `data/processed/` (currently empty) |
| **Models** | `models/` (currently empty) |
| **Docs** | `docs/` |
| **Config** | `config/` |
| **Deploy** | `deploy/` — Dockerfile, docker-compose.yml, docker-entrypoint.sh, nginx.conf |
| **Notebooks** | `notebooks/` |
| **Scripts** | `scripts/` |

---

## Docker Services

`docker-compose.yml` defines 4 services:

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| **dev** | `av-safety-dev` | — | Development shell, full project mount |
| **risk-api** | `av-safety-api` | `8000` | FastAPI risk quantification API (uvicorn) |
| **portfolio-ui** | `av-safety-ui` | `80` | Portfolio UI (static files + nginx fallback) |
| **nginx** | `av-safety-nginx` | `8080` | Reverse proxy — unified entry point |

### Entrypoint Commands

```bash
# Start all services
docker-compose up -d

# Start API only
SERVICE=api ENVIRONMENT=development docker-compose up -d risk-api

# Start UI only
SERVICE=ui ENVIRONMENT=development docker-compose up -d portfolio-ui

# API URL (development)
#   http://localhost:8000

# Portfolio UI URL
#   http://localhost:80

# Nginx proxy URL
#   http://localhost:8080
```

### Dockerfile Notes

- **Base image:** `python:3.12-slim` (multi-stage build)
- **Exposed port:** 8000
- **ENTRYPOINT:** `["python3", "-m", "uvicorn"]` — this is a known issue. The Dockerfile's ENTRYPOINT conflicts with `docker-compose.yml`'s `docker-entrypoint.sh` override. If `docker-entrypoint.sh` is not being used, the ENTRYPOINT should be reviewed.
- **CMD:** `src.risk_quantification.pipeline:app --host 0.0.0.0 --port 8000`

### Docker Entrypoint

`deploy/docker-entrypoint.sh` handles service selection via `SERVICE` env var:

| SERVICE value | What it does |
|---------------|-------------|
| `api` (default) | Starts uvicorn on port 8000, 4 workers |
| `ui` | Serves portfolio UI via nginx or Python fallback on port 80 |
| `worker` | Background task processor (stub) |

In production: 4 uvicorn workers, logging to stderr, debug off.
In development: 1 worker, console + file logging, debug on.

---

## Nginx Configuration

`deploy/nginx.conf`:

| Location | Upstream | Purpose |
|----------|----------|---------|
| `/` | Static files from `/app/ui` | Portfolio UI |
| `/docs/` | Static files from `/app/docs/` | Documentation directory listing |
| `/api/` | `http://risk-api:8000/` | Risk API proxy |

Proxy headers: `Host`, `X-Real-IP`.

---

## Ollama / Semantic Extraction

Environment variables from `.env`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama API endpoint |
| `OLLAMA_MODEL` | `gpt-oss:120b-cloud` | Model for semantic chunking |
| `OLLAMA_API_KEY` | (redacted) | API key for cloud model |
| `GRAPHIFY_OLLAMA_PARALLEL` | (unset) | Parallel semantic chunking flag |

---

## Output & Data Paths

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_RAW_DIR` | `data/raw` | Raw ingestion directory |
| `DATA_PROCESSED_DIR` | `data/processed` | Cleaned/transformed data |
| `MODELS_DIR` | `models` | Trained model checkpoints |
| `OUTPUT_DIR` | `outputs` | Analysis outputs |
| `DEBUG` | `0` | Verbose logging flag |

External data sources to populate:
- **NHTSA FARS** — Fatality Analysis Reporting System (USA)
- **CISS** — Continuous I-70 Study Site (USA)
- **Transport Canada** — Canadian crash data
- **DfT GB** — Department for Transport, UK

---

## Project Skills

Located at `skills/`:

| Skill | Path | Purpose |
|-------|------|---------|
| **scenario-taxonomy** | `skills/scenario-taxonomy/` | 42 conflict scenarios, 8 types |
| **data-exploration** | `skills/data-exploration/` | Data analysis workflows |
| **bayesian-evt** | `skills/bayesian-evt/` | Bayesian Extreme Value Theory |
| **kinematics-engine** | `skills/kinematics-engine/` | Conflict type formulas |
| **indicator-computation** | `skills/indicator-computation/` | 42 surrogate safety indicators |
| **bayesian-analysis** | `skills/bayesian-analysis/` | Bayesian modeling |
| **risk-quantification** | `skills/risk-quantification/` | Risk scoring pipeline |
| **safety-thresholds** | `skills/safety-thresholds/` | Safety threshold definitions |

### Project-Local SKILL.md

Master skill at project root: `AV_Safety/SKILL.md` — lists all skill capabilities and provides project overview.

---

## Python Dependencies

Key packages from `requirements.txt`:

| Category | Packages |
|----------|---------|
| **Data manipulation** | pandas≥2.0, numpy≥1.26, scipy≥1.12 |
| **Bayesian** | statsmodels≥0.14, pymc≥5.0, arviz≥0.15, pystan≥3.0 |
| **ML** | scikit-learn≥1.4, xgboost≥2.0 |
| **Visualization** | matplotlib≥3.8, seaborn≥0.13, plotly≥5.18, altair≥5.0 |
| **Geospatial** | geopandas≥0.14, shapely≥2.0, folium≥0.15 |
| **Data I/O** | requests≥2.31, urllib3≥2.1, pydantic≥2.0, pyyaml≥6.0 |
| **Notebooks** | jupyter≥1.0, ipywidgets≥8.0 |
| **Testing** | pytest≥7.0, pytest-cov≥4.0 |

Install: `pip3 install -r requirements.txt`

> **Known issue:** `uvicorn` and `fastapi` are referenced in the Dockerfile's ENTRYPOINT/CMD but NOT in `requirements.txt`. Add them before deployment.

---

## GitHub Repository

| Property | Value |
|----------|-------|
| **Remote** | `git@github.com:Akamel01/AV_Safety.git` |
| **URL** | https://github.com/Akamel01/AV_Safety.git |
| **Owner** | Akamel01 |
| **GitHub CLI** | `gh` available at `/opt/homebrew/bin/gh` |

---

## Source Code Layout

`src/` contains two Python packages:

### `src/risk_quantification/`
| Module | Purpose |
|--------|---------|
| `pipeline.py` | 7-step pipeline: kinematics → indicators → Monte Carlo → Bayesian EVT → collision modeling → safety thresholds → portfolio output |
| `risk_scoring.py` | Composite risk scoring (weights: 0.3/0.3/0.2/0.2 — flagged as arbitrary, needs derivation) |
| `threshold_checker.py` | Validates indicators against safety thresholds |
| `results_aggregator.py` | Aggregates Monte Carlo and EVT results |
| `output_formats.py` | JSON, CSV, report output formatting |
| `report_generator.py` | Human-readable analysis reports |
| `pipeline_validation.py` | Pipeline integrity checks |

### `src/safety_thresholds/`
| Module | Purpose |
|--------|---------|
| `ttc_thresholds.py` | Time-to-Collision thresholds |
| `drac_thresholds.py` | DRAC (Delta Ratio of Acceleration) thresholds |
| `collision_rate_thresholds.py` | Collision rate thresholds |
| `standards.py` | Standards-aligned thresholds (UL 4600, ISO 21448, ISO 26262) |
| `acceptable_risk.py` | Acceptable risk definitions |
| `safe_threshold.py` | Safe operation thresholds |
| `baseline_estimator.py` | Baseline risk estimation |
| `deployment_criteria.py` | Deployment readiness criteria |
| `monitoring.py` | Runtime safety monitoring |

---

## Single-Scenario Demo

Location: `single-scenario-demo/`

| File | Purpose |
|------|---------|
| `index.html` | Main HTML with Three.js + Canvas 2D + Pyodide embedding |
| `style.css` | Styling for demo interface |
| `app.js` | **MISSING** — `index.html` references `<script src="app.js">` but file does not exist. Demo is non-functional in any browser. |
| `modules/` | 5 JS modules (kinematics, indicators, bayesian-evt, 3d-renderer, visualization) |
| `data/` | Scenario configuration JSON |
| `docs/` | Demo-specific documentation |
| `assets/` | Static assets |

> **Critical blocker:** The demo cannot run until `app.js` is created. `index.html` references it but the file does not exist.

---

## Development Checklist

- [ ] Run `pip3 install -r requirements.txt` in project root
- [ ] Run `docker-compose up -d` for full stack
- [ ] Verify `http://localhost:8000` (API) responds
- [ ] Verify `http://localhost:80` (UI) serves the demo
- [ ] Verify `http://localhost:8080` (nginx proxy) routes correctly
- [ ] Run tests: `pytest tests/` from project root
- [ ] Update `data/raw/` with external crash data (NHTSA FARS, CISS, Transport Canada, DfT GB)
- [ ] Create missing `single-scenario-demo/app.js`
- [ ] Add `uvicorn` + `fastapi` to `requirements.txt`

---

## Known Issues & Fixes Needed

| # | Issue | Impact | Location |
|---|-------|--------|----------|
| 1 | `app.js` missing from single-scenario-demo | Demo non-functional | `single-scenario-demo/` |
| 2 | `uvicorn` not in `requirements.txt` but referenced in Dockerfile | Docker build/runtime failure | `requirements.txt`, `deploy/Dockerfile` |
| 3 | Monte Carlo uses heuristic approximations, not kinematics engine | Simulation results not grounded in physics | `src/risk_quantification/pipeline.py` |
| 4 | Bayesian EVT uses Method of Moments, not PyMC | No actual Bayesian inference | `src/risk_quantification/pipeline.py` |
| 5 | Risk scoring weights (0.3/0.3/0.2/0.2) are arbitrary | Risk scores not justified | `src/risk_quantification/risk_scoring.py` |
| 6 | Bayesian EVT JSON schema mismatch — JS expects `{xi: {estimate}}`, Python returns `{gpd_params: {xi}}` | Cross-language data flow broken | `single-scenario-demo/modules/bayesian-evt.js` vs Python pipeline |
| 7 | CSV exporter references `_get_fieldnames()` on wrong class | Exporter fails at runtime | `src/risk_quantification/output_formats.py` |
| 8 | Collision detection uses 0.01m tolerance (1cm) | May miss edge collisions | Kinematics engine |
| 9 | Monte Carlo in demo uses sync loop — 10k samples blocks UI thread | UI freeze | Demo JS |
| 10 | No `.github/` directory — no GitHub Actions workflows | No CI/CD | Root |
| 11 | All skills lack `driver.py` executable files | Skills not runnable via CLI | `skills/*/` |
| 12 | Three.js post-processing (bloom/film) commented out | Visual effects not working | Demo JS |

---

## OpenClaw Skills Used for This Project

These OpenClaw skills may be relevant during development:

- **git/github** — Issue tracking, PR management, code review
- **diagram-maker** — Architecture diagrams for documentation
- **summarize** — Research paper analysis
- **taskflow** — Multi-step detached task orchestration
- **taskflow-inbox-triage** — Managing task backlog

---

_Last updated: 2026-07-05 (session start)_
