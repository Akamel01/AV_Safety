"""Bayesian EVT validator — checks GPD model, hierarchical structure,
MRL threshold selection, validation diagnostics, cross-references,
and reference implementation correctness."""

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
class EVTReport:
    gpd_model_correct: bool = False
    gpd_formula_valid: bool = False
    gpd_params_defined: int = 0
    hierarchical_levels: int = 0
    mrl_present: bool = False
    mrl_stability: bool = False
    mrl_qqplot: bool = False
    diagnostics: dict[str, bool] = field(default_factory=dict)  # name -> found
    priors_defined: dict[str, str] = field(default_factory=dict)  # param -> distribution
    cross_refs: dict[str, str] = field(default_factory=dict)
    ref_implementation_valid: bool = False
    ref_typos: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        lines = [
            "=== Bayesian EVT Validation ===",
            f"GPD model: {'✓ correct' if self.gpd_model_correct else '❌ incorrect'}",
            f"  Formula: {'✓ valid' if self.gpd_formula_valid else '❌ invalid'}",
            f"  Parameters defined: {self.gpd_params_defined}",
            f"Hierarchical levels: {self.hierarchical_levels}/4 {'✓' if self.hierarchical_levels >= 4 else '❌'}",
            f"MRL threshold selection: {'✓ present' if self.mrl_present else '❌ missing'}",
        ]
        if self.mrl_present:
            lines.append(f"  Stability analysis: {'✓' if self.mrl_stability else '❌'}")
            lines.append(f"  QQ-plot validation: {'✓' if self.mrl_qqplot else '❌'}")
        lines.append("Validation diagnostics:")
        for name, found in self.diagnostics.items():
            lines.append(f"  {name}: {'✓' if found else '❌'}")
        lines.append(f"Prior specifications: {'✓' if self.priors_defined else '❌'}")
        for param, dist in self.priors_defined.items():
            lines.append(f"  {param}: {dist}")
        lines.append("Cross-references:")
        for skill, rel in self.cross_refs.items():
            lines.append(f"  {skill}: {'✓' if rel != '❌' else '❌'} ({rel})")
        lines.append(f"Reference implementation: {'✓' if self.ref_implementation_valid else '❌'}")
        if self.ref_implementation_valid:
            if self.ref_typos:
                lines.append(f"  Typos found: {self.ref_typos}")
            else:
                lines.append("  No API typos, GPD likelihood correct")
        if self.issues:
            lines.append(f"Issues found: {len(self.issues)}")
            for issue in self.issues:
                lines.append(f"  ❌ {issue}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠️ {w}")
        if not self.issues and not self.warnings and not self.ref_typos:
            lines.append("All checks passed ✓")
        return "\n".join(lines)


EXPECTED_HIERARCHICAL_LEVELS = ["scenario", "conflict_type", "jurisdiction", "cross-jurisdiction"]

EXPECTED_DIAGNOSTICS = ["r-hat", "ESS", "LOO", "WAIC", "PPC"]

EXPECTED_PRIORS = {
    "xi": "Normal",
    "sigma": "HalfNormal",
    "mu_xi": "Normal",
    "sigma_xi": "HalfNormal",
    "collision_rate": "Beta",
}

EXPECTED_CROSS_REFS = {
    "stochastic-simulation": "upstream",
    "kinematics-engine": "upstream",
    "indicator-computation": "upstream",
    "bayesian-analysis": "sibling",
    "safety-thresholds": "downstream",
    "risk-metrics": "downstream",
    "risk-quantification": "sibling",
}

KNOWN_TYPOS = [
    "sample_posterior_predictible",  # should be sample_posterior_predictive
]

GPD_CODE_INDICATORS = [
    "pm.GPD", "build_bayesian_evt_model", "pm.sample",
    "mrl_threshold_selection", "qq_plot_validation",
]


class EVTValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.skill_md = self.root / "skills" / "bayesian-evt" / "SKILL.md"
        self.references_md = self.root / "skills" / "bayesian-evt" / "references" / "implementation-details.md"
        self.report = EVTReport()

    def validate(self) -> EVTReport:
        self._check_gpd_model()
        self._check_hierarchical_structure()
        self._check_mrl_selection()
        self._check_diagnostics()
        self._check_priors()
        self._check_cross_references()
        self._check_reference_implementation()
        return self.report

    def _check_gpd_model(self):
        content = self.skill_md.read_text()
        # Check GPD formula
        self.report.gpd_formula_valid = "1/σ" in content and "ξ" in content
        # Check parameter constraints (ξ > 0 heavy, ξ = 0 exponential, ξ < 0 bounded)
        self.report.gpd_params_defined = 0
        for param in ["ξ", "sigma", "scale", "shape"]:
            if param in content:
                self.report.gpd_params_defined += 1
        self.report.gpd_model_correct = self.report.gpd_formula_valid and self.report.gpd_params_defined >= 2

    def _check_hierarchical_structure(self):
        content = self.skill_md.read_text().lower()
        # Normalize: remove underscores and hyphens for flexible matching
        norm_content = content.replace("_", "").replace("-", "")
        for level in EXPECTED_HIERARCHICAL_LEVELS:
            norm_level = level.replace("_", "").replace("-", "")
            if norm_level in norm_content or level in content.lower():
                self.report.hierarchical_levels += 1

    def _check_mrl_selection(self):
        content = self.skill_md.read_text()
        self.report.mrl_present = "MRL" in content or "mean residual" in content.lower()
        self.report.mrl_stability = "stability" in content.lower()
        self.report.mrl_qqplot = "QQ" in content or "qq-plot" in content.lower()

    def _check_diagnostics(self):
        content = self.skill_md.read_text()
        for diag in EXPECTED_DIAGNOSTICS:
            self.report.diagnostics[diag] = diag.lower() in content.lower() or diag in content

    def _check_priors(self):
        content = self.skill_md.read_text()
        for param, dist_type in EXPECTED_PRIORS.items():
            # Check if param has a distribution mentioned
            # Look for patterns like "Normal(0, 1)" or "HalfNormal"
            has_dist = dist_type in content
            if has_dist and param in content:
                self.report.priors_defined[param] = dist_type

    def _check_cross_references(self):
        content = self.skill_md.read_text()
        for skill, rel in EXPECTED_CROSS_REFS.items():
            if skill in content:
                self.report.cross_refs[skill] = rel
            else:
                self.report.cross_refs[skill] = "❌"
                self.report.warnings.append(f"No cross-reference to {skill}")

    def _check_reference_implementation(self):
        if not self.references_md.exists():
            self.report.issues.append("references/implementation-details.md does not exist")
            return

        content = self.references_md.read_text()

        # Check for known typos
        for typo in KNOWN_TYPOS:
            if typo in content:
                self.report.ref_typos.append(typo)

        # Check for key implementation components
        has_code = any(ind in content for ind in GPD_CODE_INDICATORS)

        # Check GPD likelihood is present
        has_gpd_likelihood = "pm.GPD" in content

        self.report.ref_implementation_valid = has_code and has_gpd_likelihood and len(self.report.ref_typos) == 0

        if self.report.ref_typos:
            self.report.issues.append(f"Reference implementation has typos: {self.report.ref_typos}")

        if not has_gpd_likelihood:
            self.report.issues.append("No pm.GPD likelihood in reference implementation")

        if not has_code:
            self.report.warnings.append("Reference has no key code indicators")


if __name__ == "__main__":
    validator = EVTValidator()
    report = validator.validate()
    print(report.summary)
    sys.exit(1 if report.issues or report.ref_typos else 0)
