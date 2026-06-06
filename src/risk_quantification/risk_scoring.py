"""Core risk scoring with weighted multi-criteria evaluation.

Integrates collision rate, severity, uncertainty, and threshold
compliance into a unified risk score per NHTSA ES-28 guidance.
"""

from __future__ import annotations

from typing import Any


class RiskScorer:
    """Compute unified risk scores from multi-criteria inputs.

    Uses weighted combination of:
    - collision_rate (weight: 0.3)
    - severity (weight: 0.3)
    - uncertainty (weight: 0.2)
    - threshold_compliance (weight: 0.2)

    Weight Derivation Methodology:
    The current weights (0.3/0.3/0.2/0.2) are preliminary defaults assigned by
    the AV Safety engineering team pending formal derivation. In the final design,
    weights should be determined through one or more of:
    - Pairwise comparison matrix (Analytic Hierarchy Process) per ISO 21448 (SOTIF)
    - Logistic regression coefficients trained on historical crash/fars/CISS datasets
    - Expert elicitation (Delphi method) with ≥5 subject-matter experts
    - Multi-criteria decision analysis (MCDA) with sensitivity analysis
    The Blueprint (doc/design/AVSafety-Blueprint.md) notes these are "arbitrary"
    placeholders and should be replaced by data-driven weights before production use.
    See `validate_weights()` below for a validation helper.
    """

    DEFAULT_WEIGHTS = {
        "collision_rate": 0.3,
        "severity": 0.3,
        "uncertainty": 0.2,
        "threshold_compliance": 0.2,
    }

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        total = sum(self.weights.values())
        if total != 1.0:
            # Normalize if user provided weights don't sum to 1
            self.weights = {k: v / total for k, v in self.weights.items()}

    def score(
        self,
        collision_rate: float,
        severity: float,
        uncertainty: float,
        safety_margin_percent: float,
    ) -> dict[str, Any]:
        """Compute unified risk score.

        Args:
            collision_rate: Normalized collision rate (0-1 scale recommended).
            severity: Severity score (0-1 scale).
            uncertainty: Uncertainty measure (0-1, higher = less certain).
            safety_margin_percent: Safety margin from threshold checker (0-100).

        Returns:
            Dict with overall_risk_score, risk_level, confidence, and
            component breakdown.
        """
        # Normalize collision rate to 0-1 scale if needed
        if collision_rate > 1.0:
            collision_rate_norm = 1.0 - (1.0 / (1.0 + collision_rate))
        else:
            collision_rate_norm = min(collision_rate, 1.0)

        # Normalize safety margin to compliance score (0-1, 1 = fully compliant)
        compliance_score = min(max(safety_margin_percent / 100.0, 0.0), 1.0)
        # Invert: higher margin = lower risk contribution
        threshold_component = 1.0 - compliance_score

        # Component scores keyed to match self.weights keys
        component_scores = {
            "collision_rate": collision_rate_norm,
            "severity": severity,
            "uncertainty": uncertainty,
            "threshold_compliance": threshold_component,
        }

        weighted_score = sum(
            self.weights[k] * component_scores[k]
            for k in self.weights
        )

        risk_level = self._classify_risk(weighted_score)

        return {
            "overall_risk_score": round(weighted_score, 6),
            "risk_level": risk_level,
            "confidence": 1.0 - uncertainty,
            "component_scores": component_scores,
            "weights": self.weights,
            "recommendation": self._get_recommendation(
                weighted_score, safety_margin_percent
            ),
        }

    def score_batch(
        self,
        scenarios: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Score multiple scenarios in batch.

        Args:
            scenarios: List of dicts with keys:
                collision_rate, severity, uncertainty, safety_margin_percent

        Returns:
            List of scored result dicts.
        """
        return [self.score(**s) for s in scenarios]

    def _classify_risk(self, score: float) -> str:
        """Classify risk level from score (0-1 scale)."""
        if score < 0.2:
            return "LOW"
        elif score < 0.5:
            return "MEDIUM"
        elif score < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"

    def _get_recommendation(self, score: float, margin: float) -> str:
        """Get deployment recommendation from score and margin."""
        if score < 0.2 and margin > 15.0:
            return "APPROVED"
        elif score < 0.5 and margin > 0:
            return "CONDITIONAL"
        elif score < 0.8:
            return "CONDITIONAL (extended_testing_required)"
        else:
            return "DENIED"
