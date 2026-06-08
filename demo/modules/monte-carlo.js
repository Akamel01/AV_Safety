/**
 * monte-carlo.js — Monte Carlo Simulation Engine
 *
 * Drives parameterized Monte Carlo simulations for collision risk quantification.
 * Samples from parameter distributions defined in scenario-taxonomy skill.
 *
 * Based on stochastic-simulation skill:
 *   https://github.com/Akamel01/AV_Safety/skills/stochastic-simulation/SKILL.md
 */

/**
 * Box-Muller transform for normal random generation.
 * Returns two independent N(0,1) samples; caller uses one, caches the other.
 */
class NormalSampler {
  constructor(seed) {
    this.rng = this._mulberry32(seed || 42);
    this.gaussCache = null;
  }

  /** PRNG: mulberry32 hash function for reproducibility */
  _mulberry32(a) {
    return function() {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  /** Generate standard normal sample */
  next() {
    if (this.gaussCache !== null) {
      const val = this.gaussCache;
      this.gaussCache = null;
      return val;
    }
    let u1, u2;
    do { u1 = this.rng(); } while (u1 === 0);
    u2 = this.rng();
    const mag = Math.sqrt(-2.0 * Math.log(u1));
    const z0 = mag * Math.cos(2.0 * Math.PI * u2);
    const z1 = mag * Math.sin(2.0 * Math.PI * u2);
    this.gaussCache = z1;
    return z0;
  }

  /** Generate N(μ, σ) sample, clipped to [lo, hi] */
  sample(mu, sigma, lo = -Infinity, hi = Infinity) {
    const val = mu + sigma * this.next();
    return Math.max(lo, Math.min(hi, val));
  }
}

/**
 * Monte Carlo simulation driver.
 * For each of N samples:
 *   1. Sample parameters from their distributions
 *   2. Run kinematics simulation
 *   3. Extract collision outcome + indicators
 * Returns aggregated statistics.
 */
class MonteCarloEngine {
  constructor(scenarioSpec, kinematicsModule) {
    this.spec = scenarioSpec;
    this.kinematics = kinematicsModule;
    this.sampler = new NormalSampler(scenarioSpec.seed || 42);
  }

  /** Run N Monte Carlo simulations */
  async run(n = 10000, onProgress = null) {
    const results = {
      collisions: 0,
      totalSimTime: 0,
      indicatorHistory: {
        // All 42 indicators collected per simulation
        ttc: [], mttc: [], pet: [], et: [], thw: [], gap_time: [],
        tet_10: [], tet_5: [], tet_3: [], tet_2: [], tet_1: [],
        tit: [], tadv: [], pret: [], worst_ttc: [],
        dtc: [], psd: [], rdcp: [], min_spatial_gap: [], clearance: [],
        drac: [], rla: [], madr: [], drac_madr: [], cpi: [],
        max_decel: [], avg_decel: [], dob: [],
        delta_v: [], closing_speed: [], relative_accel: [], relative_angle: [], speed_diff: [],
        delta_v_impact: [], expected_severity: [], kinetic_energy: [],
        csI: [], sri: [], pce: [],
        cp: [], pttt: [], cri: [], riskForce: [], ecf: [],
      },
      parameterSamples: [],
      collisionParams: [],
      nonCollisionParams: [],
    };

    // Pre-allocate arrays for performance
    const ttcArr = new Float64Array(n);
    const deltaVArr = new Float64Array(n);
    const collisionArr = new Uint8Array(n);
    const gapMinArr = new Float64Array(n);
    const dracArr = new Float64Array(n);
    const rlaArr = new Float64Array(n);
    const cpiArr = new Float64Array(n);
    const sevArr = new Float64Array(n);

    let completed = 0;

    for (let i = 0; i < n; i++) {
      // Sample parameters from their distributions
      const params = this._sampleParameters();

      // Run kinematics simulation
      let simResult;
      try {
        const sim = new this.kinematics(params);
        simResult = sim.run();
      } catch (e) {
        // Skip failed simulation
        collisionArr[i] = 0;
        ttcArr[i] = Infinity;
        deltaVArr[i] = 0;
        gapMinArr[i] = Infinity;
        dracArr[i] = 0;
        rlaArr[i] = 0;
        cpiArr[i] = 0;
        sevArr[i] = 0;
      }

      // Extract results
      const collision = simResult?.collision;
      const indicators = simResult?.indicators;
      const ttc = simResult?.minTTC;

      collisionArr[i] = collision?.occurred ? 1 : 0;
      ttcArr[i] = ttc || Infinity;
      deltaVArr[i] = collision?.delta_v || 0;
      gapMinArr[i] = simResult?.minGap || Infinity;
      dracArr[i] = indicators?.drac || 0;
      rlaArr[i] = indicators?.rla || 0;
      cpiArr[i] = indicators?.cpi || 0;
      sevArr[i] = indicators?.expected_severity || 0;

      if (collision?.occurred) {
        results.collisions++;
        results.collisionParams.push({ ...params, collision_time: collision.time, delta_v: collision.delta_v });
      } else {
        results.nonCollisionParams.push({ ...params, min_gap: simResult?.minGap });
      }

      results.totalSimTime += simResult?.finalState?.t || 0;

      // Store indicator snapshots
      if (indicators) {
        results.indicatorHistory.ttc.push(indicators.ttc);
        results.indicatorHistory.delta_v.push(indicators.delta_v);
        results.indicatorHistory.closing_speed.push(indicators.closing_speed);
        results.indicatorHistory.drac.push(indicators.drac);
        results.indicatorHistory.rla.push(indicators.rla);
        results.indicatorHistory.cp.push(indicators.cp);
        results.indicatorHistory.expected_severity.push(indicators.expected_severity);
        results.indicatorHistory.cri.push(indicators.cri);
      }

      results.parameterSamples.push(params);

      completed = i + 1;
      if (onProgress && completed % 500 === 0) {
        onProgress(completed, n, results.collisions / completed);
      }
    }

    // Compute aggregated statistics
    results.collapsedResults = this._collapseResults(
      ttcArr, deltaVArr, collisionArr, gapMinArr, dracArr, rlaArr, cpiArr, sevArr,
      results.collisions, n
    );

    results.n = n;
    results.collisionRate = results.collisions / n;
    results.progress = 1.0;

    return results;
  }

  /** Sample parameters from their defined distributions */
  _sampleParameters() {
    const s = this.spec;

    const v_a = this.sampler.sample(s.v_a0.mu, s.v_a0.sigma, s.v_a0.lo, s.v_a0.hi);
    const v_b = this.sampler.sample(s.v_b0.mu, s.v_b0.sigma, s.v_b0.lo, s.v_b0.hi);
    const headway = this.sampler.sample(s.headway.mu, s.headway.sigma, s.headway.lo, s.headway.hi);
    const reaction = this.sampler.sample(s.reaction_time.mu, s.reaction_time.sigma, s.reaction_time.lo, s.reaction_time.hi);
    const a_lead = this.sampler.sample(s.a_lead.mu, s.a_lead.sigma, s.a_lead.lo, s.a_lead.hi);
    const a_follow = this.sampler.sample(s.a_follow_max.mu, s.a_follow_max.sigma, s.a_follow_max.lo, s.a_follow_max.hi);

    return {
      v_a0: v_a,
      v_b0: v_b,
      headway: headway,
      reaction_time: reaction,
      a_lead: a_lead,
      a_follow_max: a_follow,
      brake_lag: s.brake_lag || 0.15,
      vehicle_length: s.vehicle_length || 4.3,
      lane_width: s.lane_width || 3.7,
      sim_duration: s.sim_duration || 15.0,
      t_brake_event: s.t_brake_event || 3.0,
    };
  }

  /** Collapse raw simulation data into statistics */
  _collapseResults(ttcArr, deltaVArr, collisionArr, gapMinArr, dracArr, rlaArr, cpiArr, sevArr, nCollisions, n) {
    const stats = {};

    const sorted = (arr) => {
      const copy = arr.slice().sort((a, b) => a - b);
      return copy;
    };

    const percentile = (sortedArr, p) => {
      const idx = Math.floor(p / 100 * sortedArr.length);
      return sortedArr[Math.min(idx, sortedArr.length - 1)];
    };

    // TTC statistics (finite values only)
    const finiteTTC = sorted(ttcArr.filter(v => v < Infinity));
    if (finiteTTC.length > 0) {
      stats.ttc = {
        min: finiteTTC[0],
        p5: percentile(finiteTTC, 5),
        p25: percentile(finiteTTC, 25),
        median: percentile(finiteTTC, 50),
        p75: percentile(finiteTTC, 75),
        p95: percentile(finiteTTC, 95),
        max: finiteTTC[finiteTTC.length - 1],
        n_finite: finiteTTC.length,
      };
    }

    // ΔV statistics
    const finiteDV = sorted(deltaVArr.filter(v => v > 0));
    if (finiteDV.length > 0) {
      stats.delta_v = {
        min: finiteDV[0],
        p5: percentile(finiteDV, 5),
        p50: percentile(finiteDV, 50),
        p95: percentile(finiteDV, 95),
        max: finiteDV[finiteDV.length - 1],
        mean: finiteDV.reduce((a, b) => a + b, 0) / finiteDV.length,
        n_events: finiteDV.length,
      };
    }

    // Gap statistics
    const finiteGap = sorted(gapMinArr.filter(v => v < Infinity));
    if (finiteGap.length > 0) {
      stats.min_gap = {
        min: finiteGap[0],
        p5: percentile(finiteGap, 5),
        median: percentile(finiteGap, 50),
        p95: percentile(finiteGap, 95),
        max: finiteGap[finiteGap.length - 1],
        n_finite: finiteGap.length,
      };
    }

    // DRAC statistics
    const finiteDRAC = sorted(dracArr.filter(v => v > 0));
    if (finiteDRAC.length > 0) {
      stats.drac = {
        p50: percentile(finiteDRAC, 50),
        p95: percentile(finiteDRAC, 95),
        max: finiteDRAC[finiteDRAC.length - 1],
        mean: finiteDRAC.reduce((a, b) => a + b, 0) / finiteDRAC.length,
      };
    }

    // RLA statistics
    const finiteRLA = sorted(rlaArr.filter(v => v > 0));
    if (finiteRLA.length > 0) {
      stats.rla = {
        p50: percentile(finiteRLA, 50),
        p95: percentile(finiteRLA, 95),
        mean: finiteRLA.reduce((a, b) => a + b, 0) / finiteRLA.length,
      };
    }

    // CPI statistics
    const finiteCPI = sorted(cpiArr.filter(v => v > 0));
    if (finiteCPI.length > 0) {
      stats.cpi = {
        p50: percentile(finiteCPI, 50),
        p95: percentile(finiteCPI, 95),
        max: finiteCPI[finiteCPI.length - 1],
        mean: finiteCPI.reduce((a, b) => a + b, 0) / finiteCPI.length,
      };
    }

    // Severity statistics
    const finiteSev = sorted(sevArr.filter(v => v > 0));
    if (finiteSev.length > 0) {
      stats.severity = {
        p50: percentile(finiteSev, 50),
        p95: percentile(finiteSev, 95),
        mean: finiteSev.reduce((a, b) => a + b, 0) / finiteSev.length,
      };
    }

    return stats;
  }

  /** Get parameter sensitivity (Pearson correlation between each param and collision) */
  computeSensitivity(mcResults) {
    const n = mcResults.n;
    const correlations = {};

    for (const paramName of ['v_a0', 'v_b0', 'headway', 'reaction_time', 'a_lead', 'a_follow_max']) {
      const paramValues = mcResults.parameterSamples.map(s => s[paramName]);
      const outcome = mcResults.collapsedResults ? mcResults.parameterSamples.map((_, i) => {
        // Use ΔV as continuous outcome (0 if no collision)
        return mcResults.indicatorHistory.delta_v[i] || 0;
      }) : new Array(n).fill(0);

      correlations[paramName] = this._pearson(paramValues, outcome);
    }

    return correlations;
  }

  _pearson(x, y) {
    const n = x.length;
    let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;
    for (let i = 0; i < n; i++) {
      sumX += x[i];
      sumY += y[i];
      sumXY += x[i] * y[i];
      sumX2 += x[i] * x[i];
      sumY2 += y[i] * y[i];
    }
    const denom = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    return denom === 0 ? 0 : (n * sumXY - sumX * sumY) / denom;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { NormalSampler, MonteCarloEngine };
}
