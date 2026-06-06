"""Tests for the risk quantification pipeline."""

import pytest
from src.risk_quantification.pipeline import (
    RiskQuantificationPipeline,
    PipelineStep,
    PipelineLog,
)
from src.risk_quantification.risk_scoring import RiskScorer
from src.risk_quantification.threshold_checker import ThresholdComplianceChecker
from src.risk_quantification.results_aggregator import ResultsAggregator
from src.safety_thresholds.collision_rate_thresholds import THRESHOLDS
from src.safety_thresholds.deployment_criteria import AVDeploymentCriteria


class TestPipelineStep:
    """Test PipelineStep dataclass."""
    
    def test_default_values(self):
        step = PipelineStep(name="test")
        assert step.name == "test"
        assert step.duration_seconds == 0.0
        assert step.status == "pending"


class TestPipelineLog:
    """Test PipelineLog dataclass."""
    
    def test_total_duration(self):
        log = PipelineLog(start_time=100.0, end_time=105.0)
        assert log.total_duration == 5.0
    
    def test_all_completed_empty(self):
        log = PipelineLog(start_time=100.0, end_time=100.0)
        assert log.all_completed is True
    
    def test_all_completed_partial(self):
        log = PipelineLog()
        log.steps.append(PipelineStep(name="a", status="completed"))
        log.steps.append(PipelineStep(name="b", status="pending"))
        assert log.all_completed is False
    
    def test_all_completed_all_done(self):
        log = PipelineLog()
        log.steps.append(PipelineStep(name="a", status="completed"))
        log.steps.append(PipelineStep(name="b", status="completed"))
        assert log.all_completed is True


class TestRiskScorer:
    """Test RiskScorer class."""
    
    def test_default_weights(self):
        scorer = RiskScorer()
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 1e-10
    
    def test_score_returns_correct_fields(self):
        scorer = RiskScorer()
        result = scorer.score(
            collision_rate=0.1,
            severity=0.3,
            uncertainty=0.2,
            safety_margin_percent=50.0,
        )
        assert "overall_risk_score" in result
        assert "risk_level" in result
        assert "component_scores" in result
        assert "weights" in result
        assert "recommendation" in result
    
    def test_score_returns_component_scores_with_weight_keys(self):
        scorer = RiskScorer()
        result = scorer.score(
            collision_rate=0.1,
            severity=0.3,
            uncertainty=0.2,
            safety_margin_percent=50.0,
        )
        for key in scorer.weights:
            assert key in result["component_scores"], \
                f"Weight key '{key}' missing from component_scores"
    
    def test_batch_scoring(self):
        scorer = RiskScorer()
        results = scorer.score_batch([
            {"collision_rate": 0.01, "severity": 0.1, "uncertainty": 0.1, "safety_margin_percent": 50.0},
            {"collision_rate": 0.5, "severity": 0.8, "uncertainty": 0.5, "safety_margin_percent": 10.0},
        ])
        assert len(results) == 2
        assert "overall_risk_score" in results[0]
        assert "risk_level" in results[0]


class TestThresholdComplianceChecker:
    """Test threshold compliance checking."""
    
    def test_known_jurisdictions(self):
        for jur in THRESHOLDS:
            checker = ThresholdComplianceChecker(jur)
            assert checker.jurisdiction == jur
    
    def test_unknown_jurisdiction_raises(self):
        with pytest.raises(ValueError, match="Unknown jurisdiction"):
            ThresholdComplianceChecker("unknown")
    
    def test_check_compliance_returns_fields(self):
        checker = ThresholdComplianceChecker("usa")
        result = checker.check_compliance(collision_rate=0.5)
        assert "meets_threshold" in result
        assert "compliance_level" in result
        assert "safety_margin_percent" in result


class TestAVDeploymentCriteria:
    """Test AV deployment criteria."""
    
    def test_all_jurisdictions(self):
        criteria = AVDeploymentCriteria()
        result = criteria.evaluate_all_jurisdictions(0.5)
        assert len(result) == 3
        for jur in ["usa", "canada", "england"]:
            assert jur in result


class TestPipelineIntegration:
    """End-to-end pipeline tests."""
    
    def test_run_pipeline(self):
        scenario = {
            "scenario_id": "TEST-001",
            "conflict_type": "rear-end",
            "road_users": {
                "vehicle_a": {
                    "initial_velocity_ms": 27.8,
                    "brake_event_t": 3.0,
                    "brake_accel_ms2": -5.0,
                    "dimensions_m": [4.3, 1.8, 1.4],
                },
                "vehicle_b": {
                    "initial_velocity_ms": 27.8,
                    "initial_gap_m": 30.0,
                    "reaction_time_s": 1.5,
                    "max_decel_ms2": -8.0,
                },
            },
            "road_geometry": {"lane_width_m": 3.7},
            "parameters": {},
        }
        
        pipeline = RiskQuantificationPipeline(
            scenario=scenario,
            n_mc_samples=100,
            jurisdiction="usa",
        )
        results = pipeline.run()
        
        assert results["scenario_id"] == "TEST-001"
        assert "kinematics" in results
        assert "monte_carlo" in results
        assert "portfolio_aggregation" in results
        assert pipeline.log.all_completed
    
    def test_pipeline_stores_result(self):
        scenario = {
            "scenario_id": "TEST-001",
            "conflict_type": "rear-end",
            "road_users": {
                "vehicle_a": {
                    "initial_velocity_ms": 27.8,
                    "brake_event_t": 3.0,
                    "brake_accel_ms2": -5.0,
                    "dimensions_m": [4.3, 1.8, 1.4],
                },
                "vehicle_b": {
                    "initial_velocity_ms": 27.8,
                    "initial_gap_m": 30.0,
                    "reaction_time_s": 1.5,
                    "max_decel_ms2": -8.0,
                },
            },
            "road_geometry": {"lane_width_m": 3.7},
            "parameters": {},
        }
        
        pipeline = RiskQuantificationPipeline(
            scenario=scenario,
            n_mc_samples=100,
        )
        pipeline.run()
        assert "TEST-001" in pipeline.results
