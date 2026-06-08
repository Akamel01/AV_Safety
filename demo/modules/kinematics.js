/**
 * kinematics.js — Rear-End Trajectory Engine
 *
 * Computes exact trajectories for two vehicles in a rear-end scenario:
 *   Vehicle A (lead): cruising, then sudden hard braking
 *   Vehicle B (follow): constant gap until perception-reaction, then braking
 *
 * Physics models:
 *   - Constant acceleration (kinematic equations)
 *   - AABB collision detection per timestep
 *   - dt = 10ms, sub-stepping 4× for collision accuracy
 *
 * Based on kinematics-engine skill:
 *   https://github.com/Akamel01/AV_Safety/skills/kinematics-engine/SKILL.md
 */

class RearEndKinematics {
  constructor(params) {
    // Validate and normalize inputs
    this.params = this.validateParams(params);
    this.dt = 0.0025; // 2.5ms sub-step for accuracy
    this.nSteps = Math.ceil(this.params.simDuration / this.dt);
    this.tBrake = this.params.t_brake_event || 3.0; // When lead vehicle brakes
    this.tReaction = this.params.t_reaction || 1.5; // Perception-reaction time
  }

  validateParams(p) {
    const params = {
      v_a0: parseFloat(p.v_a0) || 27.8,
      v_b0: parseFloat(p.v_b0) || 27.8,
      headway: parseFloat(p.headway) || 30.0,
      reaction_time: parseFloat(p.reaction_time) || 1.5,
      a_lead: parseFloat(p.a_lead) || -5.0,
      a_follow_max: parseFloat(p.a_follow_max) || -8.0,
      brake_lag: parseFloat(p.brake_lag) || 0.15,
      vehicle_length: parseFloat(p.vehicle_length) || 4.3,
      lane_width: parseFloat(p.lane_width) || 3.7,
      sim_duration: parseFloat(p.sim_duration) || 15.0,
      t_brake_event: parseFloat(p.t_brake_event) || 3.0,
      v_a_max: 35.0,
      v_b_max: 35.0,
      v_a_min: 0.0,
      v_b_min: 0.0,
    };
    return params;
  }

