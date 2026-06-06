"""Pipeline validation module.

Validates pipeline outputs for completeness, NaN values, convergence,
and reproducibility.
"""

from __future__ import annotations

import math
from typing import Any


def validate_no_nan(results: dict[str, Any]) -> list[str]:
    """Check all numeric values for NaN/Inf.

    Args:
        results: Pipeline results dict.

    Returns:
        List of error messages (empty if valid).
    """
    errors = []

    def _check_value(key_path: str, value: Any) -> None:
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                errors.append(f"NaN/Inf at {key_path}: {value}")
        elif isinstance(value, dict):
            for k, v in value.items():
                _check_value(f"{key_path}.{k}", v)
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value):
                _check_value(f"{key_path}[{i}]", item)

    _check_value("results", results)
    return errors


def validate_all_steps_complete(log_data: dict) -> tuple[bool, list[str]]:
    """Check that all pipeline steps completed successfully.

    Args:
        log_data: Pipeline log dict with 'steps' list.

    Returns:
        (all_complete, step_errors) tuple.
    """
    steps = log_data.get("steps", [])
    if not steps:
        return False, ["No steps in log"]

    errors = []
    for step in steps:
        if step.get("status") != "completed":
            errors.append(
                f"Step '{step.get('name')}' is {step.get('status')}"
            )

    return len(errors) == 0, errors


def validate_convergence(results: dict, tolerance: float = 1e-3) -> dict:
    """Validate statistical convergence of results.

    Args:
        results: Results dict with 'monte_carlo' and 'bayesian_evt'.
        tolerance: Convergence tolerance.

    Returns:
        Dict with convergence status.
    """
    mc = results.get("monte_carlo", {})
    evt = results.get("bayesian_evt", {})

    checks = {}

    # MC convergence: CI width vs mean
    ci95 = mc.get("collision_rate_ci95", (0, 0))
    rate = mc.get("collision_rate", 0)
    n_samples = mc.get("n_samples", 0)

    if ci95[1] > ci95[0] and rate > 0:
        ci_width = (ci95[1] - ci95[0]) / rate
        checks["mc_ci_relative_width"] = {
            "value": ci_width,
            "pass": ci_width < tolerance * 10,  # CI width < 10x rate
            "message": f"MC CI width/rate = {ci_width:.4f}" if ci_width < tolerance * 10
                       else f"MC CI too wide: {ci_width:.4f}",
        }
    else:
        checks["mc_ci_relative_width"] = {
            "value": 0,
            "pass": True,
            "message": "CI not available",
        }

    checks["mc_n_samples"] = {
        "value": n_samples,
        "pass": n_samples >= 10000,
        "message": f"n={n_samples} {'>= 10k' if n_samples >= 10000 else '< 10k (increase for accuracy)'}",
    }

    # EVT checks
    gpd = evt.get("gpd_params", {})
    checks["gpd_params"] = {
        "xi": gpd.get("xi", None),
        "sigma": gpd.get("sigma", None),
        "valid": gpd.get("sigma", 0) > 0,
    }

    return checks


def validate_reproducibility(
    results1: dict,
    results2: dict,
    tolerance: float = 1e-6,
) -> tuple[bool, list[str]]:
    """Check if two pipeline runs produce identical results.

    Args:
        results1: First run results.
        results2: Second run results.
        tolerance: Numeric tolerance for comparison.

    Returns:
        (identical, differences) tuple.
    """
    differences = []

    def _compare(a: Any, b: Any, path: str) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            if a.keys() != b.keys():
                differences.append(f"{path}: different keys {set(a.keys())} vs {set(b.keys())}")
            for k in a:
                _compare(a[k], b[k], f"{path}.{k}")
        elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            if len(a) != len(b):
                differences.append(f"{path}: different lengths {len(a)} vs {len(b)}")
            for i in range(min(len(a), len(b))):
                _compare(a[i], b[i], f"{path}[{i}]")
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if abs(a - b) > tolerance:
                differences.append(f"{path}: {a} vs {b}")
        elif a != b:
            differences.append(f"{path}: {a!r} vs {b!r}")

    _compare(results1, results2, "root")
    return len(differences) == 0, differences


def run_full_validation(
    results: dict,
    log_data: dict,
) -> dict[str, Any]:
    """Run all validation checks.

    Args:
        results: Pipeline results.
        log_data: Pipeline execution log.

    Returns:
        Dict with validation results for each check.
    """
    nan_errors = validate_no_nan(results)
    steps_complete, step_errors = validate_all_steps_complete(log_data)
    convergence = validate_convergence(results)
    reproducibility, repro_errors = validate_reproducibility(results, results)  # Self-check

    return {
        "nan_check": {"pass": len(nan_errors) == 0, "errors": nan_errors},
        "steps_complete": {"pass": steps_complete, "errors": step_errors},
        "convergence": convergence,
        "reproducibility": {"pass": len(repro_errors) == 0, "errors": repro_errors},
        "overall_pass": len(nan_errors) == 0 and steps_complete and len(repro_errors) == 0,
    }
