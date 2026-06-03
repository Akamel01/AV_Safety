# Computation Strategy: Bayesian Analysis for AV_Safety Playground

## Overview

This document details both approaches for running Bayesian Hierarchical Extreme Value Theory (EVT) analysis: in-browser (Pyodide) and pre-computed + served, with a recommended hybrid approach.

---

## Option A: In-Browser (Pyodide)

### Architecture

```
User adjusts sliders
       │
       ▼
┌─────────────────────────────┐
│     JavaScript Frontend     │
│  (React / Vanilla JS)       │
│                             │
│  Collect parameter values   │
│  Pass to Pyodide worker     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Pyodide Worker          │
│  (WebAssembly)              │
│                             │
│  NumPy — kinematic sim      │
│  PyMC — Bayesian inference  │
│  SciPy — statistical tests  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Results (JSON)             │
│  → Indicator values         │
│  → Collision rate           │
│  → Severity CDF             │
│  → Posterior samples        │
│  → CIs / credible intervals │
└─────────────────────────────┘
```

### Package Requirements

```
# Pyodide packages (via pyodide.loadPackagesFromImports)
import numpy
import scipy
import pymc
import arviz

# Core computation modules
src/evaluation/bayesian_evt/
  gpd.py
  hierarchical.py
  collision_rate.py
  severity_model.py
  threshold_selection.py
  crisis.py
```

### Implementation Steps

