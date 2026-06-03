# Skill: Scenario Taxonomy

**Purpose:** Define, validate, and maintain the complete taxonomy of traffic conflict scenarios that drive the collision risk playground.

## Conflict Type Taxonomy

### 1. Crossing Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Intersection crossing (perpendicular) | Two vehicles cross at 90° intersection | Approach speeds, intersection geometry, signal timing, reaction time |
| Mid-block crossing (jaywalking) | Pedestrian crosses road outside crosswalk | Pedestrian speed, vehicle speed, crosswalk distance, visibility |
| Crosswalk crossing | Pedestrian at marked crosswalk | Pedestrian speed, vehicle speed, signal phase, yielding rate |
| Bicycle crossing | Cyclist crossing vehicle path | Cyclist speed, vehicle speed, crossing angle, bike type |

### 2. Merging Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Lane addition (on-ramp) | Vehicle merges from ramp to highway | Ramp speed, mainline speed, gap size, acceleration rate |
| Cut-in (adjacent lane) | Vehicle moves into lane ahead | Cut-in distance, speed differential, lane width, reaction time |
| Shoulder merge | Vehicle enters from shoulder | Shoulder speed, adjacent lane speed, merge angle |
| Bus merge | Bus pulls out from stop | Bus acceleration, passing speed, gap size |

### 3. Diverging Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Lane exit (off-ramp) | Vehicle leaves lane to exit | Deceleration rate, exit speed, timing |
| Lane change (outbound) | Vehicle moves to right lane | Speed differential, distance to target lane, signal use |
| Right turn at intersection | Vehicle turns right, blocking path | Turn radius, speed, yielding behavior |

### 4. Weaving Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Short weave (closely spaced ramps) | Vehicles cross paths between nearby ramps | Weave length, merging/exiting speeds, lane position |
| Long weave (distant ramps) | Vehicles cross paths between far ramps | Weave length, speed differential, lane change timing |
| Multi-vehicle weave | Three or more vehicles in weave section | Vehicle order, speed distribution, lane discipline |
| Unsignalized weave | Weave without traffic control | Conflict frequency, priority rules |

### 5. Rear-End Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Following scenario | Vehicle follows another at varying gap | Following distance, speed, deceleration rate, reaction time |
| Cut-in ahead | Vehicle merges in front of following car | Cut-in distance, speed differential, following vehicle response |
| Sudden braking (lead) | Leading vehicle brakes abruptly | Lead deceleration, following distance, reaction time, road friction |
| Cut-under (close range) | Vehicle merges extremely close | Cut-in distance (<5m), speed differential, braking delay |
| Traffic wave braking | Braking propagates backward in traffic | Braking wave speed, vehicle spacing, reaction time distribution |
| Stop-and-go rear-end | In congested traffic | Jam density, shockwave speed, driver reaction time |

### 6. Sideswipe Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Same-direction sideswipe | Two vehicles at similar speed, different lanes | Lane width, lateral offset, speed differential, vehicle width |
| Lane-change induced | During lane change, adjacent vehicle present | Lane change rate, gap to adjacent vehicle, relative speed |
| Merging sideswipe | During merge, two lanes conflict | Merge angle, lane width, vehicle position timing |
| Passing sideswipe | Overtaking vehicle too close | Passing speed, gap to oncoming vehicle, vehicle width |

### 7. Right-Angle Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Intersection right-angle (cross-traffic) | Two vehicles cross at intersection, one runs red/yellow | Approach speeds, signal timing, running-red rate, intersection size |
| T-bone at stop sign | One vehicle stops, other doesn't | Speed differential, stop compliance, intersection geometry |
| T-bone at signal | Signal phase change, one vehicle too fast | Signal timing, yellow/duration, approach speed, stopping distance |
| Rear-end → right-angle | Initial rear-end leads to right-angle | Chain reaction dynamics, vehicle speed, braking capability |

