"""
Kinematics Engine — Exact trajectory simulation for rear-end collision scenarios.

Mirrors the JS RearEndKinematics class in single-scenario-demo/modules/kinematics.js
with full timestep simulation (2.5ms sub-steps) for accurate collision detection.

Physics:
  - Constant acceleration kinematic equations
  - AABB collision detection per timestep (gap ≤ 0 = bodies overlap)
  - Perception-reaction delay for following vehicle
  - Brake lag for both vehicles
  - Delta-V computed at collision from velocity differential
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VehicleState:
    """Current state of a single vehicle."""
    x: float = 0.0          # Position (m)
    v: float = 0.0          # Velocity (m/s)
    a: float = 0.0          # Acceleration (m/s^2)


@dataclass
class SimulationConfig:
    """Simulation parameters — mirrors JS RearEndKinematics.validateParams()."""
    # Initial conditions
    v_a0: float = 27.8      # Lead vehicle initial velocity (m/s)
    v_b0: float = 27.8      # Following vehicle initial velocity (m/s)
    headway: float = 30.0   # Initial gap between vehicles (m)

    # Driver/brake behavior
    reaction_time: float = 1.5    # Following vehicle perception-reaction time (s)
    t_brake_event: float = 3.0    # Time when lead vehicle begins braking (s)
    brake_lag: float = 0.15       # Brake engagement lag for both vehicles (s)

    # Vehicle capabilities
    a_lead: float = -5.0        # Lead vehicle deceleration (m/s^2), negative = braking
    a_follow_max: float = -8.0  # Following vehicle max deceleration (m/s^2)

    # Vehicle geometry
    vehicle_length: float = 4.3  # Vehicle length (m)
    lane_width: float = 3.7    # Lane width (m)

    # Simulation parameters
    sim_duration: float = 15.0  # Total simulation time (s)
    dt: float = 0.0025        # Timestep (2.5ms for accuracy)

    # Velocity bounds
    v_min: float = 0.0       # Minimum velocity (m/s)
    v_max: float = 35.0      # Maximum velocity (m/s)


@dataclass
class TrajectoryPoint:
    """Single timestep state in the trajectory."""
    t: float      # Time (s)
    x_a: float    # Lead vehicle position (m)
    x_b: float    # Following vehicle position (m)
    v_a: float    # Lead vehicle velocity (m/s)
    v_b: float    # Following vehicle velocity (m/s)
    a_a: float    # Lead vehicle acceleration (m/s^2)
    a_b: float    # Following vehicle acceleration (m/s^2)
    gap: float    # Safe gap (front of A to rear of B) (m)
    v_rel: float  # Relative velocity (B - A), positive = closing (m/s)
    ttc: float    # Time-to-collision (s), Infinity if safe
    collision: bool = False  # Whether collision occurred at this point


@dataclass
class CollisionResult:
    """Result of a simulation run — collision or non-collision."""
    collision: bool
    ttc: Optional[float] = None       # Time-to-collision from simulation start (s)
    ttc_at_peak: Optional[float] = None  # Minimum TTC during simulation (s)
    min_gap: Optional[float] = None   # Minimum gap during simulation (m)
    delta_v: float = 0.0            # Change in velocity at collision (m/s)
    collision_time: Optional[float] = None  # Exact collision time (s)
    v_a_final: float = 0.0          # Lead vehicle velocity at collision (m/s)
    v_b_final: float = 0.0          # Following vehicle velocity at collision (m/s)
    simulation_time: float = 0.0    # How long simulation ran before collision (s)


class KinematicsEngine:
    """
    Runs exact kinematic trajectory simulation for rear-end collision scenarios.

    Algorithm:
    1. Initialize two vehicles: A (lead) at x=0, B (following) at x=-headway
    2. At t_brake_event, lead vehicle begins braking (after brake_lag delay)
    3. At t_brake_event + reaction_time, following vehicle begins reacting (after brake_lag)
    4. Following vehicle computes required deceleration to maintain gap
    5. Collision detected when gap ≤ 0 (bodies overlap)
    6. If collision occurs, linear interpolation for exact collision time
    7. Delta-V computed from velocity differential at collision point

    This mirrors the JS implementation in single-scenario-demo/modules/kinematics.js
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self._init_state()

    def _init_state(self):
        """Reset to initial conditions."""
        cfg = self.config
        self.state_a = VehicleState(x=0.0, v=cfg.v_a0, a=0.0)
        self.state_b = VehicleState(x=-cfg.headway, v=cfg.v_b0, a=0.0)

        # Event triggers
        self._brake_triggered = False
        self._brake_lag_timer = cfg.t_brake_event + cfg.brake_lag
        self._b_reaction_triggered = False
        self._b_lag_timer = cfg.t_brake_event + cfg.reaction_time + cfg.brake_lag

        # Storage
        self.trajectory: list[TrajectoryPoint] = []

        # Collision tracking
        self.collision_result = CollisionResult(collision=False)

    def run(self) -> CollisionResult:
        """
        Run the full simulation and return collision result.

        Returns: CollisionResult with collision status, TTC, delta-V, etc.
        """
        cfg = self.config
        n_steps = int(cfg.sim_duration / cfg.dt)

        min_ttc = float('inf')
        min_gap = float('inf')
        prev_gap = float('inf')

        for step in range(n_steps):
            t = step * cfg.dt

            # === Update vehicle A (lead) ===
            if t >= cfg.t_brake_event and not self._brake_triggered:
                self._brake_triggered = True
                self._brake_lag_timer = t + cfg.brake_lag

            if t >= self._brake_lag_timer:
                self.state_a.a = max(cfg.a_lead, -10.0)  # Clamp max decel
                self.state_a.v += self.state_a.a * cfg.dt
                self.state_a.v = max(cfg.v_min, min(cfg.v_max, self.state_a.v))

            self.state_a.x += self.state_a.v * cfg.dt

            # === Update vehicle B (following) ===
            if not self._b_reaction_triggered and t >= cfg.t_brake_event + cfg.reaction_time:
                self._b_reaction_triggered = True
                self._b_lag_timer = t + cfg.brake_lag

            if self._b_reaction_triggered and t >= self._b_lag_timer:
                # Compute required deceleration to avoid collision
                gap = self._compute_gap()
                v_rel = self.state_b.v - self.state_a.v

                if v_rel > 0 and gap > cfg.vehicle_length:
                    # Required decel to maintain gap
                    required_a = -(v_rel ** 2) / (2 * max(gap - cfg.vehicle_length, 0.1))
                    self.state_b.a = max(cfg.a_follow_max, min(required_a, 0))
                else:
                    self.state_b.a = cfg.a_follow_max

                # Clamp to max capability
                self.state_b.a = max(self.state_b.a, cfg.a_follow_max)

                self.state_b.v += self.state_b.a * cfg.dt
                self.state_b.v = max(cfg.v_min, min(cfg.v_max, self.state_b.v))

            self.state_b.x += self.state_b.v * cfg.dt

            # === Compute metrics ===
            gap = self._compute_gap()
            v_rel = self.state_b.v - self.state_a.v

            # TTC: gap / v_rel if closing and gap > 0
            ttc = float('inf')
            if v_rel > 0.001 and gap > 0:
                ttc = gap / v_rel

            # Collision: gap ≤ 0 (bodies overlap, with -1cm tolerance)
            is_collision = gap <= -0.01

            # Store trajectory point
            self.trajectory.append(TrajectoryPoint(
                t=t,
                x_a=self.state_a.x,
                x_b=self.state_b.x,
                v_a=self.state_a.v,
                v_b=self.state_b.v,
                a_a=self.state_a.a,
                a_b=self.state_b.a,
                gap=gap,
                v_rel=v_rel,
                ttc=ttc,
                collision=is_collision,
            ))

            # Track extremes (only for non-collided steps)
            if not is_collision:
                if ttc > 0 and ttc < min_ttc:
                    min_ttc = ttc
                if gap < min_gap:
                    min_gap = gap

            # Detect first collision crossing: prev was safe, current is collision
            # Also handle vehicles starting already overlapping (step 0 collision)
            if is_collision and (step == 0 or prev_gap > -0.01):
                # This is the FIRST collision step:
                #   - step 0: vehicles start overlapping (zero/short headway)
                #   - step > 0: gap crossed from safe to unsafe this step
                if step == 0:
                    # Vehicles start overlapping — collision at t=0
                    collision_time = 0.0
                else:
                    # Linear interpolation for exact collision time between
                    # previous safe step and current collision step
                    prev_t = (step - 1) * cfg.dt
                    dt_between = t - prev_t
                    if abs(prev_gap - gap) > 0.0001:
                        frac = prev_gap / (prev_gap - gap)  # fraction of dt_between where gap crosses 0
                        collision_time = prev_t + dt_between * frac
                    else:
                        collision_time = t

                self.collision_result = CollisionResult(
                    collision=True,
                    collision_time=collision_time,
                    ttc=0.0,
                    min_gap=min_gap if min_gap != float('inf') else gap,
                    delta_v=max(0.0, v_rel),  # Delta-V from velocity differential
                    ttc_at_peak=min_ttc if min_ttc != float('inf') else None,
                    v_a_final=self.state_a.v,
                    v_b_final=self.state_b.v,
                    simulation_time=collision_time,
                )
                return self.collision_result

            prev_gap = gap

            if t >= cfg.sim_duration:
                break

        # No collision detected — return non-collision result
        self.collision_result = CollisionResult(
            collision=False,
            ttc=min_ttc if min_ttc != float('inf') else None,
            min_gap=min_gap if min_gap != float('inf') else prev_gap,
            simulation_time=cfg.sim_duration,
            v_a_final=self.state_a.v,
            v_b_final=self.state_b.v,
        )
        return self.collision_result

    def _compute_gap(self) -> float:
        """
        Compute safe gap between vehicles.

        Gap = x_a - x_b - vehicle_length
        Where x_a is front of lead vehicle, x_b is rear of following vehicle.
        Positive gap = safe distance, ≤ 0 = collision (overlap).
        """
        cfg = self.config
        return self.state_a.x - self.state_b.x - cfg.vehicle_length

    def run_batch(self, configs: list[SimulationConfig]) -> list[CollisionResult]:
        """Run multiple simulations and return results for each."""
        return [self.run_for_config(cfg) for cfg in configs]

    def run_for_config(self, config: SimulationConfig) -> CollisionResult:
        """Run simulation with a specific config and reset for next run."""
        old_config = self.config
        self.config = config
        try:
            return self.run()
        finally:
            self.config = old_config


