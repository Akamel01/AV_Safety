"""Regulatory framework thresholds.

UL 4600 (Safety of the Innovation) and ISO 21448 (SOTIF) threshold definitions
for AV collision avoidance and risk management.
"""

from __future__ import annotations


# UL 4600 Thresholds
# Source: UL 4600 - Standard for Safety of the Innovative Mobility System
UL4600_THRESHOLDS = {
    "collision_avoidance": {
        "minimum_safe_distance": "2.0 seconds TTC",
        "maximum_acceptable_collision_rate": 1e-6,
        "maximum_acceptable_collision_rate_str": "10^-6 per flight hour",
        "safety_margin": ">= 50% above threshold",
    },
    "risk_management": {
        "individual_risk_acceptable": 1e-5,
        "individual_risk_acceptable_str": "10^-5 per flight hour",
        "societal_risk_acceptable": 1e-7,
        "societal_risk_acceptable_str": "10^-7 per flight hour",
        "risk_reduction_required": 90,
        "risk_reduction_required_str": ">= 90% below baseline",
    },
    "validation": {
        "minimum_test_scenarios": 100000,
        "minimum_coverage": "all operational design domains",
        "documentation_required": True,
    },
}


# ISO 21448 (SOTIF) Thresholds
# Source: ISO 21448 - Road vehicles — Safety of the functionality
ISO21448_THRESHOLDS = {
    "performance": {
        "minimum_safe_operation": "TTC >= 2.5s",
        "degradation_tolerance": "10%",
        "degradation_tolerance_numeric": 0.10,
        "fallback_distance": "50m at legal speed",
    },
    "hazard_analysis": {
        "unintended_functionality": "zero tolerance",
        "perception_limit": "TTC >= 1.0s at perception limit",
        "actuation_limit": "TTC >= 2.0s at actuation limit",
    },
    "operational_design_domain": {
        "weather_conditions": "all expected weather conditions",
        "road_types": "all expected road types",
        "speed_range": "all expected speed ranges",
    },
}


def check_ul4600_compliance(
    collision_rate: float,
    individual_risk: float,
    societal_risk: float,
    risk_reduction_percent: float,
) -> dict:
    """Check compliance against UL 4600 thresholds.

    Args:
        collision_rate: Observed collision rate.
        individual_risk: Individual risk per hour.
        societal_risk: Societal risk per hour.
        risk_reduction_percent: Percentage risk reduction below baseline.

    Returns:
        Dict with 'compliant' boolean and 'violations' list.
    """
    violations = []

    if collision_rate > UL4600_THRESHOLDS["collision_avoidance"]["maximum_acceptable_collision_rate"]:
        violations.append(
            f"Collision rate {collision_rate:.2e} exceeds UL4600 limit "
            f"{UL4600_THRESHOLDS['collision_avoidance']['maximum_acceptable_collision_rate_str']}"
        )

    if individual_risk > UL4600_THRESHOLDS["risk_management"]["individual_risk_acceptable"]:
        violations.append(
            f"Individual risk {individual_risk:.2e} exceeds UL4600 limit "
            f"{UL4600_THRESHOLDS['risk_management']['individual_risk_acceptable_str']}"
        )

    if societal_risk > UL4600_THRESHOLDS["risk_management"]["societal_risk_acceptable"]:
        violations.append(
            f"Societal risk {societal_risk:.2e} exceeds UL4600 limit "
            f"{UL4600_THRESHOLDS['risk_management']['societal_risk_acceptable_str']}"
        )

    if risk_reduction_percent < UL4600_THRESHOLDS["risk_management"]["risk_reduction_required"]:
        violations.append(
            f"Risk reduction {risk_reduction_percent:.1f}% below UL4600 required "
            f"{UL4600_THRESHOLDS['risk_management']['risk_reduction_required_str']}"
        )

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "standard": "UL4600",
    }


def check_sotif_compliance(
    ttc: float,
    degradation_percent: float,
) -> dict:
    """Check compliance against ISO 21448 (SOTIF) thresholds.

    Args:
        ttc: Observed time-to-collision in seconds.
        degradation_percent: Observed degradation percentage.

    Returns:
        Dict with 'compliant' boolean and 'violations' list.
    """
    violations = []

    if ttc < 2.5:
        violations.append(
            f"TTC {ttc:.2f}s below ISO 21448 minimum {ISO21448_THRESHOLDS['performance']['minimum_safe_operation']}"
        )

    if degradation_percent > ISO21448_THRESHOLDS["performance"]["degradation_tolerance_numeric"]:
        violations.append(
            f"Degradation {degradation_percent:.1%} exceeds ISO 21448 tolerance "
            f"{ISO21448_THRESHOLDS['performance']['degradation_tolerance']}"
        )

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "standard": "ISO21448",
    }