  /**
   * Run the simulation and return full trajectory history.
   * Returns: { trajectory, collision, ttc_history, indicators_snapshot }
   */
  run() {
    const {
      v_a0, v_b0, headway, reaction_time,
      a_lead, a_follow_max, brake_lag, vehicle_length,
      sim_duration, t_brake_event, v_a_min, v_b_min,
    } = this.params;

    // Initialize states
    let x_a = 0.0;
    let x_b = -headway; // B starts behind A by headway
    let v_a = v_a0;
    let v_b = v_b0;
    let a_a = 0.0;
    let a_b = 0.0;

    // Event triggers
    let brakeTriggered = false;
    let brakeLagTimer = 0;
    let bReactionTriggered = false;
    let bLagTimer = 0;

    // Storage
    const trajectory = {
      t: [], x_a: [], x_b: [], v_a: [], v_b: [], a_a: [], a_b: [],
      gap: [], v_rel: [], ttc: [], collision: [],
    };

    let collisionTime = null;
    let collisionGap = null;
    let deltaV = 0.0;
    let minTTC = Infinity;
    let minGap = Infinity;

    for (let i = 0; i < this.nSteps; i++) {
      const t = i * this.dt;

      // === Update vehicle A (lead) ===
      if (t >= t_brake_event && !brakeTriggered) {
        brakeTriggered = true;
        brakeLagTimer = t + brake_lag;
      }
      if (t >= brakeLagTimer) {
        a_a = Math.min(a_lead, 0); // Negative (braking)
        v_a += a_a * this.dt;
        v_a = Math.max(v_a, v_a_min); // Don't go backward
      }

      x_a += v_a * this.dt;

      // === Update vehicle B (follow) ===
      if (!bReactionTriggered && t >= t_brake_event + reaction_time) {
        bReactionTriggered = true;
        bLagTimer = t + brake_lag;
      }
      if (bReactionTriggered && t >= bLagTimer) {
        // Compute required deceleration to avoid collision
        const gap = x_a - x_b;
        const v_rel = v_b - v_a; // positive = closing

        if (v_rel > 0) {
          // How much decel needed to maintain gap?
          const required_a = -(v_rel * v_rel) / (2 * Math.max(gap - vehicle_length, 0.1));
          a_b = Math.max(a_follow_max, Math.min(required_a, 0));
        } else {
          a_b = a_follow_max;
        }

        // Clamp to max capability
        a_b = Math.max(a_b, a_follow_max);

        v_b += a_b * this.dt;
        v_b = Math.max(v_b, v_b_min);
      }

      x_b += v_b * this.dt;

      // === Compute metrics ===
      const gap = x_a - x_b - vehicle_length; // gap = A_front - B_rear
      const v_rel = v_b - v_a; // positive = B faster = closing

      // TTC
      let ttc = Infinity;
      if (v_rel > 0.001 && gap > 0) {
        ttc = gap / v_rel;
      } else if (v_rel > 0.001 && gap <= 0) {
        // Collision! gap ≤ 0 means bodies overlap
        ttc = 0;
      }

      const isCollision = gap <= -0.01; // -1cm tolerance

      // Store trajectory
      trajectory.t.push(t);
      trajectory.x_a.push(x_a);
      trajectory.x_b.push(x_b);
      trajectory.v_a.push(v_a);
      trajectory.v_b.push(v_b);
      trajectory.a_a.push(a_a);
      trajectory.a_b.push(a_b);
      trajectory.gap.push(gap);
      trajectory.v_rel.push(v_rel);
      trajectory.ttc.push(ttc);
      trajectory.collision.push(isCollision);

      // Track extremes
      if (!isCollision && ttc > 0 && ttc < minTTC) {
        minTTC = ttc;
      }
      if (!isCollision && gap < minGap) {
        minGap = gap;
      }

      // Detect collision (first crossing)
      if (!isCollision && t > 0) {
        const prevGap = trajectory.gap[i - 1];
        if (prevGap > -0.01 && gap <= -0.01) {
          // Linear interpolation for exact collision time
          collisionTime = t - this.dt * (prevGap / (prevGap - gap));
          collisionGap = 0;
          deltaV = Math.abs(v_b - v_a);
          break;
        }
      }

      if (t >= sim_duration) break;
    }

    if (!collisionTime) {
      collisionTime = null;
      collisionGap = minGap;
      // Final ΔV
      deltaV = Math.abs(v_b - v_a);
    }

    // Compute full indicator suite
    const indicators = this.computeIndicators(trajectory, collisionTime, deltaV);

    return {
      collision: {
        occurred: !!collisionTime,
        time: collisionTime,
        gap: collisionGap,
        delta_v: deltaV,
      },
      minTTC: minTTC === Infinity ? null : minTTC,
      minGap: minGap === Infinity ? null : minGap,
      trajectory,
      indicators,
      finalState: {
        t: trajectory.t[trajectory.t.length - 1],
        x_a: x_a,
        x_b: x_b,
        v_a: v_a,
        v_b: v_b,
        gap: x_a - x_b - vehicle_length,
      },
    };
  }

