"""Results aggregator for risk quantification.

Aggregates results from multiple scenarios and computes summary statistics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class ScenarioResult:
    """Aggregated result for a single scenario."""
    scenario_id: str
    conflict_type: str
    jurisdiction: str
    collision_rate: float
    n_collisions: int
    n_samples: int
    severity_mean: float
    severity_std: float = 0.0
    ttc_mean: float = 0.0
    ttc_std: float = 0.0
    drac_mean: float = 0.0
    drac_std: float = 0.0
    safety_margin_percent: float = 0.0
    compliance: str = "UNKNOWN"
    risk_score: float = 0.0
    risk_level: str = "UNKNOWN"
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["confidence_interval"] = list(self.confidence_interval)
        if self.metadata is None:
            data["metadata"] = {}
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ScenarioResult":
        ci = data.get("confidence_interval", [0.0, 0.0])
        data["confidence_interval"] = tuple(ci)
        if "metadata" not in data or data["metadata"] is None:
            data["metadata"] = {}
        return ScenarioResult(**data)


class ResultsAggregator:
    """Aggregate and analyze results from multiple scenarios."""

    def __init__(self):
        self.results: dict[str, ScenarioResult] = {}

    def add_result(self, result: ScenarioResult) -> None:
        """Add a single scenario result."""
        self.results[result.scenario_id] = result

    def add_results(self, results: list[ScenarioResult]) -> None:
        """Add multiple scenario results."""
        for result in results:
            self.add_result(result)

    def get_summary(self) -> dict[str, Any]:
        """Compute summary statistics across all scenarios."""
        if not self.results:
            return {"n_scenarios": 0}

        collision_rates = [r.collision_rate for r in self.results.values() if r.n_samples > 0]
        severities = [r.severity_mean for r in self.results.values()]
        safety_margins = [r.safety_margin_percent for r in self.results.values() if r.safety_margin_percent > 0]
        risk_scores = [r.risk_score for r in self.results.values() if r.risk_score > 0]

        n_scenarios = len(self.results)
        compliant = sum(1 for r in self.results.values() if r.compliance in ("FULL", "APPROVED"))
        conditional = sum(1 for r in self.results.values() if r.compliance in ("CONDITIONAL",))
        non_compliant = sum(1 for r in self.results.values() if r.compliance in ("NON_COMPLIANT", "DENIED"))

        return {
            "n_scenarios": n_scenarios,
            "mean_collision_rate": sum(collision_rates) / len(collision_rates) if collision_rates else 0,
            "std_collision_rate": self._std(collision_rates),
            "min_collision_rate": min(collision_rates) if collision_rates else 0,
            "max_collision_rate": max(collision_rates) if collision_rates else 0,
            "mean_severity": sum(severities) / len(severities) if severities else 0,
            "mean_safety_margin": sum(safety_margins) / len(safety_margins) if safety_margins else 0,
            "mean_risk_score": sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            "compliant_count": compliant,
            "conditional_count": conditional,
            "non_compliant_count": non_compliant,
            "overall_risk_level": self._classify_overall_risk(risk_scores),
        }

    def get_by_conflict_type(self) -> dict[str, list[dict[str, Any]]]:
        """Group results by conflict type."""
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in self.results.values():
            groups.setdefault(r.conflict_type, []).append(r.to_dict())
        return groups

    def get_by_jurisdiction(self) -> dict[str, list[dict[str, Any]]]:
        """Group results by jurisdiction."""
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in self.results.values():
            groups.setdefault(r.jurisdiction, []).append(r.to_dict())
        return groups

    def export_json(self, path: str | Path) -> None:
        """Export aggregated results as JSON."""
        data = {
            "summary": self.get_summary(),
            "scenarios": {sid: r.to_dict() for sid, r in self.results.items()},
        }
        Path(path).write_text(json.dumps(data, indent=2))

    def _std(self, values: list[float]) -> float:
        """Compute sample standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def _classify_overall_risk(self, risk_scores: list[float]) -> str:
        """Classify overall risk level from mean risk score."""
        if not risk_scores:
            return "UNKNOWN"
        mean = sum(risk_scores) / len(risk_scores)
        if mean < 0.2:
            return "LOW"
        elif mean < 0.5:
            return "MEDIUM"
        elif mean < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
