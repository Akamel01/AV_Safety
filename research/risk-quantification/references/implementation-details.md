# Risk Quantification Implementation Details

## Main Pipeline Class

```python
class RiskQuantificationPipeline:
    def __init__(self, scenarios: list, n_mc_samples: int = 10000):
        self.scenarios = scenarios
        self.n_mc_samples = n_mc_samples
        self.results = {}
    
    def run_pipeline(self) -> dict:
        for scenario in self.scenarios:
            # Step 1: Kinematics
            trajectories = self._run_kinematics(scenario)
            # Step 2: Indicators
            indicators = self._compute_indicators(trajectories)
            # Step 3: Monte Carlo
            mc_results = self._run_monte_carlo(scenario, n=self.n_mc_samples)
            # Step 4: Bayesian EVT
            bayesian_results = self._fit_bayesian_evt(mc_results)
            # Step 5: Collision Modeling
            collision_results = self._predict_collisions(indicators)
            # Step 6: Safety Thresholds
            threshold_results = self._check_thresholds(mc_results, bayesian_results)
            # Step 7: Aggregate
            self.results[scenario.scenario_id] = {
                "scenario": scenario.to_dict(),
                "trajectories": trajectories,
                "indicators": indicators,
                "monte_carlo": mc_results,
                "bayesian_evt": bayesian_results,
                "collision_model": collision_results,
                "thresholds": threshold_results,
                "overall_risk": self._compute_overall_risk(...)
            }
        return self.results
    
    def _run_kinematics(self, scenario):
        from src.kinematics import KinematicsEngine
        return KinematicsEngine(scenario).simulate(dt=0.01)
    
    def _compute_indicators(self, trajectories):
        from src.indicators import IndicatorManager
        return IndicatorManager().compute_all(trajectories)
    
    def _run_monte_carlo(self, scenario, n):
        from src.stochastic_simulation import MonteCarloEngine
        return MonteCarloEngine(scenario, n_samples=n).run()
    
    def _fit_bayesian_evt(self, mc_results):
        from src.bayesian_evt import BayesianEVTModel
        return BayesianEVTModel(mc_results).fit_and_predict()
    
    def _predict_collisions(self, indicators):
        from src.collision_modeling import CollisionModelEnsemble
        return CollisionModelEnsemble().predict(indicators)
    
    def _check_thresholds(self, mc_results, bayesian_results):
        from src.safety_thresholds import SafeThresholdChecker
        return SafeThresholdChecker(mc_results["collision_rate"]).evaluate(bayesian_results)
    
    def _compute_overall_risk(self, mc_results, bayesian_results, collision_results, threshold_results):
        weights = {
            "collision_rate": 0.3, "severity": 0.3,
            "uncertainty": 0.2, "threshold_compliance": 0.2
        }
        risk_score = (
            weights["collision_rate"] * mc_results["collision_rate"] +
            weights["severity"] * bayesian_results["severity_score"] +
            weights["uncertainty"] * (1 - bayesian_results["confidence"]) +
            weights["threshold_compliance"] * (1 - threshold_results["margin_percent"])
        )
        return {
            "overall_risk_score": risk_score,
            "risk_level": self._classify_risk(risk_score),
            "recommendation": self._get_recommendation(threshold_results),
            "confidence": bayesian_results["confidence"]
        }
```

## Batch Runner

```python
class BatchRunner:
    def __init__(self, scenarios: list, n_workers: int = 4):
        self.scenarios = scenarios
        self.n_workers = n_workers
    
    def run_all_scenarios(self) -> dict:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        results = {}
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            futures = {
                executor.submit(self._run_scenario, scenario): scenario.scenario_id
                for scenario in self.scenarios
            }
            for future in as_completed(futures):
                scenario_id = futures[future]
                try: results[scenario_id] = future.result()
                except Exception as e: results[scenario_id] = {"error": str(e)}
        return results
    
    def _run_scenario(self, scenario) -> dict:
        pipeline = RiskQuantificationPipeline([scenario])
        return pipeline.run_pipeline()[scenario.scenario_id]
```

## Risk Report Generation

