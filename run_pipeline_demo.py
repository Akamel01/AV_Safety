#!/usr/bin/env python3
"""Run the AV_Safety pipeline on a demo scenario and output results."""

import sys
import os

# Change to project root for relative imports to work
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Now import
from risk_quantification.pipeline import RiskQuantificationPipeline
import json
from pathlib import Path

def main():
    # Create a simple scenario based on demo data
    scenario = {
        "scenario_id": "DEMO-001",
        "conflict_type": "rear-end",
        "road_users": {
            "vehicle_a": {
                "initial_velocity_ms": 27.8,  # 100 km/h
                "brake_event_t": 3.0,
                "brake_accel_ms2": -5.0,
                "max_brake_ms2": -8.0,
                "dimensions_m": [4.3, 1.8, 1.4],
                "mass_kg": 1200,
                "initial_position_m": [0, 1.85, 0],
            },
            "vehicle_b": {
                "initial_velocity_ms": 27.8,  # 100 km/h
                "initial_gap_m": 30.0,
                "reaction_time_s": 1.5,
                "max_decel_ms2": -8.0,
                "comfort_decel_ms2": -3.5,
                "brake_lag_s": 0.15,
                "abs_threshold_ms2": 8.33,
            }
        },
        "road_geometry": {
            "lane_width_m": 3.7,
            "lanes": 4,
            "segment_length_m": 200,
            "curve_type": "tangent",
            "visibility_m": 300,
            "surface": "dry asphalt",
            "friction_coefficient": 0.85,
        },
        "parameters": {},
    }
    
    print("Running AV_Safety pipeline...")
    
    # Run pipeline
    pipeline = RiskQuantificationPipeline(
        scenario=scenario,
        n_mc_samples=1000,  # Use fewer samples for faster demo
        jurisdiction="usa",
        seed=42,
    )
    
    results = pipeline.run()
    
    # Build output format matching API expectations
    output = {
        "pipeline_info": {
            "pipeline_id": "av-safety-pipeline-v1",
            "version": "1.0.0",
            "completed_at": pipeline.log.end_time,
        },
        "scenario_info": {
            "scenario_id": results.get("scenario_id", "unknown"),
            "conflict_type": scenario.get("conflict_type", "unknown"),  # Use scenario's conflict_type
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
    output_dir = Path(project_root) / 'single-scenario-demo'
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'av-safety-results-001.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"Pipeline complete! Results written to {output_path}")
    print(f"Collision rate: {output['monte_carlo'].get('collision_rate', 0)}")
    print(f"Risk level: {output['risk_scoring'].get('risk_level', 'unknown')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
