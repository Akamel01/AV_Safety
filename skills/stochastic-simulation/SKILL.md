# Skill: Stochastic Simulation

**Purpose:** Drive Monte Carlo simulations for collision risk quantification, parameter sampling, and uncertainty propagation through the kinematic engine.

## 1. Simulation Framework

### 1.1 Core Design

```
Parameter Space (θ)
    │
    ▼
┌──────────────────────┐
│  Monte Carlo Sampler  │
│  (N iterations)       │
│                       │
│  For i = 1 to N:      │
│    1. Sample θ_i ~ p(θ)│
│    2. Run simulation  │
│    3. Extract outcomes│
│    4. Compute results │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│  Monte Carlo Results  │
│  - Collision rate     │
│  - Severity stats     │
│  - Indicator CDFs     │
│  - Uncertainty bounds │
└──────────────────────┘
```

### 1.2 Simulation Parameters by Scenario Type

```python
@dataclass
class ScenarioParameters:
    """Parameters for a single Monte Carlo run."""
    
    # Scenario-specific parameters (sampled from distributions)
    speed_lead: float                    # m/s, normal or lognormal
    speed_follow: float                  # m/s
    cut_in_distance: float               # m, exponential or gamma
    reaction_time: float                 # s, lognormal
    braking_delay: float                 # s, lognormal
    road_friction: float                 # μ, uniform or normal
    lane_width: float                    # m, ±0.1m from standard
    vehicle_length: float                # m, ±0.2m from nominal
    vehicle_width: float                 # m
    
    # Scenario metadata
    scenario_id: str
    conflict_type: str
    iteration: int
    
    def validate(self) -> bool:
        """Validate parameters are within physically possible ranges."""
        if self.speed_lead < 0 or self.speed_lead > 50:
            return False
        if self.reaction_time < 0.1 or self.reaction_time > 5.0:
            return False
        if self.road_friction < 0.05 or self.road_friction > 1.0:
            return False
        if self.cut_in_distance < 0 or self.cut_in_distance > 100:
            return False
        return True
```

## 2. Parameter Distribution Specifications

### 2.1 Speed Distributions

```python
# Speed distributions by road type and vehicle type
SPEED_DISTRIBUTIONS = {
    # Urban conditions
    "urban_car": {"mu": 11.2, "sigma": 3.1, "min": 0, "max": 33.3},  # 40 km/h avg
    "urban_suv": {"mu": 12.0, "sigma": 3.5, "min": 0, "max": 33.3},
    "urban_truck": {"mu": 10.5, "sigma": 2.8, "min": 0, "max": 27.8},
    "urban_pedestrian": {"mu": 1.4, "sigma": 0.4, "min": 0, "max": 3.5},
    "urban_cyclist": {"mu": 5.0, "sigma": 1.5, "min": 0, "max": 15.0},
    
    # Highway conditions
    "highway_car": {"mu": 27.8, "sigma": 4.2, "min": 15.6, "max": 41.7},  # 100 km/h avg
    "highway_suv": {"mu": 28.5, "sigma": 4.5, "min": 15.6, "max": 41.7},
    "highway_truck": {"mu": 24.0, "sigma": 3.8, "min": 13.9, "max": 36.1},
    
    # Freeway conditions
    "freeway_car": {"mu": 30.6, "sigma": 4.8, "min": 22.2, "max": 44.4},  # 110 km/h avg
}

# Sample from distribution
from scipy.stats import norm, lognorm, expon, gamma

def sample_speed(dist_name, n=1):
    dist = SPEED_DISTRIBUTIONS[dist_name]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))
```

### 2.2 Reaction Time Distribution

