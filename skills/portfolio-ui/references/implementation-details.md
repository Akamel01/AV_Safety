# Portfolio UI Implementation Details

## Landing Page (index.html)

- Conflict type navigation (8 cards with icons, descriptions, sample metrics)
- Featured scenarios (16 cards: 2 per conflict type)
- "View All Scenarios" button → expand full scenario list
- Risk threshold display (UL 4600, ISO 21448 guidance)

## Scenario Card Template (scenario-card.html)
```html
<div class="scenario-card" data-conflict-type="{{conflictType}}" data-scenario-id="{{scenarioId}}">
  <span class="conflict-type-badge">{{conflictType}}</span>
  <span class="scenario-id">{{scenarioId}}</span>
  <h3 class="scenario-title">{{title}}</h3>
  <p class="scenario-description">{{description}}</p>
  <div class="preview-metrics">
    <div class="metric-item"><span>Risk</span><span class="{{riskClass}}">{{risk}}%</span></div>
    <div class="metric-item"><span>TTC</span><span>{{ttc}}s</span></div>
    <div class="metric-item"><span>Sample</span><span>{{sampleSize}}</span></div>
  </div>
  <div class="scenario-parameters">
    <div><span>v₁:</span><span>{{v1}} km/h</span></div>
    <div><span>v₂:</span><span>{{v2}} km/h</span></div>
    <div><span>Headway:</span><span>{{headway}}m</span></div>
    <div><span>Visibility:</span><span>{{visibility}}m</span></div>
  </div>
  <button data-action="view-scenario">View Scenario</button>
  <button data-action="compare-scenario">Compare</button>
</div>
```

## Conflict Type Navigation (conflict-type-nav.html)
- 8 navigation cards with icons
- Scenario count, average risk per type
- Click → show all scenarios of that type

## Parameter Controls
- Dynamic sliders for: v1, v2, TTC, headway, visibility
- Vehicle type selector (car, truck, bike)
- Monte Carlo sample size (1,000–100,000)
- Debounce controls (300ms)

## Risk Computation Module (risk-computation.js)
```javascript
const riskComputation = {
  compute: async (params) => {
    // Delegates to bayesian-evt skill
    // Validate inputs: conflictType, scenarioId, parameters
    const result = await bayesianEvt.compute(params);
    result.metadata = { ...params, computedAt: new Date().toISOString() };
    return result;
  },
  batchCompute: async (scenarios, sampleSize) => {
    // Compute risks for multiple scenarios in parallel
  },
  classifyRisk: (likelihood) => {
    if (likelihood >= 70) return 'critical';
    if (likelihood >= 50) return 'high';
    if (likelihood >= 30) return 'moderate';
    return 'low';
  },
  getThresholds: (jurisdiction) => ({
    usa: { ttc: 1.5, ssd: 2.0, drac: 2.0, pet: 1.0, psdr: 0.8 },
    canada: { ttc: 1.5, ssd: 2.0, drac: 2.0, pet: 1.0, psdr: 0.8 },
    england: { ttc: 1.5, ssd: 2.0, drac: 2.0, pet: 1.0, psdr: 0.8 }
  })
};
```

## Visualization Module (visualization.js)
```javascript
const visualization = {
  render: async (params) => {
    // Delegates to 3d-animation skill
    // params: { scene, conflictType, mode: '3d'|'2d', parameters }
    // Returns: { canvas, hud, collisionFX }
  },
  destroy: () => {
    // Cleanup Three.js canvas, event listeners
  }
};
```

## Indicator Module (indicators.js)
```javascript
const indicators = {
  compute: (kinematics, parameters) =>
    // Delegates to indicator-computation skill
    // Returns 42 metrics object
  display: (metrics, thresholds) => {
    // Color-coded display (green/yellow/red)
    // Confidence intervals from Bayesian EVT
    // Comparison to jurisdictional standards
  }
};
```

## Error Handling
- **bayesian-evt failure:** Show user-friendly error, fallback to default params, log error
- **3d-animation failure:** Auto-switch to Canvas 2D mode, show notification
- **Monte Carlo timeout:** Show progress indicator, allow reducing sample size
- **Network failure:** Retry with exponential backoff

## Responsive Design
- Mobile-first layout
- Adaptive grid for scenario cards (1 col mobile, 2-3 col desktop)
- Touch-friendly controls (min 44px tap targets)
- Readable font sizes (min 16px input labels)
- Horizontal scroll for indicator panels on small screens
