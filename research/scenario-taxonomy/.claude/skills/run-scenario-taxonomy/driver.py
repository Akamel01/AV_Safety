"""Scenario taxonomy validator — audits all 8 conflict types, sub-categories,
severity spectra, cross-skill references, and scenario JSON files."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _find_root():
    """Walk up from this file to find the AV_Safety root (marked by single-scenario-demo/)."""
    p = Path(__file__).resolve()
    for _ in range(10):
        if (p / "single-scenario-demo").is_dir():
            return p
        p = p.parent
    return Path.cwd()


ROOT = _find_root()


@dataclass
class TaxonomyReport:
    conflict_types: int = 0
    sub_categories: int = 0
    severity_defined: bool = False
    cross_refs: dict[str, bool] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    scenario_files: int = 0
    scenario_compliant: int = 0

    @property
    def summary(self) -> str:
        lines = [
            "=== Scenario Taxonomy Validation ===",
            f"Conflict types: {self.conflict_types}/8",
            f"Sub-categories: {self.sub_categories} total (avg {self.sub_categories / max(self.conflict_types, 1):.1f}/type)",
            f"Severity spectrum: {'present' if self.severity_defined else 'MISSING'}",
            "Cross-references:",
        ]
        for skill, valid in self.cross_refs.items():
            lines.append(f"  {skill}: {'✓' if valid else '✗'}")
        if self.scenario_files:
            lines.append(f"Scenario files: {self.scenario_compliant}/{self.scenario_files} compliant")
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


REQUIRED_CONFLICT_TYPES = {
    "crossing", "merging", "diverging", "weaving",
    "rear-end", "sideswipe", "right-angle", "opposing-left-turn",
}

REQUIRED_CROSS_REFS = [
    "kinematics-engine", "indicator-computation", "stochastic-simulation",
    "3d-animation", "portfolio-ui", "data-ingest", "risk-metrics",
]

SCENARIO_JSON_FIELDS = {
    "conflict_type", "sub_category",
    "road_geometry", "road_users",
}


class TaxonomyValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "scenario-taxonomy" / "SKILL.md"
        self.references_md = self.root / "skills" / "scenario-taxonomy" / "references" / "sub-categories.md"
        self.report = TaxonomyReport()

    def validate(self) -> TaxonomyReport:
        self._check_conflict_types()
        self._check_severity_spectrum()
        self._check_cross_references()
        self._check_scenario_files()
        return self.report

    def _check_conflict_types(self):
        """Check all 8 conflict types and sub-category counts."""
        content = self.skill_md.read_text()

        # Parse conflict types from headers (### N. Name format)
        types_found = set()
        for line in content.splitlines():
            line_clean = re.sub(r'[^a-z]', '', line.lower())
            for expected in REQUIRED_CONFLICT_TYPES:
                if expected.replace("-", "") in line_clean:
                    types_found.add(expected)

        self.report.conflict_types = len(types_found)
        missing = REQUIRED_CONFLICT_TYPES - types_found
        if missing:
            self.report.issues.append(f"Missing conflict types: {missing}")

        # Count sub-categories (lines starting with "- ")
        subcats = 0
        current_type = None
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("### "):
                current_type = stripped
            elif stripped.startswith("- ") and current_type:
                subcats += 1
        self.report.sub_categories = subcats

        # Check minimum 4 per type
        type_subcats: dict[str, int] = {}
        current_type = None
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("### "):
                current_type = stripped.replace("### ", "").strip()
                type_subcats[current_type] = 0
            elif stripped.startswith("- ") and current_type:
                type_subcats[current_type] += 1

        for ctype, count in type_subcats.items():
            if count < 4:
                self.report.warnings.append(f"{ctype}: only {count} sub-categories (min 4)")

    def _check_severity_spectrum(self):
        """Check severity spectrum is defined."""
        skill_content = self.skill_md.read_text()
        ref_content = self.references_md.read_text() if self.references_md.exists() else ""

        if "benign" in skill_content.lower() and "extreme" in skill_content.lower():
            self.report.severity_defined = True
        else:
            self.report.issues.append("Severity spectrum not defined in SKILL.md")

    def _check_cross_references(self):
        """Check references to other skills."""
        # Check skill SKILL.md mentions related skills
        skill_content = self.skill_md.read_text()
        for skill in REQUIRED_CROSS_REFS:
            if skill in skill_content:
                self.report.cross_refs[skill] = True
            else:
                self.report.cross_refs[skill] = False
                self.report.warnings.append(f"No cross-reference to {skill} in SKILL.md")

    def _check_scenario_files(self):
        """Validate scenario JSON files in single-scenario-demo."""
        demo_dir = self.root / "single-scenario-demo" / "data"
        if not demo_dir.exists():
            self.report.warnings.append("single-scenario-demo/data/ does not exist")
            return

        for json_file in demo_dir.glob("*.json"):
            self.report.scenario_files += 1
            try:
                data = json.loads(json_file.read_text())
                # Fields may be under "scenario" key or at top level
                scenario = data.get("scenario", data)
                all_keys = set(scenario.keys()) | set(data.keys())
                missing_fields = SCENARIO_JSON_FIELDS - all_keys
                if not missing_fields:
                    self.report.scenario_compliant += 1
                else:
                    self.report.warnings.append(f"{json_file.name}: missing fields {missing_fields}")
            except json.JSONDecodeError as e:
                self.report.issues.append(f"{json_file.name}: invalid JSON — {e}")


if __name__ == "__main__":
    validator = TaxonomyValidator()
    report = validator.validate()
    print(report.summary)
    sys.exit(1 if report.issues else 0)