```python
# Reaction time follows lognormal distribution (positive, right-skewed)
# Typical values from literature:
# - Perception time: 0.25-0.75s
# - Decision time: 0.50-1.25s
# - Motor response: 0.15-0.30s
# Total: ~1.0-2.5s typical, some up to 4-5s

REACTION_TIME_PARAMS = {
    "normal": {"mu_log": 0.7, "sigma_log": 0.3},  # median ~ 2.0s
    "alert": {"mu_log": 0.5, "sigma_log": 0.2},   # median ~ 1.4s
    "distracted": {"mu_log": 0.9, "sigma_log": 0.4},  # median ~ 2.7s
    "elderly": {"mu_log": 1.0, "sigma_log": 0.35},  # median ~ 3.0s
    "exhausted": {"mu_log": 1.1, "sigma_log": 0.45},  # median ~ 3.3s
}

def sample_reaction_time(condition="normal", n=1):
    params = REACTION_TIME_PARAMS[condition]
    return max(0.1, min(lognorm.rvs(params["sigma_log"], 
                       scale=np.exp(params["mu_log"]), size=n), 5.0))
```

### 2.3 Braking Delay Distribution

```python
# Time between decision to brake and actual brake application
BRAKING_DELAY_PARAMS = {
    "standard": {"mu_log": -0.5, "sigma_log": 0.2},  # median ~ 0.6s
    "panic": {"mu_log": -0.3, "sigma_log": 0.15},    # median ~ 0.75s
    "slow": {"mu_log": 0.0, "sigma_log": 0.3},       # median ~ 1.0s
}

def sample_braking_delay(condition="standard", n=1):
    params = BRAKING_DELAY_PARAMS[condition]
    return max(0.05, min(lognorm.rvs(params["sigma_log"],
                       scale=np.exp(params["mu_log"]), size=n), 2.0))
```

### 2.4 Road Friction Distribution

```python
# Friction coefficient distributions by road condition
FRICTION_DISTRIBUTIONS = {
    "dry_asphalt": {"mu": 0.80, "sigma": 0.05, "min": 0.6, "max": 0.95},
    "wet_asphalt": {"mu": 0.45, "sigma": 0.08, "min": 0.3, "max": 0.6},
    "snow": {"mu": 0.20, "sigma": 0.08, "min": 0.1, "max": 0.35},
    "ice": {"mu": 0.10, "sigma": 0.05, "min": 0.05, "max": 0.20},
    "gravel": {"mu": 0.55, "sigma": 0.10, "min": 0.4, "max": 0.75},
}

def sample_friction(condition="dry_asphalt", n=1):
    dist = FRICTION_DISTRIBUTIONS[condition]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))
```

### 2.5 Cut-in Distance Distribution

```python
# Distance at which cut-in maneuver begins
CUTIN_DISTRIBUTIONS = {
    "aggressive": {"mu": 10, "sigma": 3, "min": 5, "max": 20},
    "normal": {"mu": 25, "sigma": 8, "min": 10, "max": 50},
    "conservative": {"mu": 40, "sigma": 10, "min": 20, "max": 70},
}

def sample_cutin_distance(behavior="normal", n=1):
    dist = CUTIN_DISTRIBUTIONS[behavior]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))
```

## 3. Monte Carlo Engine

### 3.1 Core Simulation Loop

