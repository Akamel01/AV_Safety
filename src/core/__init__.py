"""Enums and shared types for the AV_Safety pipeline."""
from __future__ import annotations

from enum import Enum, auto


class ConflictType(str, Enum):
    """The 8 conflict types defined in the scenario taxonomy."""
    CROSSING = "crossing"
    MERGING = "merging"
    DIVERGING = "diverging"
    WEAVING = "weaving"
    REAR_END = "rear-end"
    SIDESWIPE = "sideswipe"
    RIGHT_ANGLE = "right-angle"
    OPPOSING_LEFT_TURN = "opposing-left-turn"


class TTCLevel(str, Enum):
    """Time-to-collision risk levels."""
    CRITICAL = "critical"
    DANGEROUS = "dangerous"
    WARNING = "warning"
    SAFE = "safe"


class DRACLevel(str, Enum):
    """DRAC braking intensity levels."""
    EMERGENCY = "emergency"
    HARD = "hard"
    MODERATE = "moderate"
    LIGHT = "light"


class ComplianceLevel(str, Enum):
    """Compliance classification from threshold checker."""
    FULL = "FULL"
    CONDITIONAL = "CONDITIONAL"
    NON_COMPLIANT = "NON_COMPLIANT"


class RiskLevel(str, Enum):
    """Risk classification levels from scorer."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PipelineStep(str, Enum):
    """Pipeline step identifiers."""
    KINEMATICS = "kinematics"
    MONTE_CARLO = "monte_carlo"
    BAYESIAN_EVT = "bayesian_evt"
    COLLISION_MODEL = "collision_model"
    SAFETY_THRESHOLDS = "safety_thresholds"
    RISK_SCORING = "risk_scoring"
    AGGREGATION = "aggregation"
    VALIDATION = "validation"
