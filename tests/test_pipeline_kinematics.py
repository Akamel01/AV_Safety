"""Tests for kinematics-integrated Monte Carlo in the pipeline."""

import sys
sys.path.insert(0, '.')

import pytest
from src.risk_quantification.pipeline import RiskQuantificationPipeline


class TestPipelineKinematicsMC:
    """Pipeline Monte Carlo uses kinematics engine."""

    def _make_scenario(self, v_b0=30.0, headway=30.0):
        """Factory for rear-end scenarios."""
        return {
            'scenario_id': 'TEST-RE-001',
            'conflict_type': 'rear-end',
            'road_type': 'highway',
            'jurisdiction': 'USA',
            'road_users': {
                'vehicle_a': {
                    'initial_velocity_ms': 25.0,
                    'brake_accel_ms2': -5.0,
                },
                'vehicle_b': {
                    'initial_velocity_ms': v_b0,
                    'max_decel_ms2': -8.0,
                    'initial_gap_m': headway,
                    'reaction_time_s': 1.5,
                },
            },
            'road_geometry': {'lane_width_m': 3.7},
            'nominal_case': {'collision': False},
            'parameters': {},
        }

    def test_pipeline_runs_with_kinematics_mc(self):
        """Pipeline.run() completes using kinematics engine."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=100,
        )
        result = p.run()
        assert 'monte_carlo' in result
        assert 'collision_rate' in result['monte_carlo']
        assert 'n_samples' in result['monte_carlo']

    def test_kinematics_mc_collision_detected(self):
        """Following vehicle faster -> collision detected."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(v_b0=30.0, headway=30.0),
            jurisdiction='USA',
            n_mc_samples=200,
        )
        result = p.run()
        mc = result['monte_carlo']
        # With v_b=30 > v_a=25 and 30m headway, kinematics should detect collisions
        # Monte Carlo with noise: expect significant collision rate (>0.1)
        assert mc['collision_rate'] > 0.1
        assert mc['n_collisions'] > 0
        assert mc['delta_v_mean'] is not None
        assert mc['delta_v_mean'] > 0

    def test_pipeline_returns_portfolio_aggregation(self):
        """Pipeline produces portfolio aggregation with risk score."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=100,
        )
        result = p.run()
        agg = result['portfolio_aggregation']
        assert 'overall_risk_score' in agg
        assert 'risk_level' in agg
        assert isinstance(agg['overall_risk_score'], (int, float))
        assert agg['risk_level'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'UNKNOWN']

    def test_pipeline_bayesian_evt_has_gpd(self):
        """Pipeline produces Bayesian EVT with GPD parameters."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=100,
        )
        result = p.run()
        evt = result['bayesian_evt']
        assert 'gpd_params' in evt
        assert 'xi' in evt['gpd_params']
        assert 'sigma' in evt['gpd_params']
        assert isinstance(evt['gpd_params']['xi'], float)

    def test_pipeline_stores_results(self):
        """Pipeline.run() populates self.results with scenario key."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=50,
        )
        p.run()
        assert 'TEST-RE-001' in p.results

    def test_pipeline_aggregator_available(self):
        """Pipeline.get_aggregator() returns ResultsAggregator."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=50,
        )
        p.run()
        agg = p.get_aggregator()
        assert len(agg.results) == 1

    def test_mc_deterministic_with_seed(self):
        """Same seed produces same collision count."""
        p1 = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=100,
            seed=42,
        )
        r1 = p1.run()

        p2 = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=100,
            seed=42,
        )
        r2 = p2.run()

        assert r1['monte_carlo']['n_collisions'] == r2['monte_carlo']['n_collisions']
        assert r1['monte_carlo']['collision_rate'] == r2['monte_carlo']['collision_rate']

    def test_pipeline_different_jurisdictions(self):
        """Pipeline runs for USA, Canada, England."""
        for jur in ['USA', 'Canada', 'England']:
            p = RiskQuantificationPipeline(
                scenario=self._make_scenario(),
                jurisdiction=jur,
                n_mc_samples=50,
            )
            result = p.run()
            assert 'portfolio_aggregation' in result
            assert 'safety_thresholds' in result

    def test_pipeline_reusable(self):
        """Pipeline.run() can be called multiple times."""
        p = RiskQuantificationPipeline(
            scenario=self._make_scenario(),
            jurisdiction='USA',
            n_mc_samples=50,
        )
        r1 = p.run()
        r2 = p.run()
        assert r1['monte_carlo']['n_collisions'] == r2['monte_carlo']['n_collisions']