```python
import numpy as np
from scipy import stats

class MonteCarloEngine:
    """Driver for stochastic collision risk simulation."""
    
    def __init__(self, scenario: Scenario, n_samples: int = 10000):
        self.scenario = scenario
        self.n_samples = n_samples
        self.results = {}
        
    def run(self) -> dict:
        """Execute full Monte Carlo simulation."""
        # Pre-allocate storage
        collision_outcomes = np.zeros(self.n_samples)
        indicators = {}
        all_indicators = get_all_applicable_indicators(self.scenario.conflict_type)
        for ind in all_indicators:
            indicators[ind] = np.zeros(self.n_samples)
        
        # Run simulations
        for i in range(self.n_samples):
            # Sample parameters
            params = self._sample_parameters(i)
            
            # Validate
            if not params.validate():
                collision_outcomes[i] = np.nan
                continue
            
            # Run kinematic simulation
            trajectory, collision = simulate_kinematics(params, self.scenario)
            
            # Record outcome
            collision_outcomes[i] = 1.0 if collision else 0.0
            
            # Compute indicators for this run
            for ind in all_indicators:
                indicators[ind][i] = compute_indicator(ind, trajectory, collision)
        
        # Aggregate results
        self.results = self._aggregate_results(collision_outcomes, indicators)
        
        return self.results
    
    def _sample_parameters(self, iteration: int) -> ScenarioParameters:
        """Sample a single set of parameters for Monte Carlo iteration."""
        return ScenarioParameters(
            speed_lead=sample_speed(self.scenario.lead_speed_dist, 1)[0],
            speed_follow=sample_speed(self.scenario.follow_speed_dist, 1)[0],
            cut_in_distance=sample_cutin_distance(self.scenario.cutin_behavior, 1)[0],
            reaction_time=sample_reaction_time(self.scenario.reaction_condition, 1)[0],
            braking_delay=sample_braking_delay("standard", 1)[0],
            road_friction=sample_friction(self.scenario.road_condition, 1)[0],
            lane_width=3.5 + np.random.normal(0, 0.1),
            vehicle_length=self.scenario.vehicle_length + np.random.normal(0, 0.2),
            vehicle_width=1.85 + np.random.normal(0, 0.05),
            scenario_id=self.scenario.id,
            conflict_type=self.scenario.conflict_type,
            iteration=iteration
        )
    
    def _aggregate_results(self, collisions: np.ndarray, indicators: dict) -> dict:
        """Aggregate Monte Carlo results into summary statistics."""
        n_sim = len(collisions)
        n_collisions = np.sum(collisions)
        
        result = {
            "scenario_id": self.scenario.id,
            "n_samples": n_sim,
            "n_collisions": int(n_collisions),
            "collision_rate": n_collisions / n_sim,
            "collision_rate_ci95": self._ci_binomial(n_collisions, n_sim),
        }
        
        # Per-indicator statistics (excluding NaN)
        for ind_name, ind_values in indicators.items():
            valid = ind_values[~np.isnan(ind_values)]
            if len(valid) > 0:
                result[f"{ind_name}_mean"] = np.mean(valid)
                result[f"{ind_name}_median"] = np.median(valid)
                result[f"{ind_name}_p5"] = np.percentile(valid, 5)
                result[f"{ind_name}_p25"] = np.percentile(valid, 25)
                result[f"{ind_name}_p75"] = np.percentile(valid, 75)
                result[f"{ind_name}_p95"] = np.percentile(valid, 95)
                result[f"{ind_name}_min"] = np.min(valid)
                result[f"{ind_name}_max"] = np.max(valid)
        
        return result
    
    def _ci_binomial(self, successes: int, trials: int, confidence: float = 0.95) -> tuple:
        """Wilson score interval for binomial proportion."""
        p = successes / trials
        z = stats.norm.ppf((1 + confidence) / 2)
        denom = 1 + z**2 / trials
        center = (p + z**2 / (2 * trials)) / denom
        margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * trials)) / trials) / denom
        return (max(0, center - margin), min(1, center + margin))
```

### 3.2 Adaptive Sample Size

```python
class AdaptiveMonteCarloEngine(MonteCarloEngine):
    """Monte Carlo engine with adaptive sample sizing based on convergence."""
    
    def __init__(self, scenario, n_init: int = 1000, n_step: int = 500, n_max: int = 50000):
        super().__init__(scenario, n_init)
        self.n_init = n_init
        self.n_step = n_step
        self.n_max = n_max
        self.convergence_threshold = 0.02  # 2% CI width
        
    def run_adaptive(self) -> dict:
        """Run until convergence or max samples reached."""
        n = self.n_init
        prev_collision_rate = None
        
        while n <= self.n_max:
            # Run batch
            result = self.run()
            
            # Check convergence
            ci_width = result["collision_rate_ci95"][1] - result["collision_rate_ci95"][0]
            
            if prev_collision_rate is not None and ci_width < self.convergence_threshold:
                # Converged! Use all data up to here
                break
            
            prev_collision_rate = result["collision_rate"]
            n += self.n_step
            self.n_samples = n
        
        return self._aggregate_results(
            np.random.binomial(1, result["collision_rate"], n),
            {}  # indicators from last batch
        )
```

## 4. Scenario-Specific Monte Carlo Configurations

### 4.1 Rear-End Cut-in Scenario

