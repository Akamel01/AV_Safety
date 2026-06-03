---
name: scenario-taxonomy
description: "Define and validate the complete taxonomy of traffic conflict scenarios that drive the collision risk playground."
---

# Scenario Taxonomy

Define, validate, and maintain the complete taxonomy of traffic conflict scenarios that drive the collision risk playground.

## 8 Conflict Types + Sub-Categories

### 1. Crossing
- Intersection crossing (perpendicular) — 90° intersection
- Mid-block crossing (jaywalking) — pedestrian outside crosswalk
- Crosswalk crossing — marked crosswalk with signal
- Bicycle crossing — cyclist crossing vehicle path

### 2. Merging
- Lane addition (on-ramp) — ramp to highway
- Cut-in (adjacent lane) — moves into lane ahead
- Shoulder merge — enters from shoulder
- Bus merge — pulls out from stop

### 3. Diverging
- Lane exit (off-ramp) — leaves lane to exit
- Lane change (outbound) — moves to right lane
- Right turn at intersection — turns right, blocking path

### 4. Weaving
- Short weave — closely spaced ramps
- Long weave — distant ramps
- Multi-vehicle weave — three or more vehicles
- Unsignalized weave — no traffic control

### 5. Rear-End
- Following scenario — varying gap
- Cut-in ahead — merges in front
- Sudden braking (lead) — abrupt deceleration
- Cut-under (close range) — merges <5m
- Traffic wave braking — propagates backward
- Stop-and-go rear-end — congested traffic

### 6. Sideswipe
- Same-direction — similar speed, different lanes
- Lane-change induced — during lane change
- Merging sideswipe — two lanes conflict
- Passing sideswipe — overtaking too close

### 7. Right-Angle
- Intersection right-angle — cross-traffic, one runs red/yellow
- T-bone at stop sign — one stops, other doesn't
- T-bone at signal — phase change, one too fast
- Rear-end → right-angle — chain reaction

### 8. Opposing Left-Turn
- Unprotected left across opposing — crosses opposing lane
- Protected left (yield scenario) — green with opposing green
- Both vehicles turning — both turn left across each other
- Left-turn across multi-lane — across multiple opposing lanes

## Severity Spectrum

Each scenario has 3 tiers:
- **Benign:** Collision probability < 5%, near safety threshold
- **Moderate:** Collision probability 5–50%, meaningful risk
- **Extreme:** Collision probability > 50%, near-certain crash

Parameters slide along spectrum continuously — benign → moderate → extreme with smooth transitions.

## Validation Requirements

1. **Literature alignment:** Each sub-category references at least one traffic safety study
2. **Realism:** Parameters within observed ranges in real crash data
3. **Spectrum continuity:** Benign → Moderate → Extreme smooth parameter transition
4. **Cross-type distinction:** Different conflict types produce distinctly different indicator patterns

## Reuse Trigger

Use when:
- Adding new conflict types or scenarios
- Defining parameters for a new animation
- Validating scenario realism
- Mapping indicators to conflicts
- Designing playground UI layout

## File Structure
```
src/scenario_taxonomy/
  conflict_types.py     Conflict type definitions
  scenarios.py          All scenario definitions (loaded from JSON)
  parameters.py         Parameter validation and normalization
  severity_levels.py    Severity spectrum definitions
  geometry.py           Road geometry generation
  validation.py         Validate scenarios against constraints
```
