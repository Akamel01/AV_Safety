"""Data ingestion validator — checks data sources, schemas, normalization/validation rules,
and cross-references."""

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
class DataIngestReport:
    usa_sources: int = 0
    canada_sources: int = 0
    england_sources: int = 0
    schemas_complete: bool = False
    normalization_valid: bool = False
    validation_valid: bool = False
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Data Ingestion Validation ===",
            f"USA sources: {self.usa_sources}/5",
            f"Canada sources: {self.canada_sources}/3",
            f"England sources: {self.england_sources}/4",
            f"Data schemas: {'✓' if self.schemas_complete else '❌'}",
            f"Normalization: {'✓' if self.normalization_valid else '❌'}",
            f"Validation: {'✓' if self.validation_valid else '❌'}",
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
    "scenario-taxonomy": "downstream",
    "data-exploration": "downstream",
    "bayesian-analysis": "downstream",
    "risk-metrics": "downstream",
    "statistical-validation": "sibling",
    "standards-research": "sibling",
}


class DataIngestValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "data-ingest" / "SKILL.md"
        self.report = DataIngestReport()

    def validate(self) -> DataIngestReport:
        self._count_sources()
        self._check_schemas()
        self._check_normalization()
        self._check_validation()
        self._check_cross_references()
        return self.report

    def _count_sources(self):
        content = self.skill_md.read_text()
        usa = ["FARS", "NASS-CRS", "CISS", "CMFwiki", "GES"]
        canada = ["TC Transportation", "CMFwiki Canada", "ICBC", "SAAQ"]
        england = ["DfT", "JACArP", "Highways England"]
        self.usa_sources = sum(1 for s in usa if s in content)
        self.canada_sources = sum(1 for s in canada if s in content)
        self.england_sources = sum(1 for s in england if s in content)

    def _check_schemas(self):
        content = self.skill_md.read_text()
        self.report.schemas_complete = "crash_id" in content and "vehicle_id" in content

    def _check_normalization(self):
        content = self.skill_md.read_text()
        self.report.normalization_valid = all(kw in content for kw in ["mph", "kph", "jurisdiction", "conversion"])

    def _check_validation(self):
        content = self.skill_md.read_text()
        self.report.validation_valid = all(kw in content for kw in ["crash_id", "date", "lat", "lon"])

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = DataIngestValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