def run_simple_rear_end(
    v_a0: float = 27.8,
    v_b0: float = 27.8,
    headway: float = 30.0,
    reaction_time: float = 1.5,
    a_lead: float = -5.0,
    a_follow_max: float = -8.0,
    sim_duration: float = 15.0,
) -> CollisionResult:
    """
    Convenience function for quick rear-end simulation.

    Default: highway rear-end, 100 km/h both vehicles, 30m headway,
    lead brakes at -5 m/s², following can brake at -8 m/s².
    """
    config = SimulationConfig(
        v_a0=v_a0,
        v_b0=v_b0,
        headway=headway,
        reaction_time=reaction_time,
        a_lead=a_lead,
        a_follow_max=a_follow_max,
        sim_duration=sim_duration,
    )
    engine = KinematicsEngine(config)
    return engine.run()


def run_monte_carlo_samples(
    n_samples: int = 10000,
    distributions: Optional[dict] = None,
    seed: Optional[int] = None,
) -> dict:
    """
    Monte Carlo simulation using the full kinematics engine.

    For each sample, draws parameters from distributions and runs
    the kinematics engine to compute actual collision statistics.

    Args:
        n_samples: Number of Monte Carlo samples
        distributions: Dict mapping parameter names to (mean, std) tuples
        seed: Random seed for reproducibility

    Returns:
        Dict with collision_rate, ttc statistics, delta-V statistics, etc.
    """
    import random
    if seed is not None:
        random.seed(seed)

    default_distributions = {
        "v_a0": (27.8, 1.0),       # Lead vehicle speed ~100 km/h ± 3.6 km/h
        "v_b0": (27.8, 1.0),       # Following vehicle speed
        "headway": (30.0, 5.0),    # Initial gap ~30m ± 5m
        "t_reaction": (1.5, 0.3),  # Reaction time ~1.5s ± 0.3s
        "a_lead": (-5.0, 1.0),     # Lead deceleration ~5 m/s² ± 1 m/s²
        "a_follow_max": (-8.0, 1.0), # Follow deceleration ~8 m/s² ± 1 m/s²
    }
    dists = distributions or default_distributions

    collisions = 0
    ttcs = []
    delta_vs = []
    min_gaps = []
    collision_times = []

    for _ in range(n_samples):
        # Sample parameters
        params = {}
        for key, (mu, sigma) in dists.items():
            val = random.gauss(mu, sigma)
            # Apply bounds
            if key == "v_a0":
                val = max(15.0, min(35.0, val))  # 54-126 km/h
            elif key == "v_b0":
                val = max(15.0, min(35.0, val))
            elif key == "headway":
                val = max(5.0, min(60.0, val))
            elif key == "t_reaction":
                val = max(0.5, min(4.0, val))
            elif key == "a_lead":
                val = max(-10.0, min(0.0, val))
            elif key == "a_follow_max":
                val = max(-12.0, min(0.0, val))
            params[key] = val

        # Run kinematics engine for this sample
        config = SimulationConfig(
            v_a0=params["v_a0"],
            v_b0=params["v_b0"],
            headway=params["headway"],
            reaction_time=params["t_reaction"],
            a_lead=params["a_lead"],
            a_follow_max=params["a_follow_max"],
        )
        engine = KinematicsEngine(config)
        result = engine.run()

        if result.collision:
            collisions += 1
            delta_vs.append(result.delta_v)
            collision_times.append(result.collision_time)
        else:
            if result.ttc is not None and result.ttc != float('inf'):
                ttcs.append(result.ttc)
            if result.min_gap is not None and result.min_gap != float('inf'):
                min_gaps.append(result.min_gap)

    collision_rate = collisions / n_samples

    return {
        "n_samples": n_samples,
        "collision_rate": collision_rate,
        "n_collisions": collisions,
        "collision_rate_ci95": (
            max(0, collision_rate - 1.96 * (collision_rate * (1 - collision_rate) / n_samples) ** 0.5),
            min(1.0, collision_rate + 1.96 * (collision_rate * (1 - collision_rate) / n_samples) ** 0.5),
        ),
        "ttc_mean": sum(ttcs) / len(ttcs) if ttcs else None,
        "ttc_std": (sum((t - sum(ttcs) / len(ttcs)) ** 2 for t in ttcs) / len(ttcs)) ** 0.5 if ttcs else None,
        "ttc_min": min(ttcs) if ttcs else None,
        "ttc_max": max(ttcs) if ttcs else None,
        "delta_v_mean": sum(delta_vs) / len(delta_vs) if delta_vs else None,
        "delta_v_max": max(delta_vs) if delta_vs else None,
        "min_gap_mean": sum(min_gaps) / len(min_gaps) if min_gaps else None,
        "mean_collision_time": sum(collision_times) / len(collision_times) if collision_times else None,
    }
