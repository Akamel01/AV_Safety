/**
 * risk-scoring.js — Risk Scoring Pipeline
 *
 * Integrates kinematics, Monte Carlo, Bayesian EVT, and safety thresholds
 * to compute comprehensive risk scores per NHTSA ES-28 and UL 4600 standards.
 *
 * Based on risk-quantification skill:
 *   https://github.com/Akamel01/AV_Safety/skills/risk-quantification/SKILL.md
 */

class RiskScorer {
  constructor(params) {
    this.params = params || {
      weights: {
        collision_rate: 0.30,
        severity: 0.30,
        uncertainty: 0.20,
        threshold_compliance: 0.20,
      },
      thresholds: {
        low: 20,
        moderate: 40,
        high: 60,
        critical: 100,
      },
    };
  }

  /**
   * Compute composite risk score (0-100).
   * @param {Object} monteCarloResults — Monte Carlo Engine results
   * @param {Object} bayesianEVT — BayesianEVT output
   * @param {Object} indicators — Indicator aggregation
   * @param {Object} scenarioSpec — Scenario parameters
   * @returns {Object} riskScore
   */
  compute(monteCarloResults, bayesianEVT, indicators, scenarioSpec) {
    const w = this.params.weights;

    // Component 1: Collision rate score (0-100)
    const collisionScore = this._computeCollisionScore(
      monteCarloResults?.collisionRate || 0,
      monteCarloResults?.collapsedResults?.ttc || null
    );

    // Component 2: Severity score (0-100)
    const severityScore = this._computeSeverityScore(
      monteCarloResults?.collapsedResults?.severity || null,
      bayesianEVT?.severity?.expected_severity || null,
      indicators?.aggregated?.delta_v || 0
    );

    // Component 3: Uncertainty score (0-100)
    const uncertaintyScore = this._computeUncertaintyScore(
      bayesianEVT?.gpd_parameters || null,
      monteCarloResults?.n || 0
    );

    // Component 4: Threshold compliance score (0-100)
    const thresholdScore = this._computeThresholdScore(
      indicators,
      monteCarloResults?.collapsedResults?.ttc || null,
      scenarioSpec
    );

    // Composite score
    const composite = Math.min(
      100,
      Math.max(0,
        w.collision_rate * collisionScore +
        w.severity * severityScore +
        w.uncertainty * uncertaintyScore +
        w.threshold_compliance * thresholdScore
      )
    );

    // Classification
    const classification = this._classifyRisk(composite);

    return {
      composite: {
        score: Math.round(composite * 100) / 100,
        classification,
        weights: this.params.weights,
      },
      components: {
        collision_rate: {
          score: Math.round(collisionScore * 100) / 100,
          collisionRate: monteCarloResults?.collisionRate || 0,
          bayesianRate: bayesianEVT?.collision_rate?.estimate || 0,
          ttc_min: monteCarloResults?.collapsedResults?.ttc?.min || null,
          ttc_median: monteCarloResults?.collapsedResults?.ttc?.median || null,
        },
        severity: {
          score: Math.round(severityScore * 100) / 100,
          delta_v_p50: monteCarloResults?.collapsedResults?.delta_v?.p50 || 0,
          delta_v_p95: monteCarloResults?.collapsedResults?.delta_v?.p95 || 0,
          bayes_fatal: bayesianEVT?.severity?.expected_severity?.fatal_probability || 0,
          bayes_injury: bayesianEVT?.severity?.expected_severity?.injury_probability || 0,
          bayes_mai3: bayesianEVT?.severity?.expected_severity?.mai3_plus_probability || 0,
        },
        uncertainty: {
          score: Math.round(uncertaintyScore * 100) / 100,
          xi_estimate: bayesianEVT?.gpd_parameters?.xi?.estimate || null,
          sigma_estimate: bayesianEVT?.gpd_parameters?.sigma?.estimate || null,
          xi_ci95: bayesianEVT?.gpd_parameters?.xi?.ci95 || null,
          sigma_ci95: bayesianEVT?.gpd_parameters?.sigma?.ci95 || null,
          sample_size: monteCarloResults?.n || 0,
        },
        threshold_compliance: {
          score: Math.round(thresholdScore * 100) / 100,
          ttc_threshold: 2.0,
          min_ttc: monteCarloResults?.collapsedResults?.ttc?.min || null,
          pct_below_threshold: this._computePctBelowThreshold(
            monteCarloResults?.collapsedResults?.ttc,
            2.0
          ),
        },
      },
      scenario_id: 'RE-CA-001',
      conflict_type: 'rear-end',
      timestamp: new Date().toISOString(),
    };
  }

