"""Bayesian analysis validator — checks model types, workflow steps, output format,
prior elicitation, and cross-references."""

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
class BayesianReport:
    model_types: int = 0
    workflow_steps: int = 0
    output_format_valid: bool = False
    prior_elicitation: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Bayesian Analysis Validation ===",
            f"Model types: {self.model_types}/5 {'✓' if self.model_types >= 5 else '❌'}",
            f"Workflow steps: {self.workflow_steps}/5 {'✓' if self.workflow_steps >= 5 else '❌'}",
            f"Output format: {'✓' if self.output_format_valid else '❌'}",
            f"Prior elicitation: {'✓' if self.prior_elicitation else '❌'}",
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


EXPECTED_MODELS = ["Bayesian collision rate", "Hierarchical jurisdiction", "Bayesian model comparison",
                   "Bayesian safety threshold", "Meta-analysis"]
EXPECTED_CROSS_REFS = {
    "bayesian-evt": "sibling",
    "stochastic-simulation": "upstream",
    "safety-thresholds": "downstream",
    "risk-metrics": "downstream",
    "risk-quantification": "downstream",
    "scenario-taxonomy": "upstream",
    "data-ingest": "upstream",
}


class BayesianValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "bayesian-analysis" / "SKILL.md"
        self.report = BayesianReport()

    def validate(self) -> BayesianReport:
        self._count_models()
        self._check_workflow()
        self._check_output_format()
        self._check_prior_elicitation()
        self._check_cross_references()
        return self.report

    def _count_models(self):
        content = self.skill_md.read_text()
        for model in EXPECTED_MODELS:
            if model in content:
                self.report.model_types += 1

    def _check_workflow(self):
        content = self.skill_md.read_text()
        steps = ["Define", "Specify", "Fit", "Validate", "Document"]
        self.report.workflow_steps = sum(1 for s in steps if s in content)

    def _check_output_format(self):
        content = self.skill_md.read_text()
        required = ["likelihood", "prior", "diagnostics", "posterior", "comparison"]
        self.report.output_format_valid = all(r in content.lower() for r in required)

    def _check_prior_elicitation(self):
        content = self.skill_md.read_text()
        self.report.prior_elicitation = "prior" in content.lower() and ("elicitation" in content.lower() or "literature" in content.lower())

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = BayesianValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
