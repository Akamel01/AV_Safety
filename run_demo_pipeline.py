#!/usr/bin/env python3
"""Run the AV_Safety pipeline on a demo scenario and output results."""

import sys
import json
from pathlib import Path

# Add src to path with proper module structure
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from risk_quantification.pipeline import RiskQuantificationPipeline
from risk_quantification.output_formats import JsonExporter

def main():
    # Load demo scenario
    scenario_path = Path(__file__).parent / 'demo/data/scenario-RE-CA-001.json'
    
    if not scenario_path.exists():
        print(f"Error: Scenario file not found at {scenario_path}")
        return 1
    
    with open(scenario_path) as f:
        raw_scenario = json.load(f)
    
    # Extract scenario data from nested structure
    scenario_data = raw_scenario['scenario']
    
    # Build the pipeline scenario format
    pipeline_scenario = {
        "scenario_id": scenario_data["id"],
        "conflict_type": scenario_data["conflict_type"],
        "road_users": {
            "vehicle_a": {
                "initial_velocity_ms": scenario_data["road_users"]["vehicle_a"]["initial_velocity_ms"],
                "brake_event_t": scenario_data["road_users"]["vehicle_a"]["brake_event_t"],
                "brake_accel_ms2": scenario_data["road_users"]["vehicle_a"]["brake_accel_ms2"],
                "max_brake_ms2": scenario_data["road_users"]["vehicle_a"]["max_brake_ms2"],
                "dimensions_m": scenario_data["road_users"]["vehicle_a"]["dimensions_m"],
                "mass_kg": scenario_data["road_users"]["vehicle_a"]["mass_kg"],
                "initial_position_m": scenario_data["road_users"]["vehicle_a"]["initial_position_m"],
            },
            "vehicle_b": {
                "initial_velocity_ms": scenario_data["road_users"]["vehicle_b"]["initial_velocity_ms"],
                "initial_gap_m": scenario_data["road_users"]["vehicle_b"]["initial_gap_m"],
                "reaction_time_s": scenario_data["road_users"]["vehicle_b"]["reaction_time_s"],
                "max_decel_ms2": scenario_data["road_users"]["vehicle_b"]["max_decel_ms2"],
                "comfort_decel_ms2": scenario_data["road_users"]["vehicle_b"]["comfort_decel_ms2"],
                "brake_lag_s": scenario_data["road_users"]["vehicle_b"]["brake_lag_s"],
                "abs_threshold_ms2": scenario_data["road_users"]["vehicle_b"]["abs_threshold_ms2"],
            }
        },
        "road_geometry": {
            "lane_width_m": scenario_data["road_geometry"]["lane_width_m"],
            "lanes": scenario_data["road_geometry"]["lanes"],
            "segment_length_m": scenario_data["road_geometry"]["segment_length_m"],
            "curve_type": scenario_data["road_geometry"]["curve_type"],
            "visibility_m": scenario_data["road_geometry"]["visibility_m"],
            "surface": scenario_data["road_geometry"]["surface"],
            "friction_coefficient": scenario_data["road_geometry"]["friction_coefficient"],
        },
    }
    
    # Run pipeline
    print("Running AV_Safety pipeline...")
    pipeline = RiskQuantificationPipeline(
        scenario=pipeline_scenario,
        n_mc_samples=1000,  # Use fewer samples for faster demo
        jurisdiction="usa",
        seed=42,
    )
    
    results = pipeline.run()
    
    # Add pipeline metadata
    output = {
        "pipeline_info": {
            "pipeline_id": "av-safety-pipeline-v1",
            "version": "1.0.0",
            "completed_at": pipeline.log.end_time,
        },
        "scenario_info": {
            "scenario_id": results.get("scenario_id", "unknown"),
            "conflict_type": results.get("conflict_type", "unknown"),
            "jurisdiction": "usa",
        },
        "kinematics": results.get("kinematics", {}),
        "indicators": results.get("indicators", {}),
        "monte_carlo": results.get("monte_carlo", {}),
        "bayesian_evt": results.get("bayesian_evt", {}),
        "collision_modeling": results.get("collision_modeling", {}),
        "threshold_checker": results.get("safety_thresholds", {}),
        "risk_scoring": results.get("portfolio_aggregation", {}),
    }
    
    # Write output
    output_dir = Path(__file__).parent / 'single-scenario-demo'
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'av-safety-results-001.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"Pipeline complete! Results written to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
