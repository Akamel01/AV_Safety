# Skill: Risk Quantification

**Purpose:** End-to-end risk quantification pipeline integrating all previous skills: collision modeling, Bayesian EVT, safety thresholds, and portfolio visualization.

## 1. Pipeline Architecture

### 1.1 Complete Pipeline Flow

```
Scenarios
    │
    ▼
┌──────────────┐
│ Kinematics   │  Trajectory computation
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Indicators   │  42 computed indicators
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Stochastic   │  Monte Carlo simulation
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Bayesian EVT │  GPD fitting + posterior
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Collision    │  ML prediction + uncertainty
│ Modeling     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Safety       │  Threshold comparison
│ Thresholds   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Portfolio    │  UI + visualization
└──────────────┘
```

### 1.2 File Structure

```
src/risk_quantification/
├── __init__.py
├── pipeline.py              — Main pipeline orchestrator
├── scenario_runner.py       — Run individual scenarios
├── batch_runner.py          — Run all scenarios
├── results_aggregator.py    — Aggregate results
├── risk_report_generator.py — Generate risk reports
├── threshold_checker.py     — Compare against safety thresholds
├── output_formats/
│   ├── json_export.py       — Export to JSON
│   ├── csv_export.py        — Export to CSV
│   └── markdown_report.py   — Generate markdown report
└── validation/
    └── pipeline_validation.py — Validate pipeline outputs
```

## 2. Pipeline Implementation

### 2.1 Main Pipeline Class

```python
class RiskQuantificationPipeline:
    def __init__(self, scenarios: list, n_mc_samples: int = 10000):
        self.scenarios = scenarios
        self.n_mc_samples = n_mc_samples
        self.results = {}
        
    def run_pipeline(self) -> dict:
        """Execute complete risk quantification pipeline."""
        
        for scenario in self.scenarios:
            print(f"Processing: {scenario.scenario_id}")
            
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
                "overall_risk": self._compute_overall_risk(
                    mc_results, bayesian_results, collision_results, threshold_results
                )
            }
        
        return self.results
    
    def _run_kinematics(self, scenario: Scenario) -> dict:
        """Run kinematic simulation."""
        from src.kinematics import KinematicsEngine
        
        engine = KinematicsEngine(scenario)
        return engine.simulate(dt=0.01)
    
    def _compute_indicators(self, trajectories: dict) -> dict:
        """Compute all 42 indicators."""
        from src.indicators import IndicatorManager
        
        manager = IndicatorManager()
        return manager.compute_all(trajectories)
    
    def _run_monte_carlo(self, scenario: Scenario, n: int) -> dict:
        """Run Monte Carlo simulation."""
        from src.stochastic_simulation import MonteCarloEngine
        
        engine = MonteCarloEngine(scenario, n_samples=n)
        return engine.run()
    
    def _fit_bayesian_evt(self, mc_results: dict) -> dict:
        """Fit Bayesian EVT to Monte Carlo results."""
        from src.bayesian_evt import BayesianEVTModel
        
        model = BayesianEVTModel(mc_results)
        return model.fit_and_predict()
    
    def _predict_collisions(self, indicators: dict) -> dict:
        """Predict collision risk using ML models."""
        from src.collision_modeling import CollisionModelEnsemble
        
        ensemble = CollisionModelEnsemble()
        return ensemble.predict(indicators)
    
    def _check_thresholds(self, mc_results: dict, bayesian_results: dict) -> dict:
        """Check results against safety thresholds."""
        from src.safety_thresholds import SafeThresholdChecker
        
        checker = SafeThresholdChecker(mc_results["collision_rate"])
        return checker.evaluate(bayesian_results)
    
    def _compute_overall_risk(self, mc_results: dict, bayesian_results: dict,
                             collision_results: dict, threshold_results: dict) -> dict:
        """Compute overall risk score."""
        
        # Weighted risk score
        weights = {
            "collision_rate": 0.3,
            "severity": 0.3,
            "uncertainty": 0.2,
            "threshold_compliance": 0.2
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

### 2.2 Batch Processing

```python
class BatchRunner:
    def __init__(self, scenarios: list, n_workers: int = 4):
        self.scenarios = scenarios
        self.n_workers = n_workers
    
    def run_all_scenarios(self) -> dict:
        """Run pipeline for all scenarios in parallel."""
        
        from concurrent.futures import ProcessPoolExecutor
        
        results = {}
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            futures = {
                executor.submit(self._run_scenario, scenario): scenario.scenario_id
                for scenario in self.scenarios
            }
            
            for future in as_completed(futures):
                scenario_id = futures[future]
                try:
                    results[scenario_id] = future.result()
                except Exception as e:
                    results[scenario_id] = {"error": str(e)}
        
        return results
    
    def _run_scenario(self, scenario: Scenario) -> dict:
        """Run pipeline for single scenario."""
        pipeline = RiskQuantificationPipeline([scenario])
        return pipeline.run_pipeline()[scenario.scenario_id]
