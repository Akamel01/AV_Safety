"""Kinematics engine validator — checks vehicle models, conflict type trajectories,
simulation parameters, and cross-references."""

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
class KinematicsReport:
    vehicle_models: int = 0
    conflict_trajectories: int = 0
    sim_params_valid: bool = False
    pedestrian_params_valid: bool = False
    cyclist_params_valid: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Kinematics Engine Validation ===",
            f"Vehicle models: {self.vehicle_models}/5 {'✓' if self.vehicle_models >= 5 else '❌'}",
            f"Conflict type trajectories: {self.conflict_trajectories}/8 {'✓' if self.conflict_trajectories >= 8 else '❌'}",
            f"Simulation params: {'✓' if self.sim_params_valid else '❌'}",
            f"Pedestrian params: {'✓' if self.pedestrian_params_valid else '❌'}",
            f"Cyclist params: {'✓' if self.cyclist_params_valid else '❌'}",
            "Cross-references:",
        ]
        for skill, rel in self.cross_refs.items():
            lines.append(f"  {skill}: {'✓' if rel != '❌' else '❌'} ({rel})")
        if self.issues:
            lines.append(f"Issues found: {len(self.issues)}")
            for i in self.issues:
                lines.append(f"  ❌ {i}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠️ {w}")
        if not self.issues and not self.warnings:
            lines.append("All checks passed ✓")
        return "\n".join(lines)


EXPECTED_MODELS = 5
EXPECTED_TRAJECTORIES = 8
EXPECTED_CROSS_REFS = {
    "scenario-taxonomy": "upstream",
    "indicator-computation": "downstream",
    "stochastic-simulation": "sibling",
    "3d-animation": "downstream",
    "bayesian-evt": "sibling",
    "risk-quantification": "sibling",
}


class KinematicsValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "kinematics-engine" / "SKILL.md"
        self.report = KinematicsReport()

    def validate(self) -> KinematicsReport:
        self._check_vehicle_models()
        self._check_conflict_trajectories()
        self._check_sim_params()
        self._check_road_user_params()
        self._check_cross_references()
        return self.report

    def _check_vehicle_models(self):
        content = self.skill_md.read_text().lower()
        models = ["constant velocity", "constant acceleration", "pacejka", "bicycle", "pedestrian"]
        for model in models:
            if model in content:
                self.report.vehicle_models += 1

    def _check_conflict_trajectories(self):
        content = self.skill_md.read_text()
        conflicts = ["crossing", "merging", "diverging", "weaving", "rear-end", "sideswipe", "right-angle", "opposing"]
        found = sum(1 for c in conflicts if c in content.lower())
        self.report.conflict_trajectories = found

    def _check_sim_params(self):
        content = self.skill_md.read_text()
        self.report.sim_params_valid = all(
            kw in content for kw in ["dt", "collision", "position", "velocity", "accuracy"]
        )

    def _check_road_user_params(self):
        content = self.skill_md.read_text()
        self.report.pedestrian_params_valid = "stride" in content.lower() and "reaction" in content.lower()
        self.report.cyclist_params_valid = "cruising" in content.lower() and "braking" in content.lower()

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = KinematicsValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
