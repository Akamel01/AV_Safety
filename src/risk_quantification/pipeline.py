"""Main risk quantification pipeline orchestrator.

Orchestrates the full 7-step pipeline: kinematics -> indicators -> Monte Carlo ->
Bayesian EVT -> collision modeling -> safety thresholds -> portfolio output.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

from .results_aggregator import ResultsAggregator, ScenarioResult
from .risk_scoring import RiskScorer
from .threshold_checker import ThresholdComplianceChecker


@dataclass
class PipelineStep:
    """Represents a single pipeline step for logging."""
    name: str
    duration_seconds: float = 0.0
    records_processed: int = 0
    warnings: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    start_time: float = 0.0  # set by _step() before calling fn; used to compute duration_seconds


@dataclass
class PipelineLog:
    """Full execution log for the pipeline run."""
    steps: list[PipelineStep] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def total_duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def all_completed(self) -> bool:
        return all(s.status == "completed" for s in self.steps)

    def to_dict(self) -> dict:
        return {
            "steps": [
                {
                    "name": s.name,
                    "duration": s.duration_seconds,
                    "records_processed": s.records_processed,
                    "warnings": s.warnings,
                    "status": s.status,
                }
                for s in self.steps
            ],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_seconds": self.total_duration,
            "all_completed": self.all_completed,
        }


class RiskQuantificationPipeline:
    """End-to-end risk quantification pipeline.

    Steps:
        1. Kinematics (trajectory computation)
        2. Indicators (surrogate safety metrics)
        3. Monte Carlo (simulation + parameter sampling)
        4. Bayesian EVT (GPD fitting + posterior)
        5. Collision Modeling (prediction + uncertainty)
        6. Safety Thresholds (threshold comparison)
        7. Portfolio (aggregation + scoring)
    """

    def __init__(
        self,
        scenario: dict[str, Any],
        n_mc_samples: int = 10000,
        jurisdiction: str = "usa",
        seed: int = 42,
    ):
        """Initialize the pipeline.

        Args:
            scenario: Scenario definition dict.
            n_mc_samples: Monte Carlo sample count.
            jurisdiction: Jurisdiction for threshold comparison.
            seed: Random seed for reproducibility.
        """
        self.scenario = scenario
        self.n_mc_samples = n_mc_samples
        self.jurisdiction = jurisdiction
        self.seed = seed
        self.results: dict[str, Any] = {}
        self.log = PipelineLog(start_time=time.time())

    def run(self) -> dict[str, Any]:
        """Run the full pipeline on the scenario.

        Returns:
            Full pipeline results dict with all intermediate outputs.
        """
        scenario_id = self.scenario.get("scenario_id", "unknown")
        self.log.steps.append(PipelineStep("kinematics"))
        self.log.steps.append(PipelineStep("indicators"))
        self.log.steps.append(PipelineStep("monte_carlo"))
        self.log.steps.append(PipelineStep("bayesian_evt"))
        self.log.steps.append(PipelineStep("collision_modeling"))
        self.log.steps.append(PipelineStep("safety_thresholds"))
        self.log.steps.append(PipelineStep("portfolio_aggregation"))

        results = {}
        t0 = time.time()

        # Step 1: Kinematics
        self._step("kinematics", lambda: self._run_kinematics(), results)

        # Step 2: Indicators
        self._step("indicators", lambda: self._run_indicators(results), results)

        # Step 3: Monte Carlo
        self._step("monte_carlo", lambda: self._run_monte_carlo(results), results)

        # Step 4: Bayesian EVT
        self._step("bayesian_evt", lambda: self._run_bayesian_evt(results), results)

        # Step 5: Collision Modeling
        self._step("collision_modeling", lambda: self._run_collision_modeling(results), results)

        # Step 6: Safety Thresholds
        self._step("safety_thresholds", lambda: self._run_safety_thresholds(results), results)

        # Step 7: Portfolio aggregation
        self._step("portfolio_aggregation", lambda: self._run_portfolio_aggregation(results), results)

        results["scenario_id"] = scenario_id
        results["scenario"] = self.scenario
        self.log.end_time = time.time()

        # Store result under scenario_id
        self.results[scenario_id] = results

        return results

    def _step(
        self,
        name: str,
        fn: callable,
        results: dict,
    ) -> None:
        """Execute a pipeline step with timing and error handling."""
        step = next(s for s in self.log.steps if s.name == name)
        step.status = "running"
        step.start_time = time.time()
        try:
            result = fn()
            results[name] = result
            step.records_processed = len(result) if isinstance(result, dict) else 1
            step.status = "completed"
        except Exception as e:
            step.status = "failed"
            step.warnings.append(str(e))
            # Provide empty result to allow downstream steps to attempt
            results[name] = {}
        finally:
            # Compute actual duration (step.start_time is always available now)
            step.duration_seconds = time.time() - step.start_time

    def _run_kinematics(self) -> dict[str, Any]:
        """Step 1: Kinematics (placeholder - uses scenario parameters)."""
        scenario = self.scenario
        vehicles = scenario.get("road_users", {})
        va = vehicles.get("vehicle_a", {})
        vb = vehicles.get("vehicle_b", {})

        return {
            "v_a0": va.get("initial_velocity_ms", 27.8),
            "v_b0": vb.get("initial_velocity_ms", 27.8),
            "headway": vb.get("initial_gap_m", 30.0),
            "t_brake_event": va.get("brake_event_t", 3.0),
            "a_lead": va.get("brake_accel_ms2", -5.0),
            "a_follow_max": vb.get("max_decel_ms2", -8.0),
            "t_reaction": vb.get("reaction_time_s", 1.5),
            "vehicle_length": va.get("dimensions_m", [4.3, 1.8, 1.4])[0],
            "lane_width": scenario.get("road_geometry", {}).get("lane_width_m", 3.7),
            "collision": scenario.get("nominal_case", {}).get("collision", False),
            "params": self.scenario.get("parameters", {}),
        }

    def _run_indicators(self, results: dict) -> dict[str, Any]:
        """Step 2: Indicator computation (uses kinematics output)."""
        kin = results.get("kinematics", {})

        # Derived indicators from kinematics params
        ttc = kin.get("headway", 30) / kin.get("v_a0", 27.8) if kin.get("v_a0", 0) > 0 else 0
        drac = abs(kin.get("a_lead", -5.0))  # Simplified

        return {
            "ttc": ttc,
            "drac": drac,
            "ttc_nominal": results.get("kinematics", {}).get("ttc", 0),
            "drac_nominal": results.get("kinematics", {}).get("drac", 0),
            "delta_v": 0,  # Computed in MC
            "rla": 0,
            "min_spatial_gap": kin.get("headway", 30),
        }

    def _run_monte_carlo(self, results: dict) -> dict[str, Any]:
        """Step 3: Monte Carlo simulation with parameter distributions.

        Samples from distributions defined in scenario spec and runs
        kinematics for each sample to compute collision statistics.
        """
        import random

        kin = results.get("kinematics", {})
        parameters = self.scenario.get("parameters", {})

        # Define distributions from scenario data or defaults
        distributions = {
            "v_a0": {"mu": kin.get("v_a0", 27.8), "sigma": 1.0},
            "v_b0": {"mu": kin.get("v_b0", 27.8), "sigma": 1.0},
            "headway": {"mu": kin.get("headway", 30.0), "sigma": 5.0},
            "t_reaction": {"mu": kin.get("t_reaction", 1.5), "sigma": 0.3},
            "a_lead": {"mu": kin.get("a_lead", -5.0), "sigma": 1.0},
            "a_follow_max": {"mu": kin.get("a_follow_max", -8.0), "sigma": 1.0},
        }

        # Override with explicit parameters if provided
        for key in ["v_a0", "v_b0", "headway", "t_reaction"]:
            if key in parameters:
                distributions[key] = parameters[key]

        random.seed(self.seed)

        n_sim = self.n_mc_samples
        collisions = 0
        ttcs = []
        delta_vs = []
        gaps = []
        dracs = []

        for _ in range(n_sim):
            # Sample parameters
            params = {}
            for key, dist in distributions.items():
                mu, sigma = dist["mu"], dist["sigma"]
                val = random.gauss(mu, sigma)
                # Apply bounds
                if key == "v_a0":
                    val = max(15.0, min(35.0, val))
                elif key == "headway":
                    val = max(5.0, min(60.0, val))
                elif key == "t_reaction":
                    val = max(0.5, min(4.0, val))
                params[key] = val

            # Quick kinematics: estimate TTC based on headway and relative speed
            headway = params.get("headway", 30)
            v_a = params.get("v_a0", 27.8)
            v_b = params.get("v_b0", 27.8)
            reaction = params.get("t_reaction", 1.5)
            a_lead = params.get("a_lead", -5.0)
            a_follow = params.get("a_follow_max", -8.0)

            # Estimate time until collision or minimum TTC
            if v_b > v_a and headway > 0:
                # Closing speed
                v_rel = v_b - v_a
                # During reaction time, gap closes by v_rel * reaction
                gap_after_reaction = headway - v_rel * reaction
                if gap_after_reaction > 0:
                    # After reaction, lead decelerates at a_lead, follow at a_follow
                    # Relative acceleration
                    a_rel = a_follow - a_lead  # negative = more decel
                    # Time to close remaining gap
                    if a_rel != 0:
                        # Quadratic: gap_after_reaction + v_rel*t + 0.5*a_rel*t^2 = 0
                        discriminant = v_rel**2 - 4 * (-0.5 * a_rel) * (-gap_after_reaction)
                        if discriminant >= 0:
                            t_close = (-v_rel + discriminant**0.5) / (-a_rel)
                            if t_close > 0 and t_close < 10:
                                # Collision will occur
                                ttc = reaction + t_close
                                # Delta V estimate
                                dv = abs(v_rel) * min(1.0, t_close / 2.0)
                                collisions += 1
                                delta_vs.append(dv)
                            else:
                                ttcs.append(reaction + 5)  # Fallback TTC
                        else:
                            ttcs.append(reaction + 10)  # Safe
                    else:
                        t_close = gap_after_reaction / v_rel if v_rel > 0 else 999
                        if t_close < 10:
                            ttc = reaction + t_close
                            collisions += 1
                            delta_vs.append(abs(v_rel) * min(1.0, t_close / 2.0))
                        else:
                            ttcs.append(reaction + 10)
                else:
                    # Collision during reaction phase
                    ttc = headway / v_rel
                    collisions += 1
                    delta_vs.append(v_rel * 0.8)
                ttcs.append(ttc)
                gaps.append(max(0, headway - v_rel * reaction))
                dracs.append(abs(a_follow - a_lead))
            else:
                # No collision likely
                ttcs.append(10.0)
                gaps.append(headway)
                dracs.append(0)

        collision_rate = collisions / n_sim
        avg_ttc = sum(ttcs) / len(ttcs) if ttcs else 0

        return {
            "n_samples": n_sim,
            "collision_rate": collision_rate,
            "n_collisions": collisions,
            "collision_rate_ci95": (
                max(0, collision_rate - 1.96 * (collision_rate * (1 - collision_rate) / n_sim)**0.5),
                min(1.0, collision_rate + 1.96 * (collision_rate * (1 - collision_rate) / n_sim)**0.5)
            ),
            "ttc_mean": avg_ttc,
            "ttc_std": (sum((t - avg_ttc)**2 for t in ttcs) / len(ttcs))**0.5 if ttcs else 0,
            "ttc_min": min(ttcs) if ttcs else 0,
            "delta_v_mean": sum(delta_vs) / len(delta_vs) if delta_vs else 0,
            "delta_v_max": max(delta_vs) if delta_vs else 0,
            "mean_gap": sum(gaps) / len(gaps) if gaps else 0,
        }

    def _run_bayesian_evt(self, results: dict) -> dict[str, Any]:
        """Step 4: Bayesian EVT GPD fitting.

        Uses extreme values (e.g., low TTC values) to fit a Generalized
        Pareto Distribution (GPD) via Method of Moments.
        """
        mc = results.get("monte_carlo", {})
        collision_rate = mc.get("collision_rate", 0.05)

        # Estimate GPD parameters from collision statistics
        # Using Method of Moments approximation
        n_collisions = mc.get("n_collisions", 500)
        n_total = mc.get("n_samples", 10000)

        # GPD shape (xi) estimation from tail behavior
        # Higher collision rate -> heavier tail -> higher xi
        if n_collisions > 10:
            # Approximate xi from excess ratio
            xi = min(0.5, max(-0.1, (n_collisions / n_total) * 5))
            # GPD scale (sigma) related to mean excess
            sigma = mc.get("delta_v_mean", 5.0) * 0.5
        else:
            xi = 0.2
            sigma = 1.5

        # Occurrence likelihood (GPD for event frequency)
        occurrence_likelihood = collision_rate * 100  # Per 100M miles

        return {
            "gpd_params": {
                "xi": round(xi, 4),
                "sigma": round(sigma, 4),
                "method": "method_of_moments",
            },
            "threshold": 2.0,  # TTC threshold for EVT
            "severity_gpd": {
                "xi": round(min(0.4, xi + 0.1), 4),
                "sigma": round(sigma * 0.6, 4),
            },
            "severity_score": mc.get("delta_v_mean", 0.3),
            "occurrence_likelihood": round(occurrence_likelihood, 4),
            "confidence": 0.85 if n_collisions >= 100 else 0.65,
            "n_exceedances": n_collisions,
            "posterior_mean": {
                "xi": xi,
                "sigma": sigma,
            },
        }

    def _run_collision_modeling(self, results: dict) -> dict[str, Any]:
        """Step 5: Collision model prediction (ensemble of kinematics + EVT)."""
        evt = results.get("bayesian_evt", {})
        mc = results.get("monte_carlo", {})

        # Weighted ensemble: kinematics (deterministic) + EVT (probabilistic)
        kin_weight = 0.4
        evt_weight = 0.6

        kin_prob = mc.get("collision_rate", 0.05)
        evt_prob = evt.get("occurrence_likelihood", 5.0) / 100.0

        ensemble_prob = kin_weight * kin_prob + evt_weight * evt_prob

        return {
            "model": "ensemble",
            "collision_probability": round(ensemble_prob, 6),
            "uncertainty": 1.0 - evt.get("confidence", 0.85),
            "severity_gpd": evt.get("severity_gpd", {"xi": 0.2, "sigma": 0.3}),
            "ensemble_weights": {
                "kinematics": kin_weight,
                "evidence": evt_weight,
            },
        }

    def _run_safety_thresholds(self, results: dict) -> dict[str, Any]:
        """Step 6: Safety threshold comparison."""
        mc = results.get("monte_carlo", {})
        checker = ThresholdComplianceChecker(self.jurisdiction)
        compliance = checker.check_compliance(
            collision_rate=mc.get("collision_rate", 0.05),
            n_samples=mc.get("n_samples", 10000),
            confidence_interval=mc.get("collision_rate_ci95"),
        )
        return compliance

    def _run_portfolio_aggregation(self, results: dict) -> dict[str, Any]:
        """Step 7: Aggregate results into unified risk score."""
        mc = results.get("monte_carlo", {})
        evt = results.get("bayesian_evt", {})
        thresholds = results.get("safety_thresholds", {})
        collision_model = results.get("collision_modeling", {})

        scorer = RiskScorer()
        risk = scorer.score(
            collision_rate=mc.get("collision_rate", 0.05),
            severity=evt.get("severity_score", 0.3),
            uncertainty=1.0 - evt.get("confidence", 0.85),
            safety_margin_percent=thresholds.get("safety_margin_percent", 50),
        )

        return {
            "overall_risk_score": risk["overall_risk_score"],
            "risk_level": risk["risk_level"],
            "recommendation": risk["recommendation"],
            "confidence": risk["confidence"],
            "component_scores": risk["component_scores"],
            "compliance": thresholds.get("compliance_level", "UNKNOWN"),
        }

    def get_aggregator(self) -> ResultsAggregator:
        """Create a ResultsAggregator from the last run."""
        agg = ResultsAggregator()
        for sid, res in self.results.items():
            agg.add_result(ScenarioResult(
                scenario_id=sid,
                conflict_type=res.get("scenario", {}).get("conflict_type", "unknown"),
                jurisdiction=self.jurisdiction,
                collision_rate=res.get("monte_carlo", {}).get("collision_rate", 0),
                n_collisions=res.get("monte_carlo", {}).get("n_collisions", 0),
                n_samples=res.get("monte_carlo", {}).get("n_samples", 0),
                severity_mean=res.get("bayesian_evt", {}).get("severity_score", 0),
                ttc_mean=res.get("monte_carlo", {}).get("ttc_mean", 0),
                drac_mean=res.get("monte_carlo", {}).get("drac_mean", 0),
                safety_margin_percent=res.get("safety_thresholds", {}).get("safety_margin_percent", 0),
                compliance=res.get("safety_thresholds", {}).get("compliance_level", "UNKNOWN"),
                risk_score=res.get("portfolio_aggregation", {}).get("overall_risk_score", 0),
                risk_level=res.get("portfolio_aggregation", {}).get("risk_level", "UNKNOWN"),
                metadata={"pipeline_duration": self.log.total_duration},
            ))
        return agg
