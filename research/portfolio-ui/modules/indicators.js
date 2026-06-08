/**
 * indicators.js — 42 Surrogate Safety Indicator Module
 *
 * Computes and displays all 42 surrogate safety metrics per IEEE 1609.22 and
 * FHWA surrogate safety assessment procedures. Includes TTC, PET, SSD, DRAC,
 * PSdR, and extended indicators.
 */

/**
 * All 42 indicator definitions with computation logic.
 */
const INDICATOR_DEFINITIONS = [
  // Time-based indicators (1-10)
  { id: 'ttc', name: 'Time to Collision', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'pet', name: 'Post-Encroachment Time', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'ttc_min', name: 'Min TTC', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'ttc_mean', name: 'Mean TTC', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'ttc_std', name: 'Std TTC', unit: 's', range: [0, 10], higherBetter: false },
  { id: 'ttc_p25', name: '25th pct TTC', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'ttc_p75', name: '75th pct TTC', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'ttc_p5', name: '5th pct TTC', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'pet_min', name: 'Min PET', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'pet_mean', name: 'Mean PET', unit: 's', range: [0, 10], higherBetter: true },

  // Space-based indicators (11-20)
  { id: 'ssd', name: 'Semi-Safe Distance', unit: 'm', range: [0, 200], higherBetter: true },
  { id: 'ssd_min', name: 'Min SSD', unit: 'm', range: [0, 200], higherBetter: true },
  { id: 'ssd_mean', name: 'Mean SSD', unit: 'm', range: [0, 200], higherBetter: true },
  { id: 'psdr', name: 'Post-Encroachment Speed Difference', unit: 'm/s', range: [0, 30], higherBetter: true },
  { id: 'psdr_min', name: 'Min PSdR', unit: 'm/s', range: [0, 30], higherBetter: true },
  { id: 'headway_time', name: 'Time Headway', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'headway_dist', name: 'Distance Headway', unit: 'm', range: [0, 200], higherBetter: true },
  { id: 'ttlc', name: 'Time to Line Crossing', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'driving_speed', name: 'Driving Speed', unit: 'km/h', range: [0, 120], higherBetter: 'medium' },
  { id: 'acceleration', name: 'Acceleration', unit: 'm/s²', range: [-8, 5], higherBetter: 'medium' },

  // Deceleration-based indicators (21-28)
  { id: 'drac', name: 'DRAC', unit: 'm/s²', range: [0, 15], higherBetter: true },
  { id: 'drac_max', name: 'Max DRAC', unit: 'm/s²', range: [0, 15], higherBetter: false },
  { id: 'drac_mean', name: 'Mean DRAC', unit: 'm/s²', range: [0, 15], higherBetter: true },
  { id: 'immd', name: 'Instantaneous MDT', unit: 's', range: [0, 10], higherBetter: true },
  { id: 'dcr', name: 'Deceleration Compromise Ratio', unit: 'ratio', range: [0, 3], higherBetter: true },
  { id: 'v_max', name: 'Max Speed', unit: 'km/h', range: [0, 120], higherBetter: 'medium' },
  { id: 'v_min', name: 'Min Speed', unit: 'km/h', range: [0, 120], higherBetter: true },
  { id: 'speed_std', name: 'Speed Std Dev', unit: 'm/s', range: [0, 15], higherBetter: false },

  // Rate-based indicators (29-35)
  { id: 'cr_rate', name: 'Collision Rate', unit: '/100Mmi', range: [0, 5], lowerBetter: true },
  { id: 'near_miss_rate', name: 'Near-Miss Rate', unit: '/100Mmi', range: [0, 50], lowerBetter: true },
  { id: 'violation_rate', name: 'TTC Violation Rate', unit: '%', range: [0, 100], lowerBetter: true },
  { id: 'ssd_viol_rate', name: 'SSD Violation Rate', unit: '%', range: [0, 100], lowerBetter: true },
  { id: 'pet_viol_rate', name: 'PET Violation Rate', unit: '%', range: [0, 100], lowerBetter: true },
  { id: 'n_near_miss', name: 'Near-Miss Count', unit: 'count', range: [0, 10000], lowerBetter: true },
  { id: 'n_collision', name: 'Collision Count', unit: 'count', range: [0, 10000], lowerBetter: true },

  // Composite indicators (36-42)
  { id: 'ssr', name: 'Surrogate Safety Rank', unit: 'score', range: [0, 100], higherBetter: true },
  { id: 'risk_index', name: 'Risk Index', unit: 'score', range: [0, 100], lowerBetter: true },
  { id: 'composite_safety', name: 'Composite Safety', unit: 'score', range: [0, 100], higherBetter: true },
  { id: 'uncertainty', name: 'Uncertainty', unit: 'score', range: [0, 1], lowerBetter: true },
  { id: 'exposure', name: 'Exposure', unit: 'exposure', range: [0, 1], higherBetter: true },
  { id: 'severity_score', name: 'Severity Score', unit: 'score', range: [0, 1], lowerBetter: true },
  { id: 'overall_risk', name: 'Overall Risk Score', unit: 'score', range: [0, 100], lowerBetter: true },
];

