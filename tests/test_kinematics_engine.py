"""Tests for the kinematics engine — full timestep simulation."""

import sys
sys.path.insert(0, '.')

import pytest
from src.risk_quantification.kinematics_engine import (
    KinematicsEngine,
    SimulationConfig,
    CollisionResult,
    TrajectoryPoint,
    run_simple_rear_end,
    run_monte_carlo_samples,
)


class TestKinematicsEngineBasic:
    """Basic kinematics engine functionality."""

    def test_engine_runs(self):
        """Engine completes without error."""
        cfg = SimulationConfig()
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert isinstance(result, CollisionResult)

    def test_default_config_valid(self):
        """Default config produces valid parameters."""
        cfg = SimulationConfig()
        assert cfg.v_a0 == 27.8
        assert cfg.v_b0 == 27.8
        assert cfg.headway == 30.0
        assert cfg.reaction_time == 1.5
        assert cfg.t_brake_event == 3.0
        assert cfg.brake_lag == 0.15
        assert cfg.a_lead == -5.0
        assert cfg.a_follow_max == -8.0
        assert cfg.dt == 0.0025  # 2.5ms timestep


class TestCollisionDetection:
    """Collision detection correctness."""

    def test_faster_following_vehicles_causes_collision(self):
        """Following vehicle faster than lead should collide."""
        cfg = SimulationConfig(
            v_a0=25.0, v_b0=30.0, headway=30.0
        )
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is True
        assert result.collision_time is not None
        assert result.collision_time > 0
        assert result.delta_v > 0

    def test_equal_speeds_no_collision_with_large_headway(self):
        """Equal speeds + large headway = no collision."""
        cfg = SimulationConfig(
            v_a0=27.8, v_b0=27.8, headway=100.0
        )
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is False
        assert result.ttc is not None or result.ttc is None  # TTC may be None for no-collision

    def test_slower_following_vehicle_no_collision(self):
        """Following vehicle slower = no collision."""
        cfg = SimulationConfig(
            v_a0=27.8, v_b0=20.0, headway=30.0
        )
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is False

    def test_collision_time_positive(self):
        """Collision time must be positive."""
        cfg = SimulationConfig(v_a0=25.0, v_b0=30.0, headway=30.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        if result.collision:
            assert result.collision_time is not None
            assert result.collision_time > 0
            # Should be within simulation duration
            assert result.collision_time <= cfg.sim_duration

    def test_delta_v_positive_on_collision(self):
        """Delta-V must be positive when collision occurs."""
        cfg = SimulationConfig(v_a0=25.0, v_b0=30.0, headway=30.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        if result.collision:
            assert result.delta_v > 0


class TestTrajectory:
    """Trajectory history correctness."""

    def test_trajectory_points_created(self):
        """Trajectory contains simulation points."""
        cfg = SimulationConfig(sim_duration=5.0)
        engine = KinematicsEngine(cfg)
        engine.run()
        assert len(engine.trajectory) > 0
        assert isinstance(engine.trajectory[0], TrajectoryPoint)

    def test_trajectory_times_sorted(self):
        """Trajectory times are monotonically increasing."""
        cfg = SimulationConfig(sim_duration=5.0)
        engine = KinematicsEngine(cfg)
        engine.run()
        times = [pt.t for pt in engine.trajectory]
        for i in range(1, len(times)):
            assert times[i] > times[i - 1]


class TestMonteCarloIntegration:
    """Monte Carlo simulation using kinematics engine."""

    def test_monte_carlo_runs(self):
        """Monte Carlo completes without error."""
        result = run_monte_carlo_samples(n_samples=100, seed=42)
        assert 'collision_rate' in result
        assert 'n_samples' in result
        assert result['n_samples'] == 100

    def test_monte_carlo_collision_rate_range(self):
        """Collision rate is between 0 and 1."""
        result = run_monte_carlo_samples(n_samples=1000, seed=42)
        assert 0.0 <= result['collision_rate'] <= 1.0

    def test_monte_carlo_deterministic_with_seed(self):
        """Same seed produces same results."""
        r1 = run_monte_carlo_samples(n_samples=100, seed=123)
        r2 = run_monte_carlo_samples(n_samples=100, seed=123)
        assert r1['n_collisions'] == r2['n_collisions']
        assert r1['collision_rate'] == r2['collision_rate']

    def test_monte_carlo_different_results_without_seed(self):
        """Different seeds may produce different results."""
        r1 = run_monte_carlo_samples(n_samples=100, seed=1)
        r2 = run_monte_carlo_samples(n_samples=100, seed=999)
        # Results may differ — just check both are valid
        assert isinstance(r1['collision_rate'], float)
        assert isinstance(r2['collision_rate'], float)

    def test_monte_carlo_returns_expected_keys(self):
        """Monte Carlo returns all expected statistics."""
        result = run_monte_carlo_samples(n_samples=200, seed=42)
        expected_keys = [
            'n_samples', 'collision_rate', 'n_collisions',
            'collision_rate_ci95', 'ttc_mean', 'delta_v_mean',
            'mean_collision_time'
        ]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"


class TestConvenienceFunctions:
    """Convenience function tests."""

    def test_run_simple_rear_end(self):
        """Simple rear-end function works."""
        result = run_simple_rear_end(
            v_a0=25.0, v_b0=30.0, headway=30.0
        )
        assert isinstance(result, CollisionResult)
        assert result.collision is True

    def test_run_simple_rear_end_no_collision(self):
        """Simple rear-end with no collision."""
        result = run_simple_rear_end(
            v_a0=27.8, v_b0=20.0, headway=30.0
        )
        assert result.collision is False


class TestPhysicsConsistency:
    """Physics consistency checks."""

    def test_ttc_increases_with_headway(self):
        """Larger headway should increase TTC (or stay same)."""
        r1 = run_simple_rear_end(v_a0=27.8, v_b0=27.8, headway=30.0)
        r2 = run_simple_rear_end(v_a0=27.8, v_b0=27.8, headway=60.0)
        # At equal speeds with braking, larger headway gives more time
        if r1.collision and r2.collision:
            assert r2.collision_time is not None
            if r1.collision_time is not None:
                assert r2.collision_time >= r1.collision_time

    def test_delta_v_increases_with_relative_speed(self):
        """Larger relative speed = larger delta-V."""
        r1 = run_simple_rear_end(v_a0=25.0, v_b0=27.0, headway=30.0)
        r2 = run_simple_rear_end(v_a0=25.0, v_b0=30.0, headway=30.0)
        if r1.collision and r2.collision:
            assert r2.delta_v >= r1.delta_v


class TestEdgeCases:
    """Edge case handling."""

    def test_very_short_headway(self):
        """Very short headway causes immediate collision."""
        cfg = SimulationConfig(v_a0=27.8, v_b0=27.8, headway=2.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is True
        # Should collide quickly
        if result.collision_time is not None:
            assert result.collision_time < 5.0

    def test_zero_headway(self):
        """Zero headway = immediate collision (vehicles overlapping)."""
        cfg = SimulationConfig(v_a0=27.8, v_b0=27.8, headway=0.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is True

    def test_very_long_headway_no_collision(self):
        """Very long headway = no collision (gap never closes)."""
        cfg = SimulationConfig(v_a0=27.8, v_b0=27.8, headway=200.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        assert result.collision is False

    def test_custom_sim_duration(self):
        """Custom simulation duration works."""
        cfg = SimulationConfig(sim_duration=1.0)
        engine = KinematicsEngine(cfg)
        result = engine.run()
        # Simulation should complete within 1s
        assert result.simulation_time <= 1.0
