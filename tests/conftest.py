"""Pytest fixtures for AV_Safety tests.

Shared fixtures for scenario loading, pipeline creation, and
parameter generation.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def scenario_data_path(repo_root: Path) -> Path:
    """Path to the RE-CA-001 scenario JSON file."""
    return repo_root / "single-scenario-demo" / "data" / "scenario-RE-CA-001.json"


@pytest.fixture(scope="session")
def nominal_scenario(scenario_data_path: Path) -> dict:
    """Load the nominal scenario specification."""
    return json.loads(scenario_data_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def pipeline_scenario(nominal_scenario: dict) -> dict:
    """Scenario formatted for the Python pipeline."""
    scenario = nominal_scenario.get("scenario", {}).copy()
    scenario["scenario_id"] = nominal_scenario["scenario"]["id"]
    scenario["conflict_type"] = nominal_scenario["scenario"]["conflict_type"]
    scenario["jurisdiction"] = nominal_scenario["scenario"].get("jurisdiction", "USA")
    scenario["road_geometry"] = nominal_scenario.get("road_geometry", {})
    return scenario


@pytest.fixture
def minimal_scenario() -> dict:
    """Minimal scenario dict for pipeline testing."""
    return {
        "scenario_id": "TEST-001",
        "conflict_type": "rear-end",
        "road_users": {
            "vehicle_a": {
                "initial_velocity_ms": 27.8,
                "brake_event_t": 3.0,
                "brake_accel_ms2": -5.0,
                "max_brake_ms2": -8.0,
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
