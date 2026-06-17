#!/usr/bin/env python3
"""Test script for AV_Safety API integration."""

import subprocess
import json
import sys

BASE_URL = "http://localhost:3009"

def test_get_api():
    """Test GET /api/av-safety endpoint."""
    print("Testing GET /api/av-safety...")
    result = subprocess.run(
        ["curl", "-s", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"FAIL: curl failed with code {result.returncode}")
        print(result.stderr)
        return False
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON response: {e}")
        print(result.stdout[:500])
        return False
    
    # Verify response structure
    required_fields = ["status", "pipeline", "scenario", "monte_carlo", "risk_score"]
    for field in required_fields:
        if field not in data:
            print(f"FAIL: Missing required field: {field}")
            return False
    
    if data["status"] != "success":
        print(f"FAIL: Status is not 'success': {data['status']}")
        return False
    
    print(f"PASS: GET /api/av-safety - collision_rate={data['monte_carlo']['collision_rate']}, risk_level={data['risk_score']['risk_level']}")
    return True

def test_post_api():
    """Test POST /api/av-safety endpoint."""
    print("Testing POST /api/av-safety...")
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", f"{BASE_URL}/api/av-safety"],
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        print(f"FAIL: curl failed with code {result.returncode}")
        print(result.stderr)
        return False
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON response: {e}")
        print(result.stdout[:500])
        return False
    
    # Verify response structure
    required_fields = ["status", "pipeline", "scenario", "run_triggered", "execution_log"]
    for field in required_fields:
        if field not in data:
            print(f"FAIL: Missing required field: {field}")
            return False
    
    if not data["run_triggered"]:
        print(f"FAIL: run_triggered is not True")
        return False
    
    if "stdout" not in data["execution_log"]:
        print(f"FAIL: execution_log.stdout is missing")
        return False
    
    print(f"PASS: POST /api/av-safety - run_triggered={data['run_triggered']}, stdout captured")
    return True

def test_output_file():
    """Test that output file was created correctly."""
    print("Testing output file...")
    import os
    output_path = "/Users/akamel/projects/AV_Safety/single-scenario-demo/av-safety-results-001.json"
    
    if not os.path.exists(output_path):
        print(f"FAIL: Output file not found: {output_path}")
        return False
    
    try:
        with open(output_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: Invalid JSON in output file: {e}")
        return False
    
    required_fields = ["pipeline_info", "scenario_info", "monte_carlo", "risk_scoring"]
    for field in required_fields:
        if field not in data:
            print(f"FAIL: Missing required field in output: {field}")
            return False
    
    print(f"PASS: Output file is valid JSON with required structure")
    return True

def main():
    print("=" * 60)
    print("AV_Safety API Integration Test")
    print("=" * 60)
    
    results = []
    results.append(("GET /api/av-safety", test_get_api()))
    results.append(("POST /api/av-safety", test_post_api()))
    results.append(("Output file", test_output_file()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests PASSED!")
        return 0
    else:
        print(f"\n{total - passed} test(s) FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
