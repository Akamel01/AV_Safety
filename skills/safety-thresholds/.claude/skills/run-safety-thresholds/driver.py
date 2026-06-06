"""Safety thresholds validator — checks framework steps, baseline rates, TTC/DRAC thresholds,
standards-based thresholds, deployment criteria, and cross-references."""

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
class SafetyThresholdReport:
    framework_steps: int = 0
    baseline_jurisdictions: list[str] = field(default_factory=list)
    ttc_levels: list[str] = field(default_factory=list)
    drac_levels: list[str] = field(default_factory=list)
    standards_covered: list[str] = field(default_factory=list)
    deployment_valid: bool = False
    monitoring_valid: bool = False
    validation_criteria: int = 0
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Safety Thresholds Validation ===",
            f"Framework steps: {self.framework_steps}/4",
            f"Baseline jurisdictions: {self.baseline_jurisdictions or 'none'}",
            f"TTC levels: {self.ttc_levels or 'none'}",
            f"DRAC levels: {self.drac_levels or 'none'}",
            f"Standards: {self.standards_covered or 'none'}",
            f"Deployment criteria: {'✓' if self.deployment_valid else '❌'}",
            f"Monitoring: {'✓' if self.monitoring_valid else '❌'}",
            f"Validation criteria: {self.validation_criteria}/5",
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
    "bayesian-evt": "upstream",
    "standards-research": "upstream",
    "risk-metrics": "sibling",
    "risk-quantification": "downstream",
    "portfolio-ui": "downstream",
}


class SafetyThresholdValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "safety-thresholds" / "SKILL.md"
        self.report = SafetyThresholdReport()

    def validate(self) -> SafetyThresholdReport:
        self._check_framework()
        self._check_baselines()
        self._check_ttc()
        self._check_drac()
        self._check_standards()
        self._check_deployment()
        self._check_monitoring()
        self._check_validation_criteria()
        self._check_cross_references()
        return self.report

    def _check_framework(self):
        content = self.skill_md.read_text()
        for step in ["baseline", "acceptable", "deployment", "validate"]:
            if step in content.lower():
                self.report.framework_steps += 1

    def _check_baselines(self):
        content = self.skill_md.read_text()
        for jur in ["USA", "Canada", "England"]:
            if jur in content:
                self.report.baseline_jurisdictions.append(jur)

    def _check_ttc(self):
        content = self.skill_md.read_text()
        for level in ["critical", "dangerous", "warning", "safe"]:
            if level in content.lower():
                self.report.ttc_levels.append(level)

    def _check_drac(self):
        content = self.skill_md.read_text()
        for level in ["emergency", "hard", "moderate", "light"]:
            if level in content.lower():
                self.report.drac_levels.append(level)

    def _check_standards(self):
        content = self.skill_md.read_text()
        for std in ["UL 4600", "ISO 21448"]:
            if std in content:
                self.report.standards_covered.append(std)

    def _check_deployment(self):
        content = self.skill_md.read_text()
        self.report.deployment_valid = all(kw in content for kw in ["APPROVED", "CONDITIONAL", "DENIED"])

    def _check_monitoring(self):
        content = self.skill_md.read_text()
        self.report.monitoring_valid = "online" in content.lower() or "monitoring" in content.lower()

    def _check_validation_criteria(self):
        content = self.skill_md.read_text()
        for criterion in ["statistical", "practical", "standards", "jurisdiction", "margin"]:
            if criterion in content.lower():
                self.report.validation_criteria += 1

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = SafetyThresholdValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
