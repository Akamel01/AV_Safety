/**
 * Risk Computation Module
 * Wraps bayesian-evt skill for portfolio UI
 */

import { bayesianEvt } from './bayesian-evt';

export const riskComputation = {
  /**
   * Compute risk for a scenario using Bayesian EVT
   * @param {Object} params - Scenario parameters
   * @param {string} params.conflictType - Conflict type (e.g., 'crossing')
   * @param {string} params.scenarioId - Scenario identifier
   * @param {Object} params.parameters - Kinematic parameters
   * @param {number} params.parameters.v1 - Approach speed 1 (km/h)
   * @param {number} params.parameters.v2 - Approach speed 2 (km/h)
   * @param {number} params.parameters.ttc - Time-to-collision (s)
   * @param {number} params.parameters.headway - Headway distance (m)
   * @param {number} params.parameters.visibility - Visibility distance (m)
   * @param {number} params.sampleSize - Monte Carlo sample size (default: 10000)
   * @returns {Promise<Object>} Risk computation result
   */
  async compute(params) {
    try {
      // Validate inputs
      if (!params.conflictType || !params.scenarioId || !params.parameters) {
        throw new Error('Missing required parameters: conflictType, scenarioId, parameters');
      }

      // Delegate to bayesian-evt skill
      const result = await bayesianEvt.compute({
        conflictType: params.conflictType,
        scenarioId: params.scenarioId,
        parameters: params.parameters,
        sampleSize: params.sampleSize || 10000
      });

      // Add metadata
      result.metadata = {
        conflictType: params.conflictType,
        scenarioId: params.scenarioId,
        parameters: params.parameters,
        sampleSize: params.sampleSize || 10000,
        computedAt: new Date().toISOString()
      };

      return result;
    } catch (error) {
      console.error('Risk computation failed:', error);
      throw new Error(`Risk computation failed: ${error.message}`);
    }
  },

  /**
   * Batch compute risks for multiple scenarios
   * @param {Array} scenarios - Array of scenario objects
   * @param {number} sampleSize - Monte Carlo sample size
   * @returns {Promise<Object>} Batch computation results
   */
  async batchCompute(scenarios, sampleSize = 10000) {
    const results = {};

    for (const scenario of scenarios) {
      try {
        results[scenario.id] = await this.compute({
          conflictType: scenario.conflictType,
          scenarioId: scenario.id,
          parameters: scenario.parameters,
          sampleSize
        });
      } catch (error) {
        console.error(`Failed to compute risk for scenario ${scenario.id}:`, error);
        results[scenario.id] = {
          error: error.message,
          conflictType: scenario.conflictType,
          scenarioId: scenario.id,
          computedAt: new Date().toISOString()
        };
      }
    }

    return results;
  },

  /**
   * Get risk thresholds for jurisdiction
   * @param {string} jurisdiction - Jurisdiction (usa, canada, england)
   * @returns {Object} Risk thresholds
   */
  getThresholds(jurisdiction = 'usa') {
    const thresholds = {
      usa: {
        ttc: 1.5,
        ssd: 2.0,
        drac: 2.0,
        pet: 1.0,
        psdr: 0.8
      },
      canada: {
        ttc: 1.5,
        ssd: 2.0,
        drac: 2.0,
        pet: 1.0,
        psdr: 0.8
      },
      england: {
        ttc: 1.5,
        ssd: 2.0,
        drac: 2.0,
        pet: 1.0,
        psdr: 0.8
      }
    };

    return thresholds[jurisdiction] || thresholds.usa;
  },

  /**
   * Classify risk level (low, moderate, high, critical)
   * @param {number} occurrenceLikelihood - Occurrence likelihood (0-100)
   * @returns {string} Risk level
   */
  classifyRisk(occurrenceLikelihood) {
    if (occurrenceLikelihood >= 70) return 'critical';
    if (occurrenceLikelihood >= 50) return 'high';
    if (occurrenceLikelihood >= 30) return 'moderate';
    return 'low';
  }
};

export default riskComputation;