### 8. Opposing Left-Turn Conflicts
| Sub-category | Description | Key Parameters |
|---|---|---|
| Unprotected left across opposing | Turning vehicle crosses opposing traffic lane | Turn speed, opposing speed, gap acceptance, sight distance |
| Protected left (yield scenario) | Left turn with green, opposing also has green | Turn speed, opposing speed, conflict zone timing |
| Both vehicles turning (intersection) | Both turn left across each other (or both right) | Turn speeds, intersection geometry, turning path width |
| Left-turn across multi-lane | Turn across multiple opposing lanes | Number of lanes, opposing speed distribution, gap across all lanes |

## Scenario Parameter Specification Format

Each scenario is defined by:

```json
{
  "conflict_type": "rear-end",
  "sub_category": "cut-in-ahead",
  "scenario_id": "RE-CA-001",
  "road_geometry": {
    "num_lanes": 2,
    "lane_width_m": 3.5,
    "road_type": "urban",
    "surface": "dry",
    "friction_coefficient": 0.7
  },
  "severity_parameters": {
    "vehicle_lead": {
      "length_m": 4.5,
      "width_m": 1.8,
      "mass_kg": 1500,
      "initial_speed_ms": 13.9,
      "acceleration_ms2": 0.0,
      "deceleration_ms2": -4.0
    },
    "vehicle_following": {
      "length_m": 4.5,
      "width_m": 1.8,
      "mass_kg": 1500,
      "initial_speed_ms": 18.0,
      "acceleration_ms2": 0.0,
      "deceleration_ms2": -7.0
    },
    "cut_in_distance_m": 25.0,
    "reaction_time_s": 1.5,
    "braking_delay_s": 0.3
  },
  "severity_spectrum": {
    "benign": {"cut_in_distance_m": [30, 50], "reaction_time_s": [1.0, 1.5]},
    "moderate": {"cut_in_distance_m": [15, 25], "reaction_time_s": [1.5, 2.0]},
    "extreme": {"cut_in_distance_m": [5, 15], "reaction_time_s": [2.0, 3.0]}
  },
  "applicable_indicators": ["TTC", "MTTC", "DRAC", "Delta-V", "CPI", "PCE", "RLA", "MADR"],
  "references": ["NHTSA 4-Star Safety Rating", "Li et al. 2020"]
}
```

## Severity Spectrum per Conflict Type

Each conflict type has a 3-tier severity classification:

- **Benign:** Collision probability < 5%, severe indicators near safety threshold
- **Moderate:** Collision probability 5-50%, indicators show meaningful risk
- **Extreme:** Collision probability > 50%, near-certain crash with high severity

The severity parameters are designed so that the user can slide along the spectrum and see the indicators and animation respond continuously.

## Validation Requirements

1. **Literature alignment:** Each sub-category must reference at least one traffic safety study that uses it
2. **Realism:** Parameters must fall within observed ranges in real crash data
3. **Spectrum continuity:** Benign → Moderate → Extreme must be a smooth parameter transition
4. **Cross-type distinction:** Different conflict types must produce distinctly different indicator patterns

## File Structure

```
src/scenario_taxonomy/
  conflict_types.py        — Conflict type definitions and metadata
  scenarios.py             — All scenario definitions (loaded from JSON)
  parameters.py            — Parameter validation and normalization
  severity_levels.py       — Severity spectrum definitions
  geometry.py              — Road geometry generation
  validation.py            — Validate scenarios against constraints
```

```
docs/scenario_taxonomy/
  crossing-scenarios.md
  merging-scenarios.md
  diverging-scenarios.md
  weaving-scenarios.md
  rear-end-scenarios.md
  sideswipe-scenarios.md
  right-angle-scenarios.md
  opposing-left-turn-scenarios.md
```

## Reuse

This skill is used when:
- Adding new conflict types or scenarios
- Defining parameters for a new animation
- Validating scenario realism
- Mapping indicators to conflicts
- Designing the playground UI layout
