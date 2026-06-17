"""Integration tests for AV_Safety API endpoints."""

import subprocess
import json
import os
import time

BASE_URL = "http://localhost:3009"


def test_get_av_safety_api():
    """Test GET /api/av-safety endpoint."""
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"curl failed with code {result.returncode}"
    
    data = json.loads(result.stdout)
    
    assert data["status"] == "success", f"Status is not 'success': {data['status']}"
    assert "pipeline" in data, "Missing pipeline field"
    assert "scenario" in data, "Missing scenario field"
    assert "monte_carlo" in data, "Missing monte_carlo field"
    assert "risk_score" in data, "Missing risk_score field"
    
    # Verify pipeline info
    assert "id" in data["pipeline"], "Missing pipeline.id"
    assert "version" in data["pipeline"], "Missing pipeline.version"
    
    # Verify scenario info
    assert "id" in data["scenario"], "Missing scenario.id"
    assert "type" in data["scenario"], "Missing scenario.type"
    assert "jurisdiction" in data["scenario"], "Missing scenario.jurisdiction"
    
    # Verify Monte Carlo results
    assert "collision_rate" in data["monte_carlo"], "Missing collision_rate"
    assert "n_samples" in data["monte_carlo"], "Missing n_samples"
    assert "n_collisions" in data["monte_carlo"], "Missing n_collisions"
    
    # Verify risk score
    assert "risk_level" in data["risk_score"], "Missing risk_level"
    assert "confidence" in data["risk_score"], "Missing confidence"


def test_post_av_safety_api():
    """Test POST /api/av-safety endpoint."""
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"curl failed with code {result.returncode}"
    
    data = json.loads(result.stdout)
    
    assert data["status"] == "success", f"Status is not 'success': {data['status']}"
    assert "run_triggered" in data, "Missing run_triggered field"
    assert data["run_triggered"] is True, "run_triggered is not True"
    assert "execution_log" in data, "Missing execution_log field"
    assert "stdout" in data["execution_log"], "Missing execution_log.stdout"
    
    # Verify output file was created
    output_path = "/Users/akamel/projects/AV_Safety/single-scenario-demo/av-safety-results-001.json"
    assert os.path.exists(output_path), f"Output file not found: {output_path}"
    
    # Verify output file is valid JSON
    with open(output_path) as f:
        file_data = json.load(f)
    
    assert "pipeline_info" in file_data, "Missing pipeline_info in output file"
    assert "scenario_info" in file_data, "Missing scenario_info in output file"
    assert "monte_carlo" in file_data, "Missing monte_carlo in output file"


def test_av_safety_output_format():
    """Test that AV_Safety output format matches API expectations."""
    output_path = "/Users/akamel/projects/AV_Safety/single-scenario-demo/av-safety-results-001.json"
    
    with open(output_path) as f:
        data = json.load(f)
    
    # Check top-level structure
    assert "pipeline_info" in data
    assert "scenario_info" in data
    assert "monte_carlo" in data
    assert "bayesian_evt" in data
    assert "threshold_checker" in data
    assert "risk_scoring" in data
    
    # Check scenario info has conflict_type
    assert "conflict_type" in data["scenario_info"], "Missing conflict_type in scenario_info"
    assert data["scenario_info"]["conflict_type"] == "rear-end", "Wrong conflict_type"


def test_av_safety_dashboard_compatibility():
    """Test that dashboard can parse AV_Safety output."""
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    
    # Verify all fields the dashboard expects are present
    dashboard_fields = {
        "pipeline": ["id", "version"],
        "scenario": ["id", "type", "jurisdiction"],
        "monte_carlo": ["n_samples", "collision_rate", "n_collisions", "ttc_mean", "drac_mean"],
        "bayesian_evt": ["severity_score"],
        "thresholds": ["jurisdiction", "compliance", "safety_margin_percent"],
        "risk_score": ["composite", "risk_level", "confidence"],
    }
    
    for field, subfields in dashboard_fields.items():
        assert field in data, f"Missing dashboard field: {field}"
        for subfield in subfields:
            assert subfield in data[field], f"Missing {field}.{subfield}"


def test_av_safety_comprehensive():
    """Comprehensive end-to-end test of AV_Safety API."""
    # Run the pipeline
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0
    
    run_data = json.loads(result.stdout)
    assert run_data["run_triggered"] is True
    
    # Wait a moment for file write to complete
    time.sleep(0.5)
    
    # Fetch results
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    
    fetch_data = json.loads(result.stdout)
    assert fetch_data["status"] == "success"
    
    # Verify data makes sense
    collision_rate = fetch_data["monte_carlo"]["collision_rate"]
    assert 0 <= collision_rate <= 1, f"Collision rate out of range: {collision_rate}"
    
    risk_level = fetch_data["risk_score"]["risk_level"]
    assert risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"], f"Invalid risk level: {risk_level}"
    
    print(f"\nComprehensive test passed!")
    print(f"  Collision rate: {collision_rate}")
    print(f"  Risk level: {risk_level}")
    print(f"  Confidence: {fetch_data['risk_score']['confidence']}")
