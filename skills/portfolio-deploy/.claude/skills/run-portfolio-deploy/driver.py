"""Portfolio deploy validator — checks deployment targets, CI/CD pipeline,
deployment checklist, and cross-references."""

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
class DeployReport:
    deployment_targets: list[str] = field(default_factory=list)
    ci_cd_steps: list[str] = field(default_factory=list)
    checklist_items: list[str] = field(default_factory=list)
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        target_str = f"{len(self.deployment_targets)}/3"
        target_check = "" if len(self.deployment_targets) == 3 else ""
        ci_str = f"{len(self.ci_cd_steps)}/4"
        ci_check = "" if len(self.ci_cd_steps) >= 4 else ""
        checklist_str = f"{len(self.checklist_items)}/10"
        checklist_check = "" if len(self.checklist_items) >= 10 else ""

        lines = [
            "=== Portfolio Deploy Validation ===",
            f"Deployment targets: {target_str} ({', '.join(self.deployment_targets)})"
            if self.deployment_targets else
            "Deployment targets: 0/3 (none found)",
            f"CI/CD pipeline: {ci_str} ({', '.join(self.ci_cd_steps)})",
            f"Deployment checklist: {checklist_str}",
            "Cross-references:",
        ]
        for skill, rel in self.cross_refs.items():
            lines.append(f"  {skill}: ({rel})")
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


EXPECTED_CROSS_REFS = {
    "portfolio-ui": "upstream",
    "risk-quantification": "upstream",
    "standards-research": "upstream",
}

DEPLOYMENT_TARGETS = ["portfolio ui", "pipeline api", "documentation"]
CI_CD_STEPS = ["lint", "test", "build", "deploy"]
CHECKLIST_ITEMS = [
    "tests pass", "ui builds", "pipeline results", "documentation generated",
    "environment variables", "https", "custom domain", "monitoring",
    "backup strategy", "rollback",
]


class DeployValidator:
    def __init__(self, root=None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "portfolio-deploy" / "SKILL.md"
        self.report = DeployReport()

    def validate(self) -> DeployReport:
        self._check_targets()
        self._check_ci_cd()
        self._check_deploy_checklist()
        self._check_cross_references()
        self._check_deploy_dir()
        return self.report

    def _check_targets(self):
        content = self.skill_md.read_text().lower()
        for target in DEPLOYMENT_TARGETS:
            if target in content:
                self.report.deployment_targets.append(target)

    def _check_ci_cd(self):
        content = self.skill_md.read_text().lower()
        for step in CI_CD_STEPS:
            if step in content:
                self.report.ci_cd_steps.append(step)

    def _check_deploy_checklist(self):
        content = self.skill_md.read_text().lower()
        for item in CHECKLIST_ITEMS:
            if item in content:
                self.report.checklist_items.append(item)

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill.lower() in content.lower():
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "missing"
                self.report.warnings.append(f"No cross-reference to {skill}")

    def _check_deploy_dir(self):
        deploy_dir = self.root / "deploy"
        if not deploy_dir.exists():
            self.report.issues.append("deploy/ directory not found — no deployment artifacts")
        else:
            artifacts = list(deploy_dir.glob("**/*"))
            if not artifacts:
                self.report.warnings.append("deploy/ directory exists but is empty")


if __name__ == "__main__":
    v = DeployValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
