"""DRAC (Dynamic Rear-end Assessment Criterion) threshold definitions.

Defines DRAC thresholds for different braking levels per UL 4600 and
traffic engineering standards.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class DRACLevel(str, Enum):
    """DRAC braking intensity levels."""
    EMERGENCY = "emergency"
    HARD = "hard"
    MODERATE = "moderate"
    LIGHT = "light"


@dataclass(frozen=True)
class DRACThreshold:
    """A single DRAC threshold level."""
    level: str
    threshold_ms2: float
    description: str
    required_action: str


# Pre-computed DRAC thresholds
DRAC_THRESHOLDS: dict[str, DRACThreshold] = {
    "emergency": DRACThreshold(
        level="emergency",
        threshold_ms2=8.0,
        description="Maximum emergency braking",
        required_action="Full brake",
    ),
    "hard": DRACThreshold(
        level="hard",
        threshold_ms2=5.0,
        description="Hard braking required",
        required_action="Hard brake",
    ),
    "moderate": DRACThreshold(
        level="moderate",
        threshold_ms2=3.0,
        description="Moderate braking",
        required_action="Alert driver",
    ),
    "light": DRACThreshold(
        level="light",
        threshold_ms2=1.5,
        description="Light braking",
        required_action="Monitor",
    ),
}


def classify_drac(accel: float) -> DRACLevel:
    """Classify a deceleration value into a braking intensity level.

    Args:
        accel: Deceleration in m/s² (use negative values for braking).

    Returns:
        The DRACLevel enum value.
    """
    mag = abs(accel)
    if mag >= 8.0:
        return DRACLevel.EMERGENCY
    elif mag >= 5.0:
        return DRACLevel.HARD
    elif mag >= 3.0:
        return DRACLevel.MODERATE
    else:
        return DRACLevel.LIGHT
