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
- Lane divergence — drifts from lane without signal

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

Each scenario has 3 tiers mapped to collision probability bands:
- **Benign:** P(collision) < 5%, near safety threshold — indicators within normal range
- **Moderate:** P(collision) 5–50%, meaningful risk — indicators show escalating risk
- **Extreme:** P(collision) > 50%, near-certain crash — high-severity indicators

Parameters slide along spectrum continuously — benign → moderate → extreme with smooth transitions.

## Cross-Skill Dependencies

- **kinematics-engine** — conflict types drive trajectory computation
- **indicator-computation** — each sub-category maps to applicable indicators
- **stochastic-simulation** — severity spectrum drives parameter sampling distributions
- **3d-animation** — conflict types define animation scenario catalog
- **portfolio-ui** — conflict types form the playground scenario selector
- **data-ingest** — conflict types define target scenarios for data ingestion
- **risk-metrics** — conflict types map to risk metric computation targets

## Validation Requirements

1. **Literature alignment:** Each sub-category references at least one traffic safety study
2. **Realism:** Parameters within observed ranges in real crash data (NHTSA FARS, CISS, CMFwiki)
3. **Spectrum continuity:** Benign → Moderate → Extreme smooth parameter transition
4. **Cross-type distinction:** Different conflict types produce distinctly different indicator patterns
5. **Completeness:** All 8 conflict types have ≥4 sub-categories each

## Reuse Trigger

Use when:
- Adding new conflict types or scenarios
- Defining parameters for a new animation
- Validating scenario realism
- Mapping indicators to conflicts
- Designing playground UI layout

## Scenario JSON Schema

Each scenario follows the format in `references/sub-categories.md` and `single-scenario-demo/data/`:

```
single-scenario-demo/data/scenario-<CONFLICT_TYPE>-<JURISDICTION>-<NUMBER>.json
```

Key fields: `conflict_type`, `sub_category`, `severity_spectrum` (benign/moderate/extreme ranges), `applicable_indicators`, `road_geometry`, `road_users`, `monte_carlo_expected`.
