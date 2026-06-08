"""Risk quantification validator — checks pipeline architecture (7 steps), risk scoring,
report structure, compliance checker, and cross-references."""

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
class RiskQuantReport:
    pipeline_steps: int = 0
    scoring_valid: bool = False
    report_sections: int = 0
    compliance_valid: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Risk Quantification Validation ===",
            f"Pipeline steps: {self.pipeline_steps}/7 {'✓' if self.pipeline_steps >= 7 else '❌'}",
            f"Risk scoring: {'✓' if self.scoring_valid else '❌'}",
            f"Report sections: {self.report_sections}/8 {'✓' if self.report_sections >= 8 else '❌'}",
            f"Compliance checker: {'✓' if self.compliance_valid else '❌'}",
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


EXPECTED_STEPS = ["kinematics", "indicators", "monte carlo", "bayesian", "collision", "threshold", "portfolio"]
EXPECTED_CROSS_REFS = {
    "kinematics-engine": "upstream",
    "indicator-computation": "upstream",
    "stochastic-simulation": "upstream",
    "bayesian-evt": "upstream",
    "collision-modeling": "upstream",
    "safety-thresholds": "upstream",
    "portfolio-ui": "downstream",
    "portfolio-deploy": "downstream",
}


class RiskQuantValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "risk-quantification" / "SKILL.md"
        self.report = RiskQuantReport()

    def validate(self) -> RiskQuantReport:
        self._check_pipeline()
        self._check_scoring()
        self._check_report()
        self._check_compliance()
        self._check_cross_references()
        return self.report

    def _check_pipeline(self):
        content = self.skill_md.read_text().lower()
        for step in EXPECTED_STEPS:
            if step.replace(" ", "") in content.replace(" ", "") or step in content:
                self.report.pipeline_steps += 1

    def _check_scoring(self):
        content = self.skill_md.read_text()
        self.report.scoring_valid = all(kw in content for kw in ["weights", "risk_score", "collision_rate", "severity"])

    def _check_report(self):
        content = self.skill_md.read_text()
        sections = ["executive summary", "methodology", "scenario", "cross-scenario", "threshold", "recommendation", "uncertainty", "appendix"]
        self.report.report_sections = sum(1 for s in sections if s.lower() in content.lower())

    def _check_compliance(self):
        content = self.skill_md.read_text()
        self.report.compliance_valid = all(kw in content for kw in ["FULL", "CONDITIONAL", "NON_COMPLIANT"])

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = RiskQuantValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
