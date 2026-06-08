"""Validation pipeline — validates all skills in the AV_Safety portfolio."""

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
class ValidationReport:
    total_skills: int = 0
    skills_with_skillemd: list[str] = field(default_factory=list)
    skills_with_driver: list[str] = field(default_factory=list)
    skills_with_refs: list[str] = field(default_factory=list)
    skills_with_subskill: list[str] = field(default_factory=list)
    skills_missing: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Portfolio Validation ===",
            f"Total skills: {self.total_skills}",
        ]
        lines.append(f"SKILL.md: {len(self.skills_with_skillemd)}/{self.total_skills}")
        lines.append(f"driver.py: {len(self.skills_with_driver)}/{self.total_skills}")
        lines.append(f"references/: {len(self.skills_with_refs)}/{self.total_skills}")
        lines.append(f"subskill: {len(self.skills_with_subskill)}/{self.total_skills}")
        if self.skills_missing:
            lines.append(f"Missing items:")
            for s in self.skills_missing:
                lines.append(f"  - {s}")
        if self.issues:
            lines.append(f"Issues: {len(self.issues)}")
            for i in self.issues:
                lines.append(f"  - {i}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  - {w}")
        if not self.issues and not self.warnings:
            lines.append("All checks passed")
        return chr(10).join(lines)


class ValidationPipeline:
    def __init__(self, root=None):
        self.root = root or ROOT
        self.skills_dir = self.root / "skills"
        self.report = ValidationReport()

    def run(self):
        self._scan_skills()
        return self.report

    def _scan_skills(self):
        self.report.total_skills = sum(1 for d in self.skills_dir.iterdir() if d.is_dir())
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            name = skill_dir.name
            if (skill_dir / "SKILL.md").exists():
                self.report.skills_with_skillemd.append(name)
            driver_path = skill_dir / ".claude" / "skills" / f"run-{name}" / "driver.py"
            if (skill_dir / "driver.py").exists() or driver_path.exists():
                self.report.skills_with_driver.append(name)
            refs = skill_dir / "references"
            if refs.exists() and list(refs.iterdir()):
                self.report.skills_with_refs.append(name)
            subskill = skill_dir / ".claude" / "skills" / f"run-{name}" / "SKILL.md"
            if subskill.exists():
                self.report.skills_with_subskill.append(name)
            missing = []
            if not (skill_dir / "SKILL.md").exists():
                missing.append("SKILL.md")
            if not (skill_dir / "driver.py").exists() and not driver_path.exists():
                missing.append("driver.py")
            if not refs.exists() or not list(refs.iterdir()):
                missing.append("references/")
            if not subskill.exists():
                missing.append("subskill")
            if missing:
                self.report.skills_missing.append(f"{name}: {', '.join(missing)}")


if __name__ == "__main__":
    v = ValidationPipeline()
    r = v.run()
    print(r.summary)
    sys.exit(1 if r.skills_missing else 0)
