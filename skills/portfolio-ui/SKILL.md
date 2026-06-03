---
name: portfolio-ui
description: "Build interactive collision risk playground: portfolio landing page, scenario selector, 3D/2D visualization, 42 indicator panel, Bayesian EVT integration."
---

# Portfolio UI

Build interactive collision risk playground: portfolio landing page, scenario selector, 3D/2D visualization, 42 indicator panel, Bayesian EVT integration.

## Goal

Interactive web-based "collision risk playground" featuring:
- 8 conflict types with parameterized scenarios
- 42 surrogate safety indicators
- Bayesian EVT risk quantification
- 3D animations (Three.js) + 2D fallback
- 16 featured scenarios + "View All" option

## What This Skill Does
- Portfolio landing page — conflict type navigation, scenario selector, risk metrics
- Interactive scenarios — dynamic parameter tuning, Monte Carlo simulation
- Visualization integration — 3D animation + Canvas 2D fallback, HUD overlay
- Risk computation — Bayesian EVT outputs (occurrence likelihood + severity)
- Indicator panel — all 42 surrogate safety metrics
- Responsive design — mobile-friendly, accessible

## What It Does NOT Do
- Not build bayesian-evt engine (depends on `bayesian-evt`)
- Not build 3d-animation module (depends on `3d-animation`)
- Not handle deployment (depends on `portfolio-deploy`)
- Not validate against real crash data (depends on `validation`)

## File Structure
```
/portfolio/
├── index.html         Landing page, navigation, scenario selector
├── app.js             Portfolio UI logic, state management
├── style.css          Responsive styles, layout
├── modules/
│   ├── risk-computation.js   Wraps bayesian-evt
│   ├── visualization.js      Wraps 3d-animation
│   └── indicators.js         42 indicator display
├── templates/
│   ├── scenario-card.html
│   └── conflict-type-nav.html
└── assets/
    ├── hud-overlay.svg
    └── responsive.css
```

## State Management
```javascript
const portfolioState = {
  currentConflictType: 'crossing',
  scenarioFilter: 'featured', // 'featured' | 'all'
  selectedScenario: null,
  parameters: { v1: 30, v2: 20, ttc: 1.2, headway: 2, visibility: 150 },
  sampleSize: 10000,
  mode: '3d', // '3d' | '2d'
  showIndicators: true
};
```

## Risk Computation API
```javascript
const riskComputation = {
  compute: async ({ conflictType, scenarioId, parameters, sampleSize }) =>
    // Delegates to bayesian-evt, returns { occurrenceLikelihood, severity, confidenceInterval }
  classifyRisk: (occurrenceLikelihood) =>
    // < 30: low, 30-50: moderate, 50-70: high, >= 70: critical
  getThresholds: (jurisdiction) =>
    // Returns { ttc, ssd, drac, pet, psdr } per jurisdiction
};
```

## Visualization API
```javascript
const visualization = {
  render: async ({ scene, conflictType, mode: '3d'|'2d', parameters }) =>
    // Delegates to 3d-animation, returns { canvas, hud, collisionFX }
  destroy: () => // Cleanup Three.js canvas
};
```

## Indicator API
```javascript
const indicators = {
  compute: (kinematics, parameters) =>
    // Delegates to indicator-computation, returns 42 metrics
  display: (metrics, thresholds) =>
    // Returns HTML with color-coded values (green/yellow/red)
};
```

## 8 Conflict Types
crossing, merging, diverging, weaving, rear-end, sideswipe, right-angle, opposing left-turn

## Performance Targets
| Metric | Target |
|---|-|
| Landing page load | < 2s |
| Scenario switch | < 3s |
| Monte Carlo (10k) | < 5s |
| 3D rendering | < 1s |
| Responsive resize | < 100ms |

## Optimization
- Lazy loading (3D models on demand)
- Pre-computed featured scenarios (cache 16)
- Progressive rendering (low-poly → high-poly)
- Web workers (Monte Carlo offload)
- Debounce parameter controls (300ms)
- Pagination for "View All"

## Testing Checklist
- [ ] Landing page loads, navigation works
- [ ] Featured scenarios + "View All" expand
- [ ] Scenario selector filters by conflict type
- [ ] Parameter controls update risk metrics
- [ ] Monte Carlo runs within timeout
- [ ] 3D renders (Three.js) + 2D fallback
- [ ] HUD overlay displays
- [ ] All 42 indicators display with color-coded thresholds
- [ ] Responsive on mobile
- [ ] Keyboard navigation works
- [ ] Error messages clear, loading states show progress