  /**
   * Compute all 42 indicators from trajectory history.
   * Based on indicator-computation skill:
   *   https://github.com/Akamel01/AV_Safety/skills/indicator-computation/SKILL.md
   */
  computeIndicators(traj, collisionTime, deltaV) {
    const n = traj.t.length;
    const indicators = {};

    // ===== TIME-BASED (11) =====

    // 1. TTC: Time to collision
    let ttcMin = Infinity;
    for (let i = 1; i < n; i++) {
      if (traj.v_rel[i] > 0.001 && traj.gap[i] > 0) {
        const ttc = traj.gap[i] / traj.v_rel[i];
        if (ttc < ttcMin) ttcMin = ttc;
      }
    }
    indicators.ttc = ttcMin === Infinity ? null : ttcMin;

    // 2. MTTC: Modified TTC (handles zero closing speed)
    let mttc = Infinity;
    for (let i = 1; i < n; i++) {
      if (traj.v_rel[i] > 0.001) {
        const ttc = traj.gap[i] / traj.v_rel[i];
        if (ttc < mttc) mttc = ttc;
      } else if (traj.gap[i] > 0) {
        // Zero closing speed but gap exists → MTTC = large value
        mttc = Math.min(mttc, traj.gap[i] / 0.001);
      }
    }
    indicators.mttc = mttc === Infinity ? null : mttc;

    // 3. PET: Postencounter time (time after gap stops decreasing)
    let petMin = Infinity;
    let gapStartDecreasing = false;
    let gapLastDecrease = 0;
    for (let i = 1; i < n; i++) {
      if (traj.gap[i] < traj.gap[i - 1] && !gapStartDecreasing) {
        gapStartDecreasing = true;
      }
      if (gapStartDecreasing && traj.gap[i] >= traj.gap[i - 1]) {
        gapLastDecrease = i;
        break;
      }
    }
    if (gapLastDecrease > 0) {
      petMin = traj.t[n - 1] - traj.t[gapLastDecrease];
    }
    indicators.pet = petMin === Infinity ? null : petMin;

    // 4. ET: Encounter time (time during which gap is decreasing)
    let et = 0;
    for (let i = 1; i < n; i++) {
      if (traj.gap[i] < traj.gap[i - 1]) et += this.dt;
    }
    indicators.et = et;

    // 5. THW: Time headway (gap / v_b when v_b > 0)
    let thw = [];
    for (let i = 0; i < n; i++) {
      if (traj.v_b[i] > 0.1) {
        thw.push(traj.gap[i] / traj.v_b[i]);
      }
    }
    indicators.thw = thw.length > 0 ? { min: Math.min(...thw), max: Math.max(...thw), mean: thw.reduce((a, b) => a + b, 0) / thw.length } : null;

    // 6. gap_time: Time gap (THW at constant speed)
    indicators.gap_time = indicators.thw;

    // 7. TET: Time exposed to risk (time with TTC < threshold)
    const riskThresholds = [10, 5, 3, 2, 1];
    indicators.tet = {};
    for (const thresh of riskThresholds) {
      let count = 0;
      for (let i = 0; i < n; i++) {
        if (traj.ttc[i] !== null && traj.ttc[i] < thresh) count++;
      }
      indicators.tet[thresh] = count * this.dt;
    }

    // 8. TIT: Time in danger zone (TTC < 2s)
    let tit = 0;
    for (let i = 0; i < n; i++) {
      if (traj.ttc[i] !== null && traj.ttc[i] < 2.0) tit += this.dt;
    }
    indicators.tit = tit;

    // 9. TAdv: Advanced warning time (first time TTC < 10s)
    let tadv = null;
    for (let i = 0; i < n; i++) {
      if (traj.ttc[i] !== null && traj.ttc[i] < 10.0) {
        tadv = traj.t[i];
        break;
      }
    }
    indicators.tadv = tadv;

    // 10. PrET: Predicted encounter time (gap / v_rel extrapolated)
    let pret = null;
    for (let i = n - 1; i >= 0; i--) {
      if (traj.v_rel[i] > 0.01 && traj.gap[i] > 0) {
        pret = traj.t[i] + traj.gap[i] / traj.v_rel[i];
        break;
      }
    }
    indicators.pret = pret;

    // 11. worst_TTC: Minimum TTC over simulation
    indicators.worst_ttc = indicators.ttc;

    // ===== DISTANCE-BASED (5) =====

    // 12. DTC: Distance to collision
    let dtc = Infinity;
    for (let i = 0; i < n; i++) {
      if (traj.ttc[i] !== null && traj.ttc[i] < Infinity) {
        dtc = Math.min(dtc, traj.v_b[i] * traj.ttc[i]);
      }
    }
    indicators.dtc = dtc === Infinity ? null : dtc;

    // 13. PSD: Postencounter space distance (distance after gap stabilizes)
    let psd = null;
    if (gapLastDecrease > 0 && gapLastDecrease < n - 1) {
      psd = traj.gap[n - 1];
    }
    indicators.psd = psd;

    // 14. RDCP: Relative distance at point of conflict
    let rdcp = null;
    for (let i = 0; i < n; i++) {
      if (traj.collision[i]) {
        rdcp = traj.gap[i];
        break;
      }
    }
    // Fallback: minimum gap when no collision occurred
    if (rdcp === null) {
      let fallbackGap = Infinity;
      for (let i = 0; i < n; i++) {
        if (traj.gap[i] < fallbackGap) fallbackGap = traj.gap[i];
      }
      rdcp = fallbackGap === Infinity ? null : fallbackGap;
    }
    indicators.rdcp = rdcp;

    // 15. min_spatial_gap: Minimum longitudinal gap
    let minSpatialGap = Infinity;
    for (let i = 0; i < n; i++) {
      if (traj.gap[i] < minSpatialGap) minSpatialGap = traj.gap[i];
    }
    indicators.min_spatial_gap = minSpatialGap === Infinity ? null : minSpatialGap;

    // 16. clearance: Safety margin at closest approach
    indicators.clearance = indicators.min_spatial_gap;

    // ===== DECELERATION-BASED (8) =====

    // 17. DRAC: Deceleration rate at collision
    let drac = null;
    if (collisionTime !== null) {
      drac = Math.abs(a_follow_max);
    }
    indicators.drac = drac;

    // 18. RLA: Required deceleration to avoid collision
    let rla = null;
    for (let i = 0; i < n; i++) {
      if (traj.gap[i] > 0 && traj.v_rel[i] > 0) {
        const d = traj.gap[i] - 4.3; // subtract vehicle length
        const v = traj.v_rel[i];
        if (d > 0.1) {
          const required = (v * v) / (2 * d);
          if (rla === null || required < rla) rla = required;
        }
      }
    }
    indicators.rla = rla;

    // 19. MADR: Maximum adequate deceleration
    let madr = null;
    for (let i = 0; i < n; i++) {
      if (traj.v_rel[i] > 0 && traj.gap[i] > 4.3) {
        const d = traj.gap[i] - 4.3;
        const t = traj.gap[i] / traj.v_rel[i];
        if (t > 0) {
          const adequate = (traj.v_b[i] * traj.v_b[i]) / (2 * d);
          if (madr === null || adequate < madr) madr = adequate;
        }
      }
    }
    indicators.madr = madr;

    // 20. DRAC-MADR: Combined deceleration metric
    indicators.drac_madr = (drac !== null && madr !== null) ? drac / Math.abs(madr) : null;

    // 21. CPI: Collision probability index (decel-based)
    let cpi = null;
    if (rla !== null && rla > 0) {
      // Normalize: CPI = rla / a_max_vehicle ≈ 0-1
      const a_max_vehicle = 8.0; // m/s², ABS limit
      cpi = Math.min(rla / a_max_vehicle, 1.0);
    }
    indicators.cpi = cpi;

    // 22. max_decel: Maximum deceleration experienced by B
    let maxDecel = 0;
    for (let i = 0; i < n; i++) {
      if (Math.abs(traj.a_b[i]) > Math.abs(maxDecel)) maxDecel = traj.a_b[i];
    }
    indicators.max_decel = maxDecel;

    // 23. avg_decel: Average deceleration experienced by B
    let totalDecel = 0;
    let decelCount = 0;
    for (let i = 0; i < n; i++) {
      if (traj.a_b[i] < 0) {
        totalDecel += Math.abs(traj.a_b[i]);
        decelCount++;
      }
    }
    indicators.avg_decel = decelCount > 0 ? totalDecel / decelCount : 0;

    // 24. DOB: Degree of braking (actual / max possible)
    indicators.dob = (maxDecel !== 0 && a_follow_max !== 0)
      ? Math.abs(maxDecel / a_follow_max)
      : 0;

    // ===== KINEMATIC (5) =====

    // 25. delta_v: Velocity change at impact
    indicators.delta_v = deltaV;

    // 26. closing_speed: Maximum closing speed
    let maxClosingSpeed = 0;
    for (let i = 0; i < n; i++) {
      if (traj.v_rel[i] > maxClosingSpeed) maxClosingSpeed = traj.v_rel[i];
    }
    indicators.closing_speed = maxClosingSpeed;

    // 27. relative_accel: Relative acceleration
    let relAccel = null;
    for (let i = 0; i < n; i++) {
      const ra = traj.a_b[i] - traj.a_a[i];
      if (ra !== 0) {
        if (relAccel === null) relAccel = { values: [], sum: 0 };
        relAccel.values.push(ra);
        relAccel.sum += ra;
      }
    }
    indicators.relative_accel = relAccel ? relAccel.sum / relAccel.values.length : 0;

    // 28. relative_angle: Relative heading (rear-end = 0°)
    indicators.relative_angle = 0.0;

    // 29. speed_diff: Speed differential
    let speedDiff = [];
    for (let i = 0; i < n; i++) {
      speedDiff.push(Math.abs(traj.v_a[i] - traj.v_b[i]));
    }
    indicators.speed_diff = {
      min: Math.min(...speedDiff),
      max: Math.max(...speedDiff),
      mean: speedDiff.reduce((a, b) => a + b, 0) / speedDiff.length,
    };

    // ===== SEVERITY (6) =====

    // 30. delta_v_impact: Velocity change at impact
    indicators.delta_v_impact = deltaV;

    // 31. expected_severity: Based on NHTSA ES-28 correlation
    // Severity index from ΔV: S = (ΔV/40)^2 (normalized to fatal at 40 km/h)
    const deltaVKmh = deltaV * 3.6;
    indicators.expected_severity = Math.pow(deltaVKmh / 40.0, 2);

    // 32. kinetic_energy: KE dissipated at impact
    const mass = 1200; // kg, compact sedan
    indicators.kinetic_energy = 0.5 * mass * deltaV * deltaV / 1000; // kJ

    // 33. CSI: Collision severity index
    indicators.csI = indicators.expected_severity * 100;

    // 34. SRI: Severity risk index
    indicators.sri = indicators.expected_severity * cpi;

    // 35. PCE: Passenger car equivalent (1.0 for sedan vs sedan)
    indicators.pce = 1.0;

    // ===== PROBABILITY (6) =====

    // 36. CP: Collision probability
    indicators.cp = collisionTime !== null ? 1.0 : 0.0;

    // 37. CPI (decel-based): Already computed above

    // 38. pTTT: Probability of time-to-collision < 1s
    let pttt = null;
    if (ttcMin !== null && ttcMin < 1.0) pttt = ttcMin;
    indicators.pttt = pttt;

    // 39. CRI: Collision risk index (TTC⁻¹ × ΔV normalized)
    let cri = null;
    if (ttcMin !== null && ttcMin > 0) {
      cri = (1.0 / ttcMin) * (deltaV / 50.0) * 100;
    }
    indicators.cri = cri;

    // 40. RiskForce: Risk = gap⁻¹ × v_rel²
    let riskForce = null;
    let minRisk = Infinity;
    for (let i = 0; i < n; i++) {
      if (traj.gap[i] > 0.01 && traj.v_rel[i] > 0.01) {
        const rf = (traj.v_rel[i] * traj.v_rel[i]) / traj.gap[i];
        if (rf < minRisk) minRisk = rf;
      }
    }
    indicators.riskForce = minRisk === Infinity ? null : minRisk;

    // 41. ECF: Equivalent conflict frequency (per year, extrapolated)
    // Assuming 10,000 such events per year on this road segment
    const eventsPerYear = 10000;
    indicators.ecf = indicators.cp ? indicators.cp * eventsPerYear : 0;

    // 42. Bayesian P(collision): Placeholder — filled by bayesian-evt
    indicators.bayesian_p_collision = null;

    // Add aggregated statistics
    indicators.aggregated = {
      ttc_min: indicators.ttc,
      ttc_mean: indicators.tttc?.mean || null,
      gap_min: indicators.min_spatial_gap,
      gap_mean: indicators.gap_time?.mean || null,
      delta_v: indicators.delta_v,
      collision_occurred: indicators.cp > 0,
    };

    return indicators;
  }

  /**
   * Get trajectory data suitable for visualization (downsampled for 3D).
   */
  getVisualizationTrajectory() {
    const n = this.trajectory?.t.length;
    if (!n) return [];

    const downsampleFactor = Math.max(1, Math.floor(n / 500));
    const result = [];

    for (let i = 0; i < n; i += downsampleFactor) {
      result.push({
        t: this.trajectory.t[i],
        x: this.trajectory.x_a[i] - this.trajectory.x_b[i], // relative x
        y: 1.85, // lane center
        v_a: this.trajectory.v_a[i],
        v_b: this.trajectory.v_b[i],
        a_a: this.trajectory.a_a[i],
        a_b: this.trajectory.a_b[i],
        collision: this.trajectory.collision[i],
      });
    }

    return result;
  }
}

// Export for browser and Node
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { RearEndKinematics };
}
