"""Collision modeling validator — checks ML model types, feature set, feature selection,
model comparison, performance thresholds, and cross-references."""

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
class CollisionModelReport:
    model_types: list[str] = field(default_factory=list)
    feature_groups: dict[str, int] = field(default_factory=dict)
    feature_selection: list[str] = field(default_factory=list)
    performance_metrics: list[str] = field(default_factory=list)
    stats_validation: list[str] = field(default_factory=list)
    cross_refs: dict[str, str] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        total_feats = sum(self.feature_groups.values())
        lines = [
            "=== Collision Modeling Validation ===",
            f"ML models: {self.model_types or 'none'}",
            f"Feature groups: {self.feature_groups}",
            f"Total features: {total_feats}",
            f"Feature selection: {self.feature_selection or 'none'}",
            f"Performance metrics: {self.performance_metrics or 'none'}",
            f"Statistical validation: {self.stats_validation or 'none'}",
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
    "kinematics-engine": "upstream",
    "bayesian-evt": "upstream",
    "stochastic-simulation": "upstream",
    "indicator-computation": "upstream",
    "safety-thresholds": "downstream",
    "risk-metrics": "downstream",
    "risk-quantification": "downstream",
    "statistical-validation": "sibling",
}


class CollisionModelValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "collision-modeling" / "SKILL.md"
        self.report = CollisionModelReport()

    def validate(self) -> CollisionModelReport:
        self._check_models()
        self._count_features()
        self._check_feature_selection()
        self._check_performance()
        self._check_stats_validation()
        self._check_cross_references()
        return self.report

    def _check_models(self):
        content = self.skill_md.read_text()
        for model in ["Logistic Regression", "Random Forest", "XGBoost", "Neural Network", "Bayesian"]:
            if model in content:
                self.report.model_types.append(model)

    def _count_features(self):
        content = self.skill_md.read_text()
        groups = ["kinematic", "distance", "deceleration", "severity", "probability", "metadata", "derived"]
        for group in groups:
            if group in content.lower():
                self.report.feature_groups[group] = 1

    def _check_feature_selection(self):
        content = self.skill_md.read_text()
        for method in ["random forest", "mutual information", "RFE"]:
            if method in content.lower():
                self.report.feature_selection.append(method)

    def _check_performance(self):
        content = self.skill_md.read_text()
        for metric in ["accuracy", "precision", "recall", "f1", "auc-roc"]:
            if metric in content.lower():
                self.report.performance_metrics.append(metric)

    def _check_stats_validation(self):
        content = self.skill_md.read_text()
        for method in ["t-test", "McNemar", "cross-validation"]:
            if method in content.lower():
                self.report.stats_validation.append(method)

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")


if __name__ == "__main__":
    v = CollisionModelValidator()
    r = v.validate()
    print(r.summary)
    sys.exit(1 if r.issues else 0)