```python
def generate_risk_report(results: dict, scenarios: list) -> str:
    n_scenarios = len(results)
    collision_rates = [r["monte_carlo"]["collision_rate"] for r in results.values()]
    severity_scores = [r["bayesian_evt"]["severity_score"] for r in results.values()]
    avg_collision_rate = np.mean(collision_rates)
    avg_severity = np.mean(severity_scores)
    
    risk_level = "LOW" if avg_collision_rate < 0.001 and avg_severity < 0.3 else \
                 "MEDIUM" if avg_collision_rate < 0.01 and avg_severity < 0.7 else \
                 "HIGH" if avg_collision_rate < 0.05 else \
                 "CRITICAL"
    
    report = f"""# Collision Risk Quantification Report
## 1. Executive Summary
- **Total scenarios analyzed:** {n_scenarios}
- **Average collision rate:** {avg_collision_rate:.4f}
- **Average severity:** {avg_severity:.2f}
- **Overall risk level:** {risk_level}
"""
    # ... full markdown with all 8 sections
    return report
```

## Threshold Compliance Checker

```python
class ThresholdComplianceChecker:
    def check_compliance(self, results: dict, jurisdiction: str) -> dict:
        thresholds = THRESHOLDS[jurisdiction]
        compliance = {}
        for scenario_id, result in results.items():
            collision_rate = result["monte_carlo"]["collision_rate"]
            safety_margin = thresholds.safety_margin(collision_rate)
            compliance[scenario_id] = {
                "meets_threshold": collision_rate < thresholds.deployment_threshold,
                "safety_margin_percent": safety_margin,
                "compliance_level": "FULL" if collision_rate < thresholds.safe_threshold else
                                   "CONDITIONAL" if collision_rate < thresholds.deployment_threshold else
                                   "NON_COMPLIANT",
                "required_improvement": max(0, (collision_rate - thresholds.safe_threshold) / collision_rate * 100)
            }
        return compliance
```

## Output Formats

### JSON Export
```python
def export_results_json(results: dict, output_path: str):
    export_data = {}
    for scenario_id, result in results.items():
        export_data[scenario_id] = {
            "scenario": result["scenario"],
            "monte_carlo": {
                "collision_rate": result["monte_carlo"]["collision_rate"],
                "n_collisions": result["monte_carlo"]["n_collisions"],
                "n_samples": result["monte_carlo"]["n_samples"],
                "ci95": result["monte_carlo"]["collision_rate_ci95"]
            },
            "bayesian_evt": {
                "gpd_params": result["bayesian_evt"]["gpd_params"],
                "threshold": result["bayesian_evt"]["threshold"],
                "severity_gpd": result["bayesian_evt"]["severity_gpd"]
            },
            "thresholds": result["thresholds"]
        }
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)
```

### CSV Export
```python
def export_results_csv(results: dict, output_path: str):
    rows = []
    for scenario_id, result in results.items():
        rows.append({
            "scenario_id": scenario_id,
            "conflict_type": result["scenario"]["conflict_type"],
            "jurisdiction": result["scenario"]["jurisdiction"],
            "collision_rate": result["monte_carlo"]["collision_rate"],
            "n_collisions": result["monte_carlo"]["n_collisions"],
            "severity_mean": result["bayesian_evt"]["severity_mean"],
            "safety_margin": result["thresholds"]["safety_margin_percent"],
            "compliance": result["thresholds"]["compliance_level"]
        })
    pd.DataFrame(rows).to_csv(output_path, index=False)
```

## Pipeline Validation

### Step Execution Log
Each step logs: start time, end time, records processed, warnings

### No NaN Check
```python
def validate_no_nan(results: dict):
    for scenario_id, result in results.items():
        for key, value in result.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, (int, float)) and (np.isnan(v) or np.isinf(v)):
                        raise ValueError(f"NaN/Inf in {scenario_id}.{key}.{k}")
```

### Reproducibility Check
```python
def validate_reproducibility(pipeline, scenarios, seed=42):
    np.random.seed(seed)
    result1 = pipeline.run_pipeline()
    np.random.seed(seed)
    result2 = pipeline.run_pipeline()
    assert result1 == result2, "Pipeline not reproducible"
```
