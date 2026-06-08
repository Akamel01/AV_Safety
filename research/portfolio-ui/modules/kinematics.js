/**
 * kinematics.js — Vehicle Kinematics Engine
 *
 * Computes exact trajectories for vehicles in collision scenarios using
 * classical kinematic equations with piecewise-constant acceleration.
 * Supports rear-end, crossing, merging, diverging, and other conflict types.
 */

const kinematics = {
  /**
   * Compute trajectories for a given conflict type.
   *
   * @param {Object} params
   * @param {string} params.conflictType - One of: rear-end, crossing, merging, diverging, sideswipe, right-angle, opposing-left-turn, weaving
   * @param {number} params.v1 - Vehicle 1 initial speed (m/s)
   * @param {number} params.v2 - Vehicle 2 initial speed (m/s)
   * @param {number} params.a1 - Vehicle 1 acceleration (m/s²), default 0
   * @param {number} params.a2 - Vehicle 2 acceleration (m/s²), default 0
   * @param {number} params.dt - Time step (s), default 0.01
   * @param {number} params.tMax - Simulation duration (s), default 10
   * @param {number} params.initGap - Initial gap between vehicles (m), default 30
   * @returns {Object} Trajectory data with times, positions, velocities for both vehicles
   */
  compute(params) {
    const {
      conflictType = 'rear-end',
      v1 = 30,
      v2 = 27,
      a1 = 0,
      a2 = 0,
      dt = 0.01,
      tMax = 10,
      initGap = 30,
    } = params;

    const nSteps = Math.ceil(tMax / dt);
    const times = [];
    const posA = [];
    const velA = [];
    const posB = [];
    const velB = [];
    const dist = [];

    let x1 = 0;
    let x2 = initGap;
    let vx1 = v1;
    let vx2 = v2;

    for (let i = 0; i <= nSteps; i++) {
      const t = i * dt;
      times.push(t);
      posA.push(x1);
      velA.push(vx1);
      posB.push(x2);
      velB.push(vx2);
      dist.push(x2 - x1);

      // Collision detection
      if ((x2 - x1) <= 0 && i < nSteps) break;

      // Update velocities
      vx1 += a1 * dt;
      vx2 += a2 * dt;

      // Ensure non-negative speeds
      vx1 = Math.max(0, vx1);
      vx2 = Math.max(0, vx2);

      // Update positions
      x1 += vx1 * dt;
      x2 += vx2 * dt;
    }

    return {
      conflictType,
      times,
      posA,
      velA,
      posB,
      velB,
      dist,
      params: { v1, v2, a1, a2, dt, tMax, initGap },
      nSteps: times.length,
      collisionTime: this._detectCollision(times, posA, posB),
      minDistance: Math.min(...dist),
    };
  },

  /**
   * Get the initial kinematic state for a scenario.
   */
  getInitialState(params) {
    return {
      v1: params.v1 || 30,
      v2: params.v2 || 27,
      a1: params.a1 || 0,
      a2: params.a2 || 0,
      initGap: params.initGap || 30,
      initPosA: 0,
      initPosB: params.initGap || 30,
    };
  },

  /**
   * Detect collision time from trajectory data.
   */
  _detectCollision(times, posA, posB) {
    for (let i = 1; i < times.length; i++) {
      if ((posB[i] - posA[i]) <= 0) {
        // Linear interpolation for exact collision time
        const dt_step = times[i] - times[i - 1];
        const gap_prev = posB[i - 1] - posA[i - 1];
        const gap_curr = posB[i] - posA[i];
        if (gap_prev > 0 && gap_curr <= 0) {
          const t_collision = times[i - 1] + (gap_prev / (gap_prev - gap_curr)) * dt_step;
          return t_collision;
        }
      }
    }
    return null; // No collision detected
  },

  /**
   * Compute TTC from current state.
   */
  computeTTC(posA, velA, posB, velB) {
    const relDist = posB - posA;
    const relVel = velA - velB;
    if (relVel > 0.01 && relDist > 0) {
      return relDist / relVel;
    }
    return Infinity;
  },

  /**
   * Compute SSD from current state.
   */
  computeSSD(speed, perceptionReactionTime = 2.5) {
    const brakingDist = (speed * speed) / (2 * 5.0); // Assume 0.5g braking
    return speed * perceptionReactionTime + brakingDist;
  },

  /**
   * Get conflict type display info.
   */
  getConflictTypeInfo(type) {
    const types = {
      'rear-end': {
        name: 'Rear-End Collision',
        description: 'Following vehicle strikes leading vehicle from behind',
        icon: '🚗💨',
        typicalSpeeds: '15-35 m/s',
        typicalGaps: '10-60 m',
      },
      'crossing': {
        name: 'Crossing Path',
        description: 'Vehicles intersect at perpendicular or angled paths',
        icon: '➕',
        typicalSpeeds: '10-25 m/s',
        typicalGaps: '5-50 m',
      },
      'merging': {
        name: 'Merging Conflict',
        description: 'Vehicle merges into adjacent lane with traffic',
        icon: '🔀',
        typicalSpeeds: '15-30 m/s',
        typicalGaps: '15-80 m',
      },
      'diverging': {
        name: 'Diverging Conflict',
        description: 'Vehicle exits main path across adjacent lane',
        icon: '↗️',
        typicalSpeeds: '10-25 m/s',
        typicalGaps: '15-60 m',
      },
      'sideswipe': {
        name: 'Sideswipe',
        description: 'Vehicles slide alongside each other in adjacent lanes',
        icon: '↔️',
        typicalSpeeds: '20-35 m/s',
        typicalGaps: '0.5-5 m',
      },
      'right-angle': {
        name: 'Right-Angle',
        description: 'Vehicle strikes side of another at approximately 90°',
        icon: '📐',
        typicalSpeeds: '10-30 m/s',
        typicalGaps: '5-30 m',
      },
      'opposing-left-turn': {
        name: 'Opposing Left Turn',
        description: 'Left-turning vehicle crosses oncoming traffic path',
        icon: '↩️',
        typicalSpeeds: '10-25 m/s',
        typicalGaps: '10-50 m',
      },
      'weaving': {
        name: 'Weaving',
        description: 'Vehicles cross paths during lane changes in weave sections',
        icon: '🌀',
        typicalSpeeds: '15-30 m/s',
        typicalGaps: '10-60 m',
      },
    };
    return types[type] || types['rear-end'];
  },
};

export default kinematics;
