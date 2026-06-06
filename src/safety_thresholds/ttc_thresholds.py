"""Time-to-Collision (TTC) threshold definitions.

Defines TTC thresholds for different risk levels per UL 4600 and
ISO 21448 (SOTIF) guidance.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class TTCLevel(str, Enum):
    """TTC risk levels from critical to safe."""
    CRITICAL = "critical"     # Immediate collision likely
    DANGEROUS = "dangerous"   # High collision risk
    WARNING = "warning"       # Moderate collision risk
    SAFE = "safe"             # Low collision risk


@dataclass(frozen=True)
class TTCThreshold:
    """A single TTC threshold level."""
    level: str
    threshold_seconds: float
    description: str
    required_action: str
    ul4600_reference: str
    sotif_reference: str


# Pre-computed TTC thresholds
TTC_THRESHOLDS: dict[str, TTCThreshold] = {
    "critical": TTCThreshold(
        level="critical",
        threshold_seconds=1.0,
        description="Immediate collision likely",
        required_action="Emergency brake",
        ul4600_reference="minimum TTC = 2.0s at actuation limit",
        sotif_reference="TTC >= 1.0s at perception limit",
    ),
    "dangerous": TTCThreshold(
        level="dangerous",
        threshold_seconds=2.0,
        description="High collision risk",
        required_action="Hard brake",
        ul4600_reference="minimum safe distance = 2.0s TTC",
        sotif_reference="TTC >= 2.0s at actuation limit",
    ),
    "warning": TTCThreshold(
        level="warning",
        threshold_seconds=3.0,
        description="Moderate collision risk",
        required_action="Alert driver",
        ul4600_reference="",
        sotif_reference="",
    ),
    "safe": TTCThreshold(
        level="safe",
        threshold_seconds=5.0,
        description="Low collision risk",
        required_action="Monitor",
        ul4600_reference="",
        sotif_reference="min TTC >= 2.5s",
    ),
}


def classify_ttc(ttc: float) -> TTCLevel:
    """Classify a TTC value into a risk level.

    Args:
        ttc: Time-to-collision in seconds.

    Returns:
        The TTCLevel enum value.
    """
    if ttc <= 0:
        return TTCLevel.CRITICAL
    if ttc <= 1.0:
        return TTCLevel.CRITICAL
    elif ttc <= 2.0:
        return TTCLevel.DANGEROUS
    elif ttc <= 3.0:
        return TTCLevel.WARNING
    else:
        return TTCLevel.SAFE


def get_threshold_for_level(level: str) -> TTCThreshold | None:
    """Get the threshold definition for a given level."""
    return TTC_THRESHOLDS.get(level)