```python
REA_END_CUTIN_PARAMS = {
    "speed_lead": {"dist": "normal", "mu": 22.2, "sigma": 3.0, "min": 11.1, "max": 33.3},
    "speed_follow": {"dist": "normal", "mu": 27.8, "sigma": 3.5, "min": 16.7, "max": 38.9},
    "cut_in_distance": {"dist": "lognorm", "mu_log": 3.0, "sigma_log": 0.4},
    "reaction_time": {"dist": "lognorm", "mu_log": 0.7, "sigma_log": 0.3},
    "braking_delay": {"dist": "lognorm", "mu_log": -0.5, "sigma_log": 0.2},
    "friction": {"dist": "normal", "mu": 0.80, "sigma": 0.05},
}
```

### 4.2 Intersection Crossing Scenario

```python
INTERSECTION_CROSSING_PARAMS = {
    "speed_north": {"dist": "normal", "mu": 16.7, "sigma": 3.0, "min": 8.3, "max": 27.8},
    "speed_east": {"dist": "normal", "mu": 13.9, "sigma": 2.5, "min": 5.6, "max": 22.2},
    "red_light_rate": {"dist": "beta", "alpha": 1, "beta": 100},  # rare event, ~1%
    "running_green_rate": {"dist": "beta", "alpha": 1, "beta": 50},  # ~2%
    "reaction_time": {"dist": "lognorm", "mu_log": 0.7, "sigma_log": 0.3},
    "friction": {"dist": "normal", "mu": 0.80, "sigma": 0.05},
}
```

## 5. Uncertainty Quantification

### 5.1 Confidence Intervals

```python
def compute_ci(proportions: np.ndarray, ci_level: float = 0.95) -> tuple:
    """Bootstrap confidence interval for collision rate."""
    n_bootstraps = 10000
    boot_rates = np.array([
        np.mean(np.random.choice(proportions, size=len(proportions), replace=True))
        for _ in range(n_bootstraps)
    ])
    lower = np.percentile(boot_rates, (1 - ci_level) / 2 * 100)
    upper = np.percentile(boot_rates, (1 + ci_level) / 2 * 100)
    return (lower, upper)
```

### 5.2 Sobol Sensitivity Analysis

```python
# For understanding which parameters matter most
def sobol_sensitivity(scenario, n_samples: int = 10000):
    """Compute Sobol indices to identify most influential parameters."""
    from SALib import problem_spec, analyze
    
    # Define parameter ranges
    problem = {
        'num_vars': len(scenario.param_ranges),
        'names': list(scenario.param_ranges.keys()),
        'bounds': [[r[0], r[1]] for r in scenario.param_ranges.values()]
    }
    
    # Generate Sobol sequences
    param_values = saltelli.sample(problem, n_samples)
    
    # Run simulation for each sample
    outputs = np.array([
        simulate_scenario(scenario, params) for params in param_values
    ])
    
    # Compute Sobol indices
    Si = analyze(problem, outputs, print_to_console=True)
    return Si['S1'], Si['ST']  # First-order and total-effect indices
```

## 6. File Structure

```
src/simulation/
├── __init__.py
├── engine.py           — Monte Carlo engine
├── adaptive_engine.py  — Adaptive sample sizing
├── parameter_sampler.py — Parameter distribution sampling
├── convergence.py      — Convergence detection
├── sensitivity.py      — Sobol sensitivity analysis
├── scenarios/
│   ├── __init__.py
│   ├── config/         — Scenario-specific parameter configs
│   │   ├── rear_end_cutin.py
│   │   ├── intersection_crossing.py
│   │   └── ...
│   └── validation.py   — Validate simulation outputs
└── results/
    └── __init__.py
    ├── aggregation.py  — Monte Carlo aggregation
    ├── statistics.py   — Statistical summaries
    └── export.py       — Export results (JSON, CSV)
```

## 7. Validation Requirements

### 7.1 Convergence Testing
Each Monte Carlo run must verify:
- **Sample size adequacy:** CI width < threshold (default 2%)
- **Stability:** Repeated runs with same seed produce same results
- **Distribution fit:** Check that sampled parameters match target distributions

### 7.2 Benchmark Comparisons
- Compare collision rates against published crash data
- Validate indicator values against NHTSA/BANSYSE benchmarks
- Cross-validate with independent simulation tools

### 7.3 Reproducibility
- All random seeds must be logged
- Parameter distributions must be fully documented
- Simulation parameters must be stored with results
