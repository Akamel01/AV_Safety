# AV_Safety — Collision Risk Analysis for Autonomous Vehicles

**Status:** Development — Single-Scenario Demo Functional  
**Last Updated:** 2026-06-07  
**License:** [To Be Determined]

---

## What It Is

AV_Safety is a research-grade collision risk quantification system for autonomous vehicles. It simulates rear-end collision scenarios, computes surrogate safety indicators, runs Monte Carlo simulations with parameter uncertainty, performs Bayesian extreme value analysis on tail risk, and classifies deployment risk levels.

## Quick Start

### Browser Demo (No Server Required)

1. Open `single-scenario-demo/index.html` in a modern browser (Chrome, Firefox, Safari)
2. Adjust parameter sliders or use preset scenarios
3. Click "Run Monte Carlo" to simulate 10k scenarios
4. Bayesian EVT runs automatically when collisions exceed 10 samples
5. Download CSV results or share via URL

### Python Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python3 -c "
from src.risk_quantification.pipeline import RiskQuantificationPipeline
import json

with open('single-scenario-demo/data/scenario-RE-CA-001.json') as f:
    scenario = json.load(f)

pipeline = RiskQuantificationPipeline(scenario, n_mc_samples=10000, jurisdiction='usa')
results = pipeline.run()

print('Risk Level:', results['portfolio_aggregation']['risk_level'])
print('Risk Score:', results['portfolio_aggregation']['overall_risk_score'])
"
```

### Docker

```bash
# Build and serve demo
docker compose up

# Or build production image
docker build -t av-safety .
```

## Architecture

```
AV_Safety/
├── src/                          # Python backend
│   ├── risk_quantification/      # Core pipeline (7 steps)
│   │   ├── pipeline.py           # Orchestrator
│   │   ├── kinematics_engine.py  # 2.5ms timestep simulation
│   │   ├── risk_scoring.py       # Composite risk scoring
│   │   ├── threshold_checker.py  # Jurisdiction compliance
│   │   ├── results_aggregator.py # Multi-scenario aggregation
│   │   └── output_formats.py     # CSV/JSON/Report export
│   └── safety_thresholds/        # Jurisdiction thresholds
│       ├── ttc_thresholds.py     # Time-to-collision standards
│       ├── drac_thresholds.py    # Delta-rated-acceleration
│       ├── deployment_criteria.py # AV deployment gates
│       └── ...
├── single-scenario-demo/          # Browser demo (no server)
│   ├── index.html                # Main UI
│   ├── style.css                 # Responsive styles
│   ├── app.js                    # Application orchestrator
│   └── modules/
│       ├── kinematics.js         # JS kinematics engine
│       ├── monte-carlo.js        # MC simulation with 42 indicators
│       ├── bayesian-evt.js       # GPD fitting + profile likelihood
│       ├── risk-scoring.js       # Composite scoring
│       └── visualization.js      # 3D (Three.js) + 2D Canvas
├── tests/                        # 46 pytest tests (all passing)
├── deploy/                       # Docker + CI scripts
├── skills/                       # 23 reusable capability skills
└── data/                         # Empty — external data ingestion pending
```

### Pipeline Steps

1. **Kinematics** — 2.5ms timestep simulation of vehicle trajectories
2. **Indicators** — 42 surrogate safety metrics (TTC, DRAC, PET, etc.)
3. **Monte Carlo** — 10k samples with parameter distributions → collision rate
4. **Bayesian EVT** — GPD fitting on tail exceedances (method of moments)
5. **Collision Modeling** — Ensemble of kinematics (40%) + EVT (60%)
6. **Safety Thresholds** — Compare against jurisdiction standards (USA, CAN, GB)
7. **Portfolio Aggregation** — Composite risk score (collision rate, severity, uncertainty, compliance)

## Safety Standards

| Standard | Application |
|----------|-------------|
| ISO 21448 (SOTIF) | Safety of the Intended Functionality |
| ISO 26262 | Functional safety for road vehicles |
| UL 4600 | Autonomous robotically operated vehicles |
| NHTSA FARS 2020 | Fatality Analysis Reporting System data |

### Jurisdiction Thresholds

| Jurisdiction | TTC (s) | DRAC (m/s²) | Deployment Status |
|-------------|---------|-------------|-------------------|
| USA (NHTSA) | ≥ 2.0 | < 4.0 | APPROVED / CONDITIONAL / DENIED |
| Canada (TC) | ≥ 2.5 | < 3.5 | APPROVED / CONDITIONAL / DENIED |
| GB (DfT) | ≥ 1.5 | < 5.0 | APPROVED / CONDITIONAL / DENIED |

## Known Limitations

- **Risk scoring weights (0.3/0.3/0.2/0.2)** are arbitrary — no empirical derivation
- **Bayesian EVT** uses heuristic approximation (Method of Moments) — full PyMC inference not available in browser
- **No external data** — all simulations use synthetic parameter distributions
- **No persistence** — results are lost when the page reloads

## Standards References

- NHTSA: Forward Collision Warning (FMVSS 126), Automatic Emergency Braking
- ISO 21448:2022 — Safety of the Intended Functionality
- ISO 26262:2018 — Road vehicles functional safety
- UL 4600:2022 — Standard for Autonomous Robots

---

*Built as a research and safety analysis tool. Not for real-world autonomous vehicle deployment without validation.*