```

## 3. Risk Report Generation

### 3.1 Report Structure

```markdown
# Collision Risk Quantification Report

## 1. Executive Summary
- **Total scenarios analyzed:** {n_scenarios}
- **Overall risk level:** {risk_level}
- **Deployment recommendation:** {recommendation}
- **Key finding:** {summary}

## 2. Methodology
- **Kinematic model:** {model_type}
- **Simulation method:** Monte Carlo ({n_samples} runs)
- **Bayesian model:** Hierarchical EVT with GPD
- **ML models:** {models_used}
- **Safety thresholds:** {thresholds_used}

## 3. Scenario Results
### 3.1 {scenario_name}
- **Collision rate:** {rate} (95% CI: {ci})
- **Average severity:** {severity}
- **Expected fatalities:** {expected_fatalities}
- **TTC distribution:** {ttc_stats}
- **DRAC distribution:** {drac_stats}
- **Bayesian GPD fit:** ξ={xi}, σ={sigma}
- **Safety margin:** {margin}%
- **Compliance:** {compliance_status}

### 3.2 {next_scenario}
...

## 4. Cross-Scenario Analysis
### 4.1 Conflict Type Comparison
{conflict_type_comparison}

### 4.2 Jurisdiction Comparison
{jurisdiction_comparison}

### 4.3 Severity Distribution
{severity_distribution}

## 5. Threshold Analysis
### 5.1 Safe Thresholds
{safe_thresholds}

### 5.2 Deployment Readiness
{deployment_readiness}

## 6. Recommendations
1. {recommendation_1}
2. {recommendation_2}
3. {recommendation_3}

## 7. Uncertainty Analysis
- **Primary uncertainty source:** {primary_uncertainty}
- **Confidence level:** {confidence}%
- **Sensitivity:** {sensitivity_analysis}

## 8. Appendices
- A. Parameter specifications
- B. Model validation results
- C. Data sources and quality
- D. Computational details
```

### 3.2 Report Generation Function

```python
def generate_risk_report(results: dict, scenarios: list) -> str:
    """Generate comprehensive risk quantification report."""
    
    # Aggregate results
    n_scenarios = len(results)
    collision_rates = [r["monte_carlo"]["collision_rate"] for r in results.values()]
    severity_scores = [r["bayesian_evt"]["severity_score"] for r in results.values()]
    
    # Classify overall risk
    avg_collision_rate = np.mean(collision_rates)
    avg_severity = np.mean(severity_scores)
    
    risk_level = "LOW" if avg_collision_rate < 0.001 and avg_severity < 0.3 else \
                 "MEDIUM" if avg_collision_rate < 0.01 and avg_severity < 0.7 else \
                 "HIGH" if avg_collision_rate < 0.05 else \
                 "CRITICAL"
    
    # Generate markdown
    report = f"""# Collision Risk Quantification Report
## 1. Executive Summary
- **Total scenarios analyzed:** {n_scenarios}
- **Average collision rate:** {avg_collision_rate:.4f}
- **Average severity:** {avg_severity:.2f}
- **Overall risk level:** {risk_level}
"""
    
    return report
```

## 4. Threshold Compliance

### 4.1 Compliance Checker

```python
class ThresholdComplianceChecker:
    def check_compliance(self, results: dict, jurisdiction: str) -> dict:
        """Check all scenario results against safety thresholds."""
        
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

## 5. Output Formats

### 5.1 JSON Export

```python
def export_results_json(results: dict, output_path: str):
    """Export results to JSON."""
    
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

### 5.2 CSV Export

```python
def export_results_csv(results: dict, output_path: str):
    """Export results to CSV for spreadsheet analysis."""
    
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

## 6. Validation Requirements

### 6.1 Pipeline Validation

| Check | Method | Pass Condition |
|---|-|-|
| **All steps complete** | Step execution log | 100% completion |
| **No NaN outputs** | Value check | No NaN in results |
| **Convergence achieved** | R-hat, ESS | R-hat < 1.01, ESS > 400 |
| **Threshold compliance** | Comparison | All scenarios evaluated |
| **Reproducibility** | Seed testing | Same results with same seed |

### 6.2 Result Quality

- **Minimum scenarios:** ≥ 16 (2 per conflict type)
- **Minimum Monte Carlo samples:** ≥ 10,000 per scenario
- **Bayesian convergence:** R-hat < 1.01, ESS > 400
- **Statistical power:** ≥ 0.80 for significance tests
- **Uncertainty bounds:** 95% CI reported for all estimates
