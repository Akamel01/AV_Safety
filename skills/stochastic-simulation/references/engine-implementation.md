# Detailed Monte Carlo Engine Implementation

## Parameter Sampler

```python
from scipy.stats import norm, lognorm, expon, gamma, beta

def sample_speed(dist_name, n=1):
    SPEED_DISTRIBUTIONS = {
        "urban_car": {"mu": 11.2, "sigma": 3.1, "min": 0, "max": 33.3},
        "urban_suv": {"mu": 12.0, "sigma": 3.5, "min": 0, "max": 33.3},
        "urban_truck": {"mu": 10.5, "sigma": 2.8, "min": 0, "max": 27.8},
        "urban_pedestrian": {"mu": 1.4, "sigma": 0.4, "min": 0, "max": 3.5},
        "urban_cyclist": {"mu": 5.0, "sigma": 1.5, "min": 0, "max": 15.0},
        "highway_car": {"mu": 27.8, "sigma": 4.2, "min": 15.6, "max": 41.7},
        "highway_suv": {"mu": 28.5, "sigma": 4.5, "min": 15.6, "max": 41.7},
        "highway_truck": {"mu": 24.0, "sigma": 3.8, "min": 13.9, "max": 36.1},
        "freeway_car": {"mu": 30.6, "sigma": 4.8, "min": 22.2, "max": 44.4},
    }
    dist = SPEED_DISTRIBUTIONS[dist_name]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))

def sample_reaction_time(condition="normal", n=1):
    REACTION_TIME_PARAMS = {
        "normal": {"mu_log": 0.7, "sigma_log": 0.3},
        "alert": {"mu_log": 0.5, "sigma_log": 0.2},
        "distracted": {"mu_log": 0.9, "sigma_log": 0.4},
        "elderly": {"mu_log": 1.0, "sigma_log": 0.35},
        "exhausted": {"mu_log": 1.1, "sigma_log": 0.45},
    }
    params = REACTION_TIME_PARAMS[condition]
    return max(0.1, min(lognorm.rvs(params["sigma_log"], scale=np.exp(params["mu_log"]), size=n), 5.0))

def sample_braking_delay(condition="standard", n=1):
    BRAKING_DELAY_PARAMS = {
        "standard": {"mu_log": -0.5, "sigma_log": 0.2},
        "panic": {"mu_log": -0.3, "sigma_log": 0.15},
        "slow": {"mu_log": 0.0, "sigma_log": 0.3},
    }
    params = BRAKING_DELAY_PARAMS[condition]
    return max(0.05, min(lognorm.rvs(params["sigma_log"], scale=np.exp(params["mu_log"]), size=n), 2.0))

def sample_friction(condition="dry_asphalt", n=1):
    FRICTION_DISTRIBUTIONS = {
        "dry_asphalt": {"mu": 0.80, "sigma": 0.05, "min": 0.6, "max": 0.95},
        "wet_asphalt": {"mu": 0.45, "sigma": 0.08, "min": 0.3, "max": 0.6},
        "snow": {"mu": 0.20, "sigma": 0.08, "min": 0.1, "max": 0.35},
        "ice": {"mu": 0.10, "sigma": 0.05, "min": 0.05, "max": 0.20},
        "gravel": {"mu": 0.55, "sigma": 0.10, "min": 0.4, "max": 0.75},
    }
    dist = FRICTION_DISTRIBUTIONS[condition]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))

def sample_cutin_distance(behavior="normal", n=1):
    CUTIN_DISTRIBUTIONS = {
        "aggressive": {"mu": 10, "sigma": 3, "min": 5, "max": 20},
        "normal": {"mu": 25, "sigma": 8, "min": 10, "max": 50},
        "conservative": {"mu": 40, "sigma": 10, "min": 20, "max": 70},
    }
    dist = CUTIN_DISTRIBUTIONS[behavior]
    return max(dist["min"], min(norm.rvs(dist["mu"], dist["sigma"], size=n), dist["max"]))
```

## Scenario-Specific Configs

### Rear-End Cut-in
```python
REAR_END_CUTIN_PARAMS = {
    "speed_lead": {"dist": "normal", "mu": 22.2, "sigma": 3.0, "min": 11.1, "max": 33.3},
    "speed_follow": {"dist": "normal", "mu": 27.8, "sigma": 3.5, "min": 16.7, "max": 38.9},
    "cut_in_distance": {"dist": "lognorm", "mu_log": 3.0, "sigma_log": 0.4},
    "reaction_time": {"dist": "lognorm", "mu_log": 0.7, "sigma_log": 0.3},
    "braking_delay": {"dist": "lognorm", "mu_log": -0.5, "sigma_log": 0.2},
    "friction": {"dist": "normal", "mu": 0.80, "sigma": 0.05},
}
```

### Intersection Crossing
```python
INTERSECTION_CROSSING_PARAMS = {
    "speed_north": {"dist": "normal", "mu": 16.7, "sigma": 3.0, "min": 8.3, "max": 27.8},
    "speed_east": {"dist": "normal", "mu": 13.9, "sigma": 2.5, "min": 5.6, "max": 22.2},
    "red_light_rate": {"dist": "beta", "alpha": 1, "beta": 100},  # ~1%
    "running_green_rate": {"dist": "beta", "alpha": 1, "beta": 50},  # ~2%
    "reaction_time": {"dist": "lognorm", "mu_log": 0.7, "sigma_log": 0.3},
    "friction": {"dist": "normal", "mu": 0.80, "sigma": 0.05},
}
```

## Adaptive Monte Carlo Engine

```python
class AdaptiveMonteCarloEngine(MonteCarloEngine):
    def __init__(self, scenario, n_init=1000, n_step=500, n_max=50000):
        super().__init__(scenario, n_init)
        self.n_step = n_step
        self.n_max = n_max
        self.convergence_threshold = 0.02  # 2% CI width
    
    def run_adaptive(self) -> dict:
        n = self.n_init
        prev_rate = None
        while n <= self.n_max:
            result = self.run()
            ci_width = result["collision_rate_ci95"][1] - result["collision_rate_ci95"][0]
            if prev_rate is not None and ci_width < self.convergence_threshold:
                break
            prev_rate = result["collision_rate"]
            n += self.n_step
            self.n_samples = n
        return result
```

## Sobol Sensitivity Analysis

```python
from SALib import problem_spec, analyze

def sobol_sensitivity(scenario, n_samples=10000):
    problem = {
        'num_vars': len(scenario.param_ranges),
        'names': list(scenario.param_ranges.keys()),
        'bounds': [[r[0], r[1]] for r in scenario.param_ranges.values()]
    }
    param_values = saltelli.sample(problem, n_samples)
    outputs = np.array([simulate_scenario(scenario, params) for params in param_values])
    Si = analyze(problem, outputs, print_to_console=True)
    return Si['S1'], Si['ST']  # First-order and total-effect indices
```

## Uncertainty Quantification

### Bootstrap CI
```python
def compute_ci(proportions, ci_level=0.95):
    n_bootstraps = 10000
    boot_rates = np.array([
        np.mean(np.random.choice(proportions, size=len(proportions), replace=True))
        for _ in range(n_bootstraps)
    ])
    lower = np.percentile(boot_rates, (1 - ci_level) / 2 * 100)
    upper = np.percentile(boot_rates, (1 + ci_level) / 2 * 100)
    return (lower, upper)
```
