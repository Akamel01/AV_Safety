"""Statistical validation validator — checks validation framework, goodness-of-fit tests,
hypothesis tests, benchmarks, sensitivity analysis, and cross-references."""

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
class StatsValidatorReport:
    validation_categories: int = 0
    gof_tests: list[str] = field(default_factory=list)
    hypothesis_tests: list[str] = field(default_factory=list)
    benchmark_count: int = 0
    sensitivity_methods: list[str] = field(default_factory=list)
    report_sections: int = 0
    quality_standards: list[str] = field(default_factory=list)
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Statistical Validation Validation ===",
            f"Validation categories: {self.validation_categories}/5",
            f"GoF tests: {self.gof_tests or 'none'}",
            f"Hypothesis tests: {self.hypothesis_tests or 'none'}",
            f"Benchmarks: {self.benchmark_count}",
            f"Sensitivity methods: {self.sensitivity_methods or 'none'}",
            f"Report sections: {self.report_sections}/6",
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
    "risk-quantification": "upstream",
    "safety-thresholds": "upstream",
    "data-ingest": "upstream",
    "risk-metrics": "sibling",
    "collision-modeling": "sibling",
}


class StatsValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "statistical-validation" / "SKILL.md"
        self.report = StatsValidatorReport()

    def validate(self) -> StatsValidatorReport:
        self._count_categories()
        self._check_gof()
        self._check_hypothesis()
        self._count_benchmarks()
        self._check_sensitivity()
        self._check_report_sections()
        self._check_cross_references()
        return self.report

    def _count_categories(self):
        content = self.skill_md.read_text()
        cats = ["Model Validation", "Statistical Validation", "Benchmark Validation", "Sensitivity Validation", "Reproducibility Validation"]
        self.report.validation_categories = sum(1 for c in cats if c in content)

    def _check_gof(self):
        content = self.skill_md.read_text()
        for test in ["Kolmogorov-Smirnov", "Shapiro-Wilk", "Anderson-Darling", "Chi-square"]:
            if test in content:
                self.report.gof_tests.append(test)

    def _check_hypothesis(self):
        content = self.skill_md.read_text()
        for test in ["z-test", "chi-square", "homogeneity"]:
            if test in content.lower():
                self.report.hypothesis_tests.append(test)

    def _count_benchmarks(self):
        content = self.skill_md.read_text()
        self.report.benchmark_count = sum(1 for b in ["NHTSA", "UK", "Canada", "TTC", "braking", "friction"] if b in content)

    def _check_sensitivity(self):
        content = self.skill_md.read_text()
        for method in ["OAT", "Sobol"]:
            if method in content:
                self.report.sensitivity_methods.append(method)

    def _check_report_sections(self):
        content = self.skill_md.read_text()
        sections = ["Summary", "Model validation", "Hypothesis", "Benchmark", "Sensitivity", "Key findings"]
        self.report.report_sections = sum(1 for s in sections if s in content)

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = StatsValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
