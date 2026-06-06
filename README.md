# AV_Safety — Interactive Collision Risk Playground

**Quantify pedestrian and cyclist collision risk using real-world kinematics, Bayesian Extreme Value Theory, and Monte Carlo simulation.**

AV_Safety is a research-grade toolkit for quantifying surrogate safety indicators in connected-vehicle and intersection scenarios. It provides an interactive 3D visualization playground alongside a REST API for scoring, thresholding, and portfolio-level risk analysis.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  AV_Safety Platform                                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Portfolio UI │◄──►│   Nginx      │◄──►│  Risk API    │   │
│  │  (Static/SPA) │    │  :8080       │    │  :8000       │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                           │                  │               │
│                           ▼                  ▼               │
│                     ┌──────────┐      ┌──────────────┐      │
│                     │ Nginx    │      │ Kinematics   │      │
│                     │ Proxy    │      │ Engine       │      │
│                     └──────────┘      └──────────────┘      │
│                             │                │               │
│                             ▼                ▼               │
│                     ┌──────────────────────────────┐       │
│                     │  Monte Carlo + Bayesian EVT   │       │
│                     │  + Indicator Computation      │       │
│                     └──────────────────────────────┘       │
│                                            │               │
│                                            ▼               │
│                     ┌──────────────────────────────┐       │
│                     │  Safety Thresholds           │       │
│                     │  (UL 4600 · ISO 21448 ·      │       │
│                     │   ISO 26262)                 │       │
│                     └──────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

- **Risk API** (`:8000`) — FastAPI service running the 7-step quantification pipeline
- **Portfolio UI** (`:80`) — Three.js + Canvas 2D / Pyodide interactive visualizer
- **Nginx** (`:8080`) — Reverse proxy unifying all endpoints under a single host

---

## Quick Start

### 1. Local Development (Python)

```bash
cd AV_Safety
pip3 install -r requirements.txt
python3 -m uvicorn src.risk_quantification.pipeline:app --host 0.0.0.0 --port 8000
```

### 2. Docker Compose (Full Stack)

```bash
cd AV_Safety
docker-compose up -d

# Risk API    → http://localhost:8000
# Portfolio UI → http://localhost:80
# Nginx proxy → http://localhost:8080
```

### 3. Single-Scenario Demo (No Docker)

Open `single-scenario-demo/index.html` in a browser. The demo runs Three.js and Pyodide entirely client-side with pre-loaded scenario data.

---

## Skills

The project ships with **21 skill packages** in `skills/`, each covering a distinct analysis domain:

| Skill | Focus |
|-------|-------|
| `scenario-taxonomy` | 42 conflict scenarios across 8 types |
| `kinematics-engine` | Interaction-speed formulas for each conflict type |
| `indicator-computation` | 42 surrogate safety indicators |
| `monte-carlo` | Monte Carlo simulation engine |
| `bayesian-evt` | Bayesian Extreme Value Theory |
| `collision-modeling` | Collision probability models |
| `risk-metrics` | MIAT, PMF, and risk scoring |
| `risk-quantification` | Full 7-step pipeline orchestrator |
| `safety-thresholds` | UL 4600 / SAE J3016 compliance thresholds |
| `data-ingest` | Raw data ingestion (NHTSA FARS, CISS, etc.) |
| `data-exploration` | Exploratory data analysis workflows |
| `bayesian-analysis` | General Bayesian modeling |
| `stochastic-simulation` | Stochastic process simulation |
| `3d-animation` | Animated collision visualizations |
| `portfolio-ui` | Portfolio-level dashboard UI |
| `portfolio-deploy` | Docker + Nginx deployment |
| `statistical-validation` | Statistical validation & goodness-of-fit |
| `standards-research` | Regulatory standards alignment |
| `validation` | End-to-end validation harness |
| `project-setup` | Environment bootstrap and setup |
| `graphify-out` | Graph-based output / report generation |

Each skill includes a `SKILL.md` with usage instructions.

---

## 42 Conflict Scenarios

The `scenario-taxonomy` skill defines **42 scripted conflict scenarios** spanning 8 conflict types:

1. **Following — Stationary Ahead** (4 scenarios)
2. **Following — Moving Ahead** (5 scenarios)
3. **Cut-in** (5 scenarios)
4. **Cut-out** (5 scenarios)
5. **Merging** (5 scenarios)
6. **Perpendicular — Crossing** (5 scenarios)
7. **Opposite — Crossing** (5 scenarios)
8. **Opposite — Reversal** (5 scenarios)

Each scenario includes kinematic profiles (acceleration, speed, distance), interaction points, and severity classification.

---

## Standards Alignment

AV_Safety is designed to align with key autonomous-vehicle safety standards:

- **UL 4600** — Standard for Application of Safety Engineering for Autonomy
- **ISO 21448 (SOTIF)** — Safety of the Intended Functionality for ADAS
- **ISO 26262** — Road vehicles functional safety (ASIL mapping via SAE J3016)

Safety thresholds in the `safety-thresholds` skill map surrogate indicators (PET, TTC, TTC-based measures) to ASIL levels and SOTIF hazard categories.

---

## Project Structure

```
AV_Safety/
├── src/                     # Core source code
│   ├── risk_quantification/ # 7-step pipeline (FastAPI app)
│   └── safety_thresholds/   # Threshold definitions & compliance
├── skills/                  # 21 skill packages
├── tests/                   # Pytest test suite
├── data/                    # Raw & processed data
├── deploy/                  # Docker + Nginx configuration
├── single-scenario-demo/    # Standalone browser demo
├── notebooks/               # Jupyter exploration
├── config/                  # YAML/JSON configuration
└── docs/                    # Generated documentation
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/quantify` | Run full 7-step quantification pipeline |
| `POST` | `/api/thresholds/check` | Check scenario against safety thresholds |
| `GET`  | `/api/indicators` | List available surrogate indicators |
| `GET`  | `/api/scenarios` | List all 42 conflict scenarios |
| `GET`  | `/api/health` | Health check |

---

## Requirements

- Python 3.10–3.12
- Docker & Docker Compose (for full stack)
- ~2 GB RAM minimum; ~8 GB recommended for Bayesian EVT

Key dependencies: `pandas`, `numpy`, `scipy`, `statsmodels`, `pymc`, `plotly`, `fastapi`, `uvicorn`, `pydantic`.

See `requirements.txt` for the full list.

---

## Testing

```bash
pytest tests/
pytest tests/ --cov=src --cov-report=term-missing
```

---

## License

Research / experimental. See the repository root for license details.

---

## Acknowledgments

- NHTSA FARS database for crash data reference
- UT Dallas Crash Investigation Simulation System (CISS)
- Transport Canada and UK DfT traffic safety datasets
- UL 4600, ISO 21448, ISO 26262 standards bodies
- The open-source Bayes, PyMC, and SciPy communities

---

*Built for safe, explainable, and quantifiable autonomous vehicle safety research.*
