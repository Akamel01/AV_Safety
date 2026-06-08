"""Data exploration EDA validator — checks pipeline completeness, reference
implementation correctness, cross-references, and data availability."""

from __future__ import annotations

import json
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
class EDAReport:
    pipeline_stages: int = 0
    pipeline_complete: bool = False
    references_valid: bool = False
    reference_has_code: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)  # skill -> relationship
    data_raw_size: int = 0
    data_processed_size: int = 0
    notebooks_count: int = 0
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Data Exploration Validation ===",
            f"EDA pipeline stages: {self.pipeline_stages}/5",
            f"Pipeline complete: {'yes' if self.pipeline_complete else 'no'}",
            f"Reference implementations: {'present' if self.references_valid else 'missing'}",
            f"Reference code quality: {'has code' if self.reference_has_code else 'no code'}",
            "Cross-references:",
        ]
        for skill, rel in self.cross_refs.items():
            lines.append(f"  {skill}: {rel}")
        lines.append("Data availability:")
        lines.append(f"  data/raw/: {self.data_raw_size} files")
        lines.append(f"  data/processed/: {self.data_processed_size} files")
        lines.append(f"  notebooks/: {self.notebooks_count} files")
        if self.issues:
            lines.append(f"Issues found: {len(self.issues)}")
            for issue in self.issues:
                lines.append(f"  ❌ {issue}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠️ {w}")
        if not self.issues and not self.warnings:
            lines.append("All checks passed ✓")
        return "\n".join(lines)


EXPECTED_STAGES = [
    "summary_stats", "distribution_analysis", "correlation_analysis",
    "segmentation", "visualization",
]

EXPECTED_CROSS_REFS = {
    "data-ingest": "upstream",
    "bayesian-analysis": "downstream",
    "risk-metrics": "downstream",
    "scenario-taxonomy": "taxonomy segmentation",
    "stochastic-simulation": "distribution sampling",
}

PIPELINE_CODE_INDICATORS = [
    "EDAEngine", "SummaryStatistics", "DistributionAnalysis",
    "compute_correlation_matrix", "segment_by_conflict_type",
    "EDAVisualization",
]


class EDAValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "data-exploration" / "SKILL.md"
        self.references_md = self.root / "skills" / "data-exploration" / "references" / "implementation-details.md"
        self.report = EDAReport()

    def validate(self) -> EDAReport:
        self._check_pipeline_stages()
        self._check_references()
        self._check_cross_references()
        self._check_data_availability()
        return self.report

    def _check_pipeline_stages(self):
        content = self.skill_md.read_text().lower()
        # Map expected stages to more flexible keywords
        stage_keywords = {
            "summary_stats": ["summary_stat", "descriptive", "overall_summary", "summary statistics"],
            "distribution_analysis": ["distribution", "histogram", "kde", "gpd"],
            "correlation_analysis": ["correlation", "pearson", "spearman"],
            "segmentation": ["segmentation", "grouped by", "stratification"],
            "visualization": ["visualization", "plot", "heatmap", "bar chart"],
        }
        for stage, keywords in stage_keywords.items():
            if any(kw in content for kw in keywords):
                self.report.pipeline_stages += 1
        self.report.pipeline_complete = self.report.pipeline_stages >= 5
        if not self.report.pipeline_complete:
            missing = [stage for stage, keywords in stage_keywords.items()
                       if not any(kw in content for kw in keywords)]
            self.report.issues.append(f"Missing pipeline stages: {missing}")

    def _check_references(self):
        if not self.references_md.exists():
            self.report.issues.append("references/implementation-details.md does not exist")
            return
        content = self.references_md.read_text()
        # Check for code blocks (implementation details should have code)
        code_count = content.count("```") // 2  # pairs of ```
        self.report.references_valid = code_count >= 3
        self.report.reference_has_code = any(
            indicator in content for indicator in PIPELINE_CODE_INDICATORS
        )
        if not self.report.references_valid:
            self.report.warnings.append("Reference has <3 code blocks — insufficient implementation detail")

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = f"missing ({rel})"
                self.report.warnings.append(f"No cross-reference to {skill}")

    def _check_data_availability(self):
        raw_dir = self.root / "data" / "raw"
        processed_dir = self.root / "data" / "processed"
        notebooks_dir = self.root / "notebooks"

        if raw_dir.exists():
            self.report.data_raw_size = sum(1 for f in raw_dir.iterdir() if f.is_file())
        if processed_dir.exists():
            self.report.data_processed_size = sum(1 for f in processed_dir.iterdir() if f.is_file())
        if notebooks_dir.exists():
            self.report.notebooks_count = sum(1 for f in notebooks_dir.iterdir() if f.suffix == '.ipynb')

        if self.report.data_processed_size == 0:
            self.report.warnings.append("No data in data/processed/ — EDA has no input")


if __name__ == "__main__":
    validator = EDAValidator()
    report = validator.validate()
    print(report.summary)
    sys.exit(1 if report.issues else 0)
