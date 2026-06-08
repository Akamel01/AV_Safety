# Detailed Sub-Category Descriptions and Scenario Format

## Sub-Category Details

### Crossing Conflicts
1. **Intersection crossing (perpendicular):** Two vehicles cross at 90° intersection; parameters: approach speeds, intersection geometry, signal timing, reaction time
2. **Mid-block crossing (jaywalking):** Pedestrian crosses outside crosswalk; parameters: pedestrian speed, vehicle speed, crosswalk distance, visibility
3. **Crosswalk crossing:** Pedestrian at marked crosswalk; parameters: pedestrian speed, vehicle speed, signal phase, yielding rate
4. **Bicycle crossing:** Cyclist crossing vehicle path; parameters: cyclist speed, vehicle speed, crossing angle, bike type

### Merging Conflicts
5. **Lane addition (on-ramp):** Vehicle merges from ramp to highway; parameters: ramp speed, mainline speed, gap size, acceleration rate
6. **Cut-in (adjacent lane):** Vehicle moves into lane ahead; parameters: cut-in distance, speed differential, lane width, reaction time
7. **Shoulder merge:** Vehicle enters from shoulder; parameters: shoulder speed, adjacent lane speed, merge angle
8. **Bus merge:** Bus pulls out from stop; parameters: bus acceleration, passing speed, gap size

### Diverging Conflicts
9. **Lane exit (off-ramp):** Vehicle leaves lane to exit; parameters: deceleration rate, exit speed, timing
10. **Lane change (outbound):** Vehicle moves to right lane; parameters: speed differential, distance to target lane, signal use
11. **Right turn at intersection:** Vehicle turns right, blocking path; parameters: turn radius, speed, yielding behavior
12. **Lane divergence:** Vehicle drifts from lane without signal; parameters: lateral offset rate, speed differential, response time

### Weaving Conflicts
13. **Short weave (closely spaced ramps):** Vehicles cross paths between nearby ramps; parameters: weave length, merging/exiting speeds, lane position
14. **Long weave (distant ramps):** Vehicles cross paths between far ramps; parameters: weave length, speed differential, lane change timing
15. **Multi-vehicle weave:** Three or more vehicles in weave section; parameters: vehicle order, speed distribution, lane discipline
16. **Unsignalized weave:** Weave without traffic control; parameters: conflict frequency, priority rules

### Rear-End Conflicts
17. **Following scenario:** Vehicle follows another at varying gap; parameters: following distance, speed, deceleration rate, reaction time
18. **Cut-in ahead:** Vehicle merges in front of following car; parameters: cut-in distance, speed differential, following vehicle response
19. **Sudden braking (lead):** Leading vehicle brakes abruptly; parameters: lead deceleration, following distance, reaction time, road friction
20. **Cut-under (close range):** Vehicle merges extremely close; parameters: cut-in distance (<5m), speed differential, braking delay
21. **Traffic wave braking:** Braking propagates backward in traffic; parameters: braking wave speed, vehicle spacing, reaction time distribution
22. **Stop-and-go rear-end:** In congested traffic; parameters: jam density, shockwave speed, driver reaction time

### Sideswipe Conflicts
23. **Same-direction sideswipe:** Two vehicles at similar speed, different lanes; parameters: lane width, lateral offset, speed differential, vehicle width
24. **Lane-change induced:** During lane change, adjacent vehicle present; parameters: lane change rate, gap to adjacent vehicle, relative speed
25. **Merging sideswipe:** During merge, two lanes conflict; parameters: merge angle, lane width, vehicle position timing
26. **Passing sideswipe:** Overtaking vehicle too close; parameters: passing speed, gap to oncoming vehicle, vehicle width

### Right-Angle Conflicts
27. **Intersection right-angle (cross-traffic):** Two vehicles cross at intersection, one runs red/yellow; parameters: approach speeds, signal timing, running-red rate, intersection size
28. **T-bone at stop sign:** One vehicle stops, other doesn't; parameters: speed differential, stop compliance, intersection geometry
29. **T-bone at signal:** Signal phase change, one vehicle too fast; parameters: signal timing, yellow duration, approach speed, stopping distance
30. **Rear-end → right-angle:** Initial rear-end leads to right-angle; parameters: chain reaction dynamics, vehicle speed, braking capability

### Opposing Left-Turn Conflicts
31. **Unprotected left across opposing:** Turning vehicle crosses opposing traffic lane; parameters: turn speed, opposing speed, gap acceptance, sight distance
32. **Protected left (yield scenario):** Left turn with green, opposing also has green; parameters: turn speed, opposing speed, conflict zone timing
33. **Both vehicles turning (intersection):** Both turn left across each other (or both right); parameters: turn speeds, intersection geometry, turning path width
34. **Left-turn across multi-lane:** Turn across multiple opposing lanes; parameters: number of lanes, opposing speed distribution, gap across all lanes

## Scenario Parameter Specification Format

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

## Severity Spectrum Details

- **Benign:** Collision probability < 5%, severe indicators near safety threshold
- **Moderate:** Collision probability 5–50%, indicators show meaningful risk
- **Extreme:** Collision probability > 50%, near-certain crash with high severity
