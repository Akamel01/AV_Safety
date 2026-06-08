"""Stochastic simulation validator — checks Monte Carlo framework, parameter distributions,
adaptive sizing, uncertainty quantification, and cross-references."""

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
class StochSimReport:
    mc_framework: bool = False
    speed_dist_count: int = 0
    friction_dist_count: int = 0
    reaction_count: int = 0
    adaptive_valid: bool = False
    uncertainty_methods: list[str] = field(default_factory=list)
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Stochastic Simulation Validation ===",
            f"MC framework: {'✓' if self.mc_framework else '❌'}",
            f"Speed distributions: {self.speed_dist_count}/5",
            f"Friction distributions: {self.friction_dist_count}/5",
            f"Reaction conditions: {self.reaction_count}/5",
            f"Adaptive sizing: {'✓' if self.adaptive_valid else '❌'}",
            f"Uncertainty methods: {', '.join(self.uncertainty_methods) or 'none'}",
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
    "kinematics-engine": "downstream",
    "bayesian-evt": "downstream",
    "indicator-computation": "downstream",
    "risk-quantification": "sibling",
    "data-ingest": "sibling",
}


class StochSimValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "stochastic-simulation" / "SKILL.md"
        self.report = StochSimReport()

    def validate(self) -> StochSimReport:
        self._check_mc_framework()
        self._count_distributions()
        self._check_adaptive()
        self._check_uncertainty()
        self._check_cross_references()
        return self.report

    def _check_mc_framework(self):
        content = self.skill_md.read_text()
        self.report.mc_framework = "Monte Carlo" in content and "sample" in content.lower()

    def _count_distributions(self):
        content = self.skill_md.read_text()
        self.report.speed_dist_count = sum(1 for t in ["urban car", "urban SUV", "highway car", "highway SUV", "highway truck"] if t in content)
        self.report.friction_dist_count = sum(1 for s in ["dry asphalt", "wet asphalt", "snow", "ice", "gravel"] if s in content)
        self.report.reaction_count = sum(1 for c in ["Alert", "Normal", "Distracted", "Elderly", "Exhausted"] if c in content)

    def _check_adaptive(self):
        content = self.skill_md.read_text()
        self.report.adaptive_valid = all(kw in content for kw in ["Adaptive", "convergence", "Wilson"])

    def _check_uncertainty(self):
        content = self.skill_md.read_text()
        for method in ["Wilson", "bootstrap", "Sobol"]:
            if method in content:
                self.report.uncertainty_methods.append(method)

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = StochSimValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
