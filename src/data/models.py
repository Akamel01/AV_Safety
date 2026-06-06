"""Data types and domain models for the AV_Safety pipeline.

Provides canonical data structures used across all packages:
scenarios, kinematic states, indicator results, EVT results,
and risk scoring inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Enums ──────────────────────────────────────────────────────────

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
    """Compliance levels from threshold checker."""
    FULL = "FULL"
    CONDITIONAL = "CONDITIONAL"
    NON_COMPLIANT = "NON_COMPLIANT"


class RiskLevel(str, Enum):
    """Risk classification levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Scenario models ───────────────────────────────────────────────

@dataclass
class VehicleDefinition:
    """Definition of a single road user in a scenario."""
    id: str
    # Kinematic parameters
    initial_velocity_ms: float = 0.0
    initial_accel_ms2: float = 0.0
    max_brake_ms2: float = -8.0
    brake_event_t: float = 3.0  # time when braking begins
    dimensions_m: list[float] = field(default_factory=lambda: [4.3, 1.8, 1.4])
    mass_kg: float = 1200.0
    # Driver parameters
    reaction_time_s: float = 1.5
    brake_accel_ms2: float = -5.0  # actual braking deceleration

    @property
    def length(self) -> float:
        return self.dimensions_m[0] if len(self.dimensions_m) >= 1 else 4.3

    @property
    def width(self) -> float:
        return self.dimensions_m[1] if len(self.dimensions_m) >= 2 else 1.8


@dataclass
class RoadGeometry:
    """Road geometry for a scenario."""
    lane_width_m: float = 3.7
    num_lanes: int = 2
    intersection_angle: float = 90.0  # degrees


@dataclass
class Scenario:
    """Complete scenario definition fed into the pipeline."""
    scenario_id: str
    conflict_type: ConflictType
    jurisdiction: str = "usa"
    road_geometry: RoadGeometry | None = None
    road_users: dict[str, VehicleDefinition] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize scenario to a dict for pipeline input."""
        return {
            "scenario_id": self.scenario_id,
            "conflict_type": self.conflict_type.value,
            "jurisdiction": self.jurisdiction,
            "road_geometry": (
                {"lane_width_m": self.road_geometry.lane_width_m}
                if self.road_geometry else {}
            ),
            "road_users": {
                k: {
                    "initial_velocity_ms": v.initial_velocity_ms,
                    "brake_event_t": v.brake_event_t,
                    "brake_accel_ms2": v.brake_accel_ms2,
                    "max_brake_ms2": v.max_brake_ms2,
                    "dimensions_m": v.dimensions_m,
                    "reaction_time_s": v.reaction_time_s,
                    "mass_kg": v.mass_kg,
                }
                for k, v in self.road_users.items()
            },
            "parameters": self.parameters,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scenario":
        """Deserialize scenario from dict."""
        ct = data.get("conflict_type", "rear-end")
        try:
            conflict_type = ConflictType(ct)
        except ValueError:
            conflict_type = ConflictType.REAR_END

        rg_data = data.get("road_geometry", {})
        road_geometry = None
        if rg_data:
            road_geometry = RoadGeometry(
                lane_width_m=rg_data.get("lane_width_m", 3.7),
            )

        users = {}
        for uid, udata in data.get("road_users", {}).items():
            users[uid] = VehicleDefinition(
                id=uid,
                initial_velocity_ms=udata.get("initial_velocity_ms", 0.0),
                brake_event_t=udata.get("brake_event_t", 3.0),
                brake_accel_ms2=udata.get("brake_accel_ms2", -5.0),
                max_brake_ms2=udata.get("max_brake_ms2", -8.0),
                dimensions_m=udata.get("dimensions_m", [4.3, 1.8, 1.4]),
                reaction_time_s=udata.get("reaction_time_s", 1.5),
                mass_kg=udata.get("mass_kg", 1200.0),
            )

        return Scenario(
            scenario_id=data.get("scenario_id", "UNKNOWN"),
            conflict_type=conflict_type,
            jurisdiction=data.get("jurisdiction", "usa"),
            road_geometry=road_geometry,
            road_users=users,
            parameters=data.get("parameters", {}),
        )