  _computeCollisionScore(collisionRate, ttcStats) {
    // Collision rate component: 0-100 based on observed rate
    // Scale: 0% → 0, 5% → 50, 10%+ → 100 (logarithmic)
    let rateScore = 0;
    if (collisionRate > 0) {
      rateScore = Math.min(100, Math.log10(collisionRate * 100 + 1) * 50);
    }

    // TTC component: lower TTC = higher score
    let ttcScore = 0;
    const minTtc = ttcStats?.min;
    if (minTtc != null && minTtc !== Infinity) {
      // Inverse relationship: TTC < 1s → 100, TTC > 10s → 0
      if (minTtc < 1.0) {
        ttcScore = 100;
      } else if (minTtc > 10.0) {
        ttcScore = 0;
      } else {
        ttcScore = 100 * (1 - (minTtc - 1.0) / 9.0);
      }
    }

    return rateScore * 0.5 + ttcScore * 0.5;
  }

  _computeSeverityScore(severityStats, bayesSeverity, deltaV) {
    // Severity component: 0-100 based on ΔV and severity probabilities
    let dvScore = 0;
    if (deltaV > 0) {
      // Scale: ΔV = 0 → 0, ΔV = 20 m/s → 100
      dvScore = Math.min(100, (deltaV / 20.0) * 100);
    }

    let bayesScore = 0;
    if (bayesSeverity) {
      // Combine fatal + MAIS3+ probability
      bayesScore = Math.min(100, (bayesSeverity.fatal_probability + bayesSeverity.mai3_plus_probability) * 500);
    }

    let sevScore = 0;
    if (severityStats?.p95) {
      sevScore = Math.min(100, (severityStats.p95 / 20.0) * 100);
    }

    return dvScore * 0.3 + bayesScore * 0.4 + sevScore * 0.3;
  }

  _computeUncertaintyScore(gpdParams, sampleSize) {
    // Uncertainty component: 0-100 (higher = more uncertain)
    let paramScore = 0;
    if (gpdParams?.xi?.ci95) {
      // Wide CI → high uncertainty
      const xiWidth = Math.abs(gpdParams.xi.ci95[1] - gpdParams.xi.ci95[0]);
      paramScore = Math.min(50, xiWidth * 100);
    }

    let sampleScore = 0;
    if (sampleSize > 0) {
      // Low sample count → high uncertainty
      if (sampleSize < 1000) sampleScore = 50;
      else if (sampleSize < 5000) sampleScore = 30;
      else if (sampleSize < 10000) sampleScore = 15;
      else sampleScore = 5;
    }

    return Math.min(100, paramScore + sampleScore);
  }

  _computeThresholdScore(indicators, ttcStats, scenarioSpec) {
    // Threshold compliance: 0-100 (higher = more compliant = safer)
    // Start at 100 and subtract for violations
    let score = 100;

    // TTC < 2s threshold
    const minTtc = ttcStats?.min;
    if (minTtc != null && minTtc < 2.0) {
      score -= 30;
    }

    // TTC < 1s threshold
    if (minTtc != null && minTtc < 1.0) {
      score -= 30;
    }

    // DRAC threshold
    const drac = indicators?.drac;
    if (drac && drac > 0 && drac < 3.5) {
      score -= 15;
    }

    // Headway threshold (< 1.0s = unsafe)
    const headway = scenarioSpec?.headway;
    if (headway !== undefined && headway < 14.0) { // 1.0s at 14m/s
      score -= 20;
    }

    return Math.max(0, score);
  }

  _classifyRisk(score) {
    if (score <= this.params.thresholds.low) return 'LOW';
    if (score <= this.params.thresholds.moderate) return 'MODERATE';
    if (score <= this.params.thresholds.high) return 'HIGH';
    return 'CRITICAL';
  }

  _computePctBelowThreshold(ttcStats, threshold) {
    if (!ttcStats) return 0;
    // Use p5 as conservative estimate
    const p5 = ttcStats.p5 || 0;
    return p5 < threshold ? Math.min(100, (1 - p5 / threshold) * 100) : 0;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { RiskScorer };
}