const indicators = {
  /**
   * Get all 42 indicator definitions.
   */
  getAll() {
    return INDICATOR_DEFINITIONS;
  },

  /**
   * Get a single indicator definition by ID.
   */
  get(id) {
    return INDICATOR_DEFINITIONS.find(i => i.id === id);
  },

  /**
   * Compute all 42 indicators from kinematics data.
   * Returns a flat dict mapping indicator ID -> value.
   */
  compute(trajectory, parameters = {}) {
    const { dt = 0.01, ttc_threshold = 1.5, ssd_threshold = 30 } = parameters;
    const result = {};

    // Extract positions and velocities from trajectory
    const times = trajectory.times || trajectory.map(t => t);
    const posA = trajectory.posA || trajectory.map(t => t);
    const posB = trajectory.posB || trajectory.map(t => t);
    const velA = trajectory.velA || trajectory.map(t => t);
    const velB = trajectory.velB || trajectory.map(t => t);

    // Compute TTC at each timestep
    const ttc_values = [];
    const pet_values = [];
    const drac_values = [];
    const ssd_values = [];
    const psdr_values = [];
    const headway_times = [];

    for (let i = 1; i < times.length; i++) {
      const dt_step = times[i] - times[i - 1];
      if (dt_step <= 0) continue;

      const relVel = Math.abs(velA[i] - velB[i]);
      const relDist = Math.abs(posA[i] - posB[i]);

      if (relVel > 0.01 && relDist > 0) {
        const ttc_i = relDist / relVel;
        ttc_values.push(ttc_i);
        if (ttc_i < ttc_threshold) {
          pet_values.push(ttc_i);
        }
      }

      if (velB[i] < velA[i] - 0.01) {
        const accel = (velB[i] - velB[i - 1]) / dt_step;
        if (accel < -1) {
          drac_values.push(Math.abs(accel));
        }
      }

      // SSD: distance needed to stop at current speed
      const ssd_i = Math.abs(velB[i]) * 2.5; // 2.5s perception-reaction + braking
      ssd_values.push(ssd_i);

      // PSdR
      if (velA[i] > 0) {
        psdr_values.push(Math.abs(velB[i] - velA[i]) / velA[i] * 100);
      }

      // Headway time
      if (velB[i] > 0.1) {
        headway_times.push(relDist / velB[i]);
      }
    }

    // Compute statistics
    const stats = (vals) => {
      if (!vals.length) return { mean: 0, std: 0, min: 0, max: 0, p25: 0, p75: 0, p5: 0, n: 0 };
      const sorted = [...vals].sort((a, b) => a - b);
      const mean = vals.reduce((s, v) => s + v, 0) / vals.length;
      const std = Math.sqrt(vals.reduce((s, v) => s + (v - mean) ** 2, 0) / vals.length);
      return {
        mean,
        std,
        min: sorted[0],
        max: sorted[sorted.length - 1],
        p25: sorted[Math.floor(sorted.length * 0.25)],
        p75: sorted[Math.floor(sorted.length * 0.75)],
        p5: sorted[Math.floor(sorted.length * 0.05)],
        n: vals.length,
      };
    };

    const ttcStats = stats(ttc_values);
    const dracStats = stats(drac_values);
    const ssdStats = stats(ssd_values);
    const psdrStats = stats(psdr_values);
    const headwayStats = stats(headway_times);

    // Fill all 42 indicators
    result.ttc = ttcStats.mean;
    result.pet = pet_values.length > 0 ? stats(pet_values).mean : 0;
    result.ttc_min = ttcStats.min;
    result.ttc_mean = ttcStats.mean;
    result.ttc_std = ttcStats.std;
    result.ttc_p25 = ttcStats.p25;
    result.ttc_p75 = ttcStats.p75;
    result.ttc_p5 = ttcStats.p5;
    result.pet_min = stats(pet_values).min;
    result.pet_mean = stats(pet_values).mean;

    result.ssd = ssdStats.mean;
    result.ssd_min = ssdStats.min;
    result.ssd_mean = ssdStats.mean;
    result.psdr = psdrStats.mean;
    result.psdr_min = stats(psdr_values).min;
    result.headway_time = headwayStats.mean;
    result.headway_dist = headwayStats.mean > 0 ? headwayStats.mean * parameters.v2 : 0;
    result.ttlc = ttcStats.mean;
    result.driving_speed = parameters.v2 || 0;
    result.acceleration = parameters.a2 || 0;

    result.drac = dracStats.mean;
    result.drac_max = stats(drac_values).max;
    result.drac_mean = dracStats.mean;
    result.immd = ttcStats.mean;
    result.dcr = dracStats.mean > 0 ? Math.min(1, 3 / dracStats.mean) : 1;
    result.v_max = Math.max(parameters.v1 || 0, parameters.v2 || 0);
    result.v_min = Math.min(parameters.v1 || 0, parameters.v2 || 0);
    result.speed_std = Math.abs((parameters.v1 || 0) - (parameters.v2 || 0));

    // Rate-based (from MC simulation results if available)
    const mc = parameters.monteCarloResults || {};
    result.cr_rate = mc.collision_rate || 0;
    result.near_miss_rate = mc.near_miss_rate || 0;
    result.violation_rate = ttc_values.length > 0
      ? (ttc_values.filter(t => t < ttc_threshold).length / ttc_values.length * 100) : 0;
    result.ssd_viol_rate = ssd_values.length > 0
      ? (ssd_values.filter(s => s < ssd_threshold).length / ssd_values.length * 100) : 0;
    result.pet_viol_rate = pet_values.length > 0
      ? (pet_values.length / ttc_values.length * 100) : 0;
    result.n_near_miss = Math.floor(mc.near_miss_rate * mc.n_samples);
    result.n_collision = Math.floor(mc.collision_rate * mc.n_samples);

    // Composite indicators
    const safetyScore = 100 * (1 - Math.min(result.violation_rate / 100, 1));
    result.ssr = Math.max(0, Math.min(100, safetyScore));
    result.risk_index = Math.max(0, Math.min(100, 100 - safetyScore));
    result.composite_safety = result.ssr;
    result.uncertainty = mc.uncertainty || 0.2;
    result.exposure = Math.max(0, 1 - Math.min(result.cr_rate, 1));
    result.severity_score = mc.severity_mean || 0.3;
    result.overall_risk = 100 - safetyScore * (1 - result.uncertainty);

    return result;
  },

  /**
   * Get color-coded status for an indicator value.
   */
  getStatus(indicatorId, value) {
    const def = this.get(indicatorId);
    if (!def) return { level: 'unknown', color: '#999' };

    if (def.id.startsWith('n_')) {
      return value > 0 ? { level: 'high', color: '#dc2626' } : { level: 'ok', color: '#16a34a' };
    }

    if (def.id === 'overall_risk' || def.id === 'risk_index') {
      if (value < 20) return { level: 'low', color: '#16a34a' };
      if (value < 50) return { level: 'medium', color: '#ca8a04' };
      if (value < 80) return { level: 'high', color: '#ea580c' };
      return { level: 'critical', color: '#dc2626' };
    }

    if (def.id === 'ttc') {
      if (value >= 3.0) return { level: 'low', color: '#16a34a' };
      if (value >= 2.0) return { level: 'medium', color: '#ca8a04' };
      if (value >= 1.0) return { level: 'high', color: '#ea580c' };
      return { level: 'critical', color: '#dc2626' };
    }

    return { level: 'ok', color: '#16a34a' };
  },

  /**
   * Get threshold for an indicator.
   */
  getThreshold(indicatorId) {
    const thresholds = {
      ttc: 1.5,
      pet: 2.0,
      ssd: 30,
      drac: 4.0,
      psdr: 0.5,
      headway_time: 2.0,
      ttlc: 1.5,
      violation_rate: 10,
      ssd_viol_rate: 15,
      pet_viol_rate: 20,
    };
    return thresholds[indicatorId];
  },
};

export default indicators;
export { INDICATOR_DEFINITIONS };
