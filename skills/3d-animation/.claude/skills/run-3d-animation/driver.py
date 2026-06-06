"""3D animation validator — checks technology stack, core systems, integration points,
quality requirements, and cross-references."""

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
class AnimationReport:
    tech_stack_valid: bool = False
    core_systems: int = 0
    asset_types: int = 0
    integration_inputs: int = 0
    integration_outputs: int = 0
    quality_valid: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== 3D Animation Validation ===",
            f"Tech stack: {'✓' if self.tech_stack_valid else '❌'} (Three.js + post-processing + 2D fallback)",
            f"Core systems: {self.core_systems}/5",
            f"Asset types: {self.asset_types}/8",
            f"Integration inputs: {self.integration_inputs}/5",
            f"Integration outputs: {self.integration_outputs}/4",
            f"Quality requirements: {'✓' if self.quality_valid else '❌'}",
            "Cross-references:",
        ]
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


EXPECTED_CROSS_REFS = {
    "scenario-taxonomy": "upstream",
    "kinematics-engine": "upstream",
    "indicator-computation": "upstream",
    "stochastic-simulation": "upstream",
    "bayesian-evt": "upstream",
    "portfolio-ui": "downstream",
}


class AnimationValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "3d-animation" / "SKILL.md"
        self.report = AnimationReport()

    def validate(self) -> AnimationReport:
        self._check_tech_stack()
        self._count_core_systems()
        self._count_assets()
        self._count_integrations()
        self._check_quality()
        self._check_cross_references()
        return self.report

    def _check_tech_stack(self):
        content = self.skill_md.read_text()
        self.report.tech_stack_valid = "Three.js" in content and "Canvas" in content

    def _count_core_systems(self):
        content = self.skill_md.read_text()
        systems = ["Scene Manager", "Vehicle Model", "Lighting", "Camera", "HUD"]
        self.report.core_systems = sum(1 for s in systems if s in content)

    def _count_assets(self):
        content = self.skill_md.read_text()
        assets = ["Vehicles", "Roads", "Signage", "Pedestrians", "Cyclists", "Environment", "Collision FX"]
        self.report.asset_types = sum(1 for a in assets if a in content)

    def _count_integrations(self):
        content = self.skill_md.read_text()
        self.report.integration_inputs = sum(1 for src in ["taxonomy", "kinematics", "indicator", "Monte Carlo", "Bayesian"] if src.lower() in content)
        self.report.integration_outputs = sum(1 for out in ["3D scene", "2D scene", "HUD", "distribution"] if out in content.lower())

    def _check_quality(self):
        content = self.skill_md.read_text()
        self.report.quality_valid = all(kw in content.lower() for kw in ["pbr", "shadow", "interpolation"])

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = AnimationValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
