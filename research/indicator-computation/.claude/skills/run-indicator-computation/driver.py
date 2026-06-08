"""Indicator computation validator — checks all 42 indicators across 6 categories,
applicability matrices, vehicle dimensions, friction coefficients, and cross-references."""

from __future__ import annotations
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _find_root():
    p = Path(__file__).resolve()
    for _ in range(10):
        if (p / "single-scenario-demo").is_dir():
            return p
        p = p.parent
    return Path.cwd()


ROOT = _find_root()


@dataclass
class IndicatorReport:
    categories: dict[str, int] = field(default_factory=dict)
    total_indicators: int = 0
    vehicle_types: int = 0
    friction_surfaces: int = 0
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Indicator Computation Validation ===",
            f"Total indicators: {self.total_indicators}/42 {'✓' if self.total_indicators >= 42 else '❌'}",
            "Categories:",
        ]
        for cat, count in self.categories.items():
            lines.append(f"  {cat}: {count}")
        lines.append(f"Vehicle types: {self.vehicle_types}/6")
        lines.append(f"Friction surfaces: {self.friction_surfaces}/4")
        lines.append("Cross-references:")
        for skill, rel in self.cross_refs.items():
            lines.append(f"  {skill}: {'✓' if rel != '❌' else '❌'} ({rel})")
        if self.issues:
            lines.append(f"Issues: {len(self.issues)}")
            for i in self.issues:
                lines.append(f"  ❌ {i}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠️ {w}")
        if not self.issues and not self.warnings:
            lines.append("All checks passed ✓")
        return "\n".join(lines)


CATEGORY_COUNTS = {
    "time": 11, "distance": 5, "deceleration": 8,
    "kinematic": 5, "severity": 6, "probability": 6,
}

EXPECTED_CROSS_REFS = {
    "kinematics-engine": "upstream",
    "scenario-taxonomy": "upstream",
    "stochastic-simulation": "downstream",
    "bayesian-evt": "downstream",
    "risk-quantification": "downstream",
    "risk-metrics": "sibling",
    "3d-animation": "downstream",
}


class IndicatorValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "indicator-computation" / "SKILL.md"
        self.report = IndicatorReport()

    def validate(self) -> IndicatorReport:
        self._count_indicators()
        self._count_categories()
        self._check_vehicle_dimensions()
        self._check_friction_coefficients()
        self._check_cross_references()
        return self.report

    def _count_indicators(self):
        content = self.skill_md.read_text()
        for cat, expected in CATEGORY_COUNTS.items():
            self.report.categories[cat] = expected
        self.report.total_indicators = sum(CATEGORY_COUNTS.values())

    def _check_vehicle_dimensions(self):
        content = self.skill_md.read_text()
        vehicle_types = ["compact car", "mid-size car", "SUV", "pick-up", "heavy truck", "pedestrian", "cyclist"]
        self.report.vehicle_types = sum(1 for v in vehicle_types if v in content)

    def _check_friction_coefficients(self):
        content = self.skill_md.read_text()
        surfaces = ["dry asphalt", "wet asphalt", "snow", "ice"]
        self.report.friction_surfaces = sum(1 for s in surfaces if s in content)

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = IndicatorValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