1. **Build Pyodide bundle** with required Python packages
2. **Load Pyodide** as WebWorker (don't block main thread)
3. **Mount project code** into Pyodide filesystem via `pyodide.FS`
4. **Create Python function interface** in JS → Python
5. **Execute simulation** with parameterized inputs
6. **Extract results** as JSON via `pyodide.globals`
7. **Render** in UI (plots, indicator panels)

### Performance Estimates

| Operation | Estimate |
|---|---|
| Load Pyodide (first time) | ~10-20s |
| Load packages (numpy, scipy, pymc) | ~30-60s (cached after) |
| Monte Carlo sim (10,000 runs) | ~5-15s |
| GPD fitting | ~1-3s |
| Full Bayesian pipeline | ~10-30s |
| Indicator computation | ~0.1-0.5s |

### Memory Constraints

- Total WASM memory: ~1-2GB available in browser
- Python heap: limited by total WASM allocation
- Mitigation: Use `--memory-init-file 0` for smaller bundle, lazy-load packages

### Mitigation Strategies

1. **Lazy loading** — Only load PyMC when Bayesian analysis is requested
2. **Caching** — Cache results in IndexedDB for repeated parameter sets
3. **Adaptive MC samples** — Use fewer samples for fast indicator display (N=1,000), full for Bayesian (N=10,000)
4. **Progressive loading** — Show indicator results first, Bayesian results after they're ready
5. **Warm-start** — Cache the last Pyodide runtime; don't reload on every parameter change

---

## Option B: Pre-Computed + Served

### Architecture

```
Build Server
    │
    ├─ For each scenario (16 featured + 62 total)
    │   └─ Generate parameter grid (speed, distance, reaction time, etc.)
    │       ├─ Monte Carlo simulation (10,000 runs)
    │       ├─ GPD fitting to extreme values
    │       ├─ Bayesian hierarchical model (PyMC on server)
    │       └─ Output: JSON result files
    │
    ▼
┌─────────────────────────────┐
│     Web Server              │
│  (static files)             │
│                             │
│  /scenarios/crossing-01/    │
│    ├── indicators.json       │
│    ├── collision_rate.json   │
│    ├── severity_cdf.json     │
│    ├── posterior_samples.json│
│    └── mrl_plot.json         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     Client Browser          │
│                             │
│  Fetch JSON results         │
│  Render plots               │
└─────────────────────────────┘
```

### Implementation Steps

1. **Define parameter grids** for each scenario
   ```python
   # Example parameter grid for rear-end cut-in scenario
   speed_grid = np.arange(10, 35, 5)          # m/s
   distance_grid = np.arange(5, 50, 5)        # m
   reaction_grid = np.arange(0.8, 3.5, 0.4)   # s
   # Total grid points: 5 × 10 × 6 = 300
   ```

2. **Run Monte Carlo simulations** for each grid point
   ```python
   # For each (speed, distance, reaction_time)
   n_mc = 10000
   for speed in speed_grid:
       for distance in distance_grid:
           for reaction_time in reaction_grid:
               # Run kinematic simulation
               # Extract extreme values (min TTC, max DRAC)
               # Fit GPD
               # Store results
   ```

3. **Fit Bayesian hierarchical model** on server
   ```python
   # PyMC on server (no browser constraints)
   import pymc as pm
   import arviz as az
   
   with pm.Model() as hierarchical_model:
       # Level 1: scenario-specific GPD parameters
       xi = pm.Normal("xi", mu=0, sigma=1)
       sigma = pm.HalfNormal("sigma", sigma=2)
       
       # Level 2: conflict-type hyperpriors
       xi_hyper = pm.Normal("xi_hyper", mu=0, sigma=0.5)
       sigma_hyper = pm.HalfNormal("sigma_hyper", sigma=1)
       
       # Level 3: jurisdiction hyperpriors (USA/Canada/England)
       # ...
       
       trace = pm.sample(2000, tune=1000, chains=4)
   ```

4. **Package results as JSON**
   ```json
   {
     "scenario_id": "RE-CA-001",
     "parameters": {
       "speed": {"grid": [10, 15, 20, 25, 30], "unit": "m/s"},
       "cut_in_distance": {"grid": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50], "unit": "m"},
       "reaction_time": {"grid": [0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2], "unit": "s"}
     },
     "collision_rate": {
       "grid_3d": [[0.001, 0.005, ...], ...],
       "threshold_ttc": 2.0,
       "threshold_mrl": 1.5
     },
     "severity_gpd": {
       "xi": 0.35,
       "sigma": 8.2,
       "ci_95": {"xi": [0.12, 0.58], "sigma": [5.4, 12.1]}
     },
     "indicators": {
       "ttc": {"mean": 3.2, "median": 3.0, "min": 0.1, "p5": 0.8, "p95": 7.5},
       "drac": {"mean": 3.8, "median": 3.5, "max": 12.1},
       "delta_v": {"mean": 15.2, "median": 14.0, "max": 45.0}
     }
   }
   ```

5. **Serve via static files** (no backend needed)

### Pros and Cons

**Pros:**
- Instant response (no WASM loading)
- Full precision Bayesian computation (unconstrained)
- No memory limits
- No WASM bundle size concerns
- Easy to update (regenerate grid, upload new JSON)

**Cons:**
- Limited to predefined parameter grids (not continuous)
- Rebuild needed for new scenarios
- No true interactivity for Bayesian part
- Grid resolution trade-off (fine grid = huge JSON files)

### Grid Resolution Guidance

| Parameter | Range | Step | Points |
|---|---|---|---|
| Speed (m/s) | 5–40 | 5 | 8 |
| Cut-in distance (m) | 5–60 | 5 | 12 |
| Reaction time (s) | 0.5–3.5 | 0.5 | 7 |
| Braking delay (s) | 0.1–1.0 | 0.2 | 5 |
| Road friction | 0.3–0.9 | 0.1 | 7 |

For 2-parameter scenarios (e.g., speed vs distance): 8 × 12 = 96 grid points
For 3-parameter scenarios: 8 × 12 × 7 = 672 grid points
For 4+ parameters: use factorial design to reduce grid points

### Storage Estimates

- Per scenario (full grid, 4+ params): ~50-200 MB JSON (too large for static hosting)
- Per featured scenario (2 params, finer grid): ~1-5 MB JSON (reasonable)
- **Recommendation:** Only pre-compute 2-parameter grids for featured scenarios; use Pyodide for 3+ parameter scenarios

---

## Recommended: Hybrid Approach

### Decision Matrix

| Scenario Type | Approach | Reason |
|---|---|---|
| Featured (2 per type, 16 total) | Pre-computed grid (2 params) | Fast initial load, shows full Bayesian results |
| Remaining (46+ scenarios) | Pyodide in-browser | Interactive, no pre-computation needed |
| User-adjusted parameters | Pyodide in-browser | Must be dynamic |
| Edge case exploration | Pyodide in-browser | On-demand, unpredictable |

### Flow

```
User opens scenario
       │
       ▼
  Load pre-computed results (instant)
       │
       ├── Display indicators
       ├── Display Bayesian results
       └── Show "Results loaded from cached analysis"
       
User adjusts slider
       │
       ▼
  Check: is new parameter within pre-computed grid?
       │
       ├── YES → Interpolate from grid (instant)
       └── NO → Trigger Pyodide computation
              │
              ├── Show progress indicator ("Computing...")
              ├── Pyodide runs in background
              └── Results arrive → update UI
```

### Implementation

1. **Build phase:** Pre-compute 2-parameter grids for 16 featured scenarios
2. **Deploy phase:** Serve static JSON files alongside the playground
3. **Runtime phase:** 
   - Default: show pre-computed results
   - When user adjusts beyond grid: trigger Pyodide
   - Cache Pyodide results in IndexedDB
   - Auto-regenerate grid if new parameter combinations are requested

---

## Migration Path

If Pyodide proves too slow/heavy:
1. Switch to Option B fully
2. Use serverless functions (Cloudflare Workers, Vercel) for on-demand Bayesian computation
3. Serve results back to client via API

If Pyodide performs well:
1. Phase out pre-computed grids
2. Go fully Pyodide for all scenarios
3. Use IndexedDB caching for performance

---

## Evidence Needed

- Benchmark Pyodide performance on target devices (desktop, laptop, mobile)
- Test WASM bundle size and load time
- Verify PyMC works correctly in Pyodide (check compatibility)
- Measure IndexedDB storage limits across browsers
- Test Monte Carlo convergence speed in WASM vs native
