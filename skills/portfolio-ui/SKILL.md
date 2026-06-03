# portfolio-ui — Interactive Collision Risk Playground

**Skill:** Web-based portfolio UI for AV_Safety project
**Dependencies:** `bayesian-evt`, `3d-animation`
**Output:** `/portfolio` landing page with interactive scenarios
**Audience:** Technical, safety-critical, regulatory stakeholders

---

## Goal

Build an interactive web-based "collision risk playground" featuring:
- 8 conflict types (crossing, merging, diverging, weaving, rear-end, sideswipe, right-angle, opposing left-turn)
- 42 surrogate safety indicators
- Bayesian EVT risk quantification
- 3D animations (Three.js) + 2D fallback
- 16 featured scenarios + "View All" option

---

## Scope

### What This Skill Does
- **Portfolio landing page** — Conflict type navigation, scenario selector, risk metrics display
- **Interactive scenarios** — Dynamic parameter tuning, Monte Carlo simulation
- **Visualization integration** — 3D animation + Canvas 2D fallback, HUD overlay
- **Risk computation** — Bayesian EVT outputs (occurrence likelihood + severity)
- **Indicator panel** — All 42 surrogate safety metrics
- **Responsive design** — Mobile-friendly, accessible

### What It Does NOT Do
- **Not** build bayesian-evt computation engine (depends on `bayesian-evt` skill)
- **Not** build 3d-animation module (depends on `3d-animation` skill)
- **Not** handle deployment (depends on `portfolio-deploy` skill)
- **Not** validate against real crash data (depends on `validation` skill)

---

## Architecture

### File Structure
```
/portfolio/
├── index.html              # Landing page, navigation, scenario selector
├── app.js                  # Portfolio UI logic, state management
├── style.css               # Responsive styles, layout
├── modules/
│   ├── risk-computation.js # Wraps bayesian-evt module
│   ├── visualization.js    # Wraps 3d-animation module
│   └── indicators.js       # 42 surrogate safety indicators display
├── templates/
│   ├── scenario-card.html  # Template for featured scenarios
│   └── conflict-type-nav.html
└── assets/
    ├── hud-overlay.svg     # Heads-up display overlay
    └── responsive.css      # Mobile styles
```

### Data Flow
```
User Input → Portfolio UI State
    ↓
Risk Computation (bayesian-evt)
    ↓
Visualization (3d-animation)
    ↓
Indicator Panel (42 metrics)
    ↓
3D + HUD → User Output
```

---

## Core Features

### 1. Landing Page
- **Conflict Type Navigation:** 8 cards with icons, descriptions, sample metrics
- **Featured Scenarios:** 16 cards (2 per conflict type)
- **"View All Scenarios" Button:** Expands to full scenario list
- **Risk Thresholds:** UL 4600, ISO 21448 guidance

### 2. Scenario Selector
- **Filter by Conflict Type:** All, crossing, merging, diverging, weaving, rear-end, sideswipe, right-angle, opposing left-turn
- **Featured Only vs All:** Toggle switch
- **Parameter Controls:** Dynamic sliders for:
  - Approach speeds (v1, v2)
  - Time-to-collision (TTC)
  - Headway distances
  - Lane width, visibility
  - Vehicle type (car, truck, bike)
- **Monte Carlo Sample Size:** 1,000 to 100,000 iterations

### 3. Risk Computation Module
Wraps `bayesian-evt` skill:
```javascript
// Example API
const riskResult = await riskComputation.compute({
  conflictType: 'crossing',
  scenario: 'crossing-right-oncoming',
  parameters: { v1: 30, v2: 20, ttc: 1.2, visibility: 150 },
  sampleSize: 10000
});

// Returns: { occurrenceLikelihood, severity, confidenceInterval }
```

### 4. Visualization Module
Wraps `3d-animation` skill:
```javascript
// Example API
await visualization.render({
  scene: 'crossing',
  conflictType: 'right-angle',
  mode: '3d', // or '2d'
  parameters: { v1: 30, v2: 20 }
});

// Returns: Three.js canvas, HUD overlay, collision FX
```

### 5. Indicator Panel
Displays 42 surrogate safety indicators:
- **Time-based:** TTC, PTAC, PET, IDMR, DRM
- **Distance-based:** SSR, SSD, SSD_2s, 1.5s SSD
- **Deceleration-based:** PSDR, DRAC, IDRA
- **Kinematic:** VCR, SCR, OSCR, TAC, PAC, CR, CR2, DCR, DCR2
- **Severity:** VRC, FCR, NRC, RCR, NCR
- **Probability:** PTC, PCC, PDC, PSC, PDC2, PDC3, PCC2

**Display Format:**
- Numeric values with units
- Color-coded thresholds (green/yellow/red)
- Confidence intervals from Bayesian EVT
- Comparison to jurisdictional standards (NHTSA, Transport Canada, DfT GB)

---

## Implementation Steps

### Phase 1: Structure
1. Create portfolio directory structure
2. Implement landing page (`index.html`)
3. Create navigation component (`conflict-type-nav.html`)
4. Create scenario card template (`scenario-card.html`)

### Phase 2: UI Logic
1. Build portfolio UI state management (`app.js`)
2. Implement scenario selector with filters
3. Create parameter controls (sliders, toggles)
4. Add Monte Carlo sample size selector

### Phase 3: Module Integration
1. Wrap bayesian-evt module (`risk-computation.js`)
2. Wrap 3d-animation module (`visualization.js`)
3. Implement indicator display (`indicators.js`)

### Phase 4: 3D + 2D Fallback
1. Implement Three.js rendering
2. Add Canvas 2D fallback mode
3. Create HUD overlay integration
4. Add collision FX triggers

### Phase 5: Polish
1. Responsive design (mobile-friendly)
2. Accessibility (ARIA labels, keyboard nav)
3. Loading states, error handling
4. Performance optimization (lazy loading)

---

## API Reference

### Portfolio UI State
```javascript
const portfolioState = {
  currentConflictType: 'crossing',
  scenarioFilter: 'featured', // 'featured' | 'all'
  selectedScenario: null,
  parameters: {
    v1: 30, v2: 20, ttc: 1.2, headway: 2, visibility: 150
  },
  sampleSize: 10000,
  mode: '3d', // '3d' | '2d'
  showIndicators: true
};
```

### Risk Computation API
```javascript
const riskComputation = {
  compute: async (params) => {
    // Delegates to bayesian-evt skill
    // Returns: { occurrenceLikelihood, severity, confidenceInterval }
  }
};
```

### Visualization API
```javascript
const visualization = {
  render: async (params) => {
    // Delegates to 3d-animation skill
    // Returns: { canvas, hud, collisionFX }
  },
  destroy: () => {
    // Cleanup Three.js canvas
  }
};
```

### Indicator API
```javascript
const indicators = {
  compute: (kinematics, parameters) => {
    // Delegates to indicator-computation skill
    // Returns: { ttc: 2.3, ssr: 12.5, ... } // 42 metrics
  },
  display: (metrics, thresholds) => {
    // Returns HTML string with color-coded values
  }
};
```

---

## Configuration

### Environment Variables
```bash
PORT=3000
HOST=0.0.0.0
DEBUG=false
RENDER_MODE=3d  # '3d' or '2d'
SAMPLE_SIZE=10000
```

### Thresholds (Jurisdiction-Specific)
```javascript
const thresholds = {
  usa: { ttc: 1.5, ssd: 2.0, drac: 2.0 },
  canada: { ttc: 1.5, ssd: 2.0, drac: 2.0 },
  england: { ttc: 1.5, ssd: 2.0, drac: 2.0 }
};
```

---

## Error Handling

### What If bayesian-evt Fails?
- Show user-friendly error message
- Fall back to default parameter values
- Log error for debugging
- Allow user to retry

### What If 3d-animation Fails?
- Switch to Canvas 2D mode automatically
- Show notification to user
- Log error for debugging

### What If Monte Carlo Takes Too Long?
- Show progress indicator
- Allow user to reduce sample size
- Show estimated time remaining

---

## Testing Checklist

- [ ] Landing page loads correctly
- [ ] Conflict type navigation works
- [ ] Featured scenarios display correctly
- [ ] "View All Scenarios" expands full list
- [ ] Scenario selector filters by conflict type
- [ ] Parameter controls update risk metrics
- [ ] Monte Carlo simulation runs within timeout
- [ ] 3D rendering works (Three.js)
- [ ] Canvas 2D fallback works
- [ ] HUD overlay displays correctly
- [ ] All 42 indicators display (no missing metrics)
- [ ] Color-coded thresholds work (green/yellow/red)
- [ ] Responsive design works on mobile
- [ ] Keyboard navigation works (tab index)
- [ ] Error messages are clear
- [ ] Loading states show progress
- [ ] Performance is acceptable (< 5s per scenario)

---

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading:** Load 3D models only when needed
2. **Pre-computed Featured Scenarios:** Cache 16 featured scenario risk outputs
3. **Progressive Rendering:** Show low-poly 3D while loading high-poly models
4. **Web Workers:** Offload Monte Carlo simulation to worker threads
5. **Debouncing:** Debounce parameter controls (300ms)
6. **Pagination:** Paginate "View All Scenarios" if > 50

### Performance Targets
- Landing page load: < 2s
- Scenario switch: < 3s
- Monte Carlo simulation: < 5s (sample size 10,000)
- 3D rendering: < 1s
- Responsive resize: < 100ms

---

## Dependencies

### Internal Skills
- `bayesian-evt` — Bayesian EVT computation (required)
- `3d-animation` — Three.js + Canvas 2D rendering (required)

### External Libraries
- **Three.js** — 3D rendering (CDN: `https://unpkg.com/three@0.160.0/build/three.min.js`)
- **Pyodide** — In-browser Python (CDN: `https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js`)
- **Tailwind CSS** — Styling (CDN: `https://cdn.tailwindcss.com`)
- **Chart.js** — Indicator charts (optional)
- **D3.js** — Advanced visualizations (optional)

### Python Dependencies (Pyodide)
```python
# requirements.txt (for Pyodide)
numpy
pandas
pymc
arviz
scipy
matplotlib
```

---

## Future Enhancements

### Phase 2 (Post-MVP)
- **Compare Scenarios:** Side-by-side comparison of two scenarios
- **Scenario Export:** Export risk report (PDF, HTML)
- **Scenario Sharing:** Share scenario URL with parameter presets
- **User Accounts:** Save favorite scenarios, custom presets
- **Collaboration:** Share scenarios with team members

### Phase 3 (Advanced)
- **Custom Scenario Builder:** Create custom scenarios from scratch
- **Machine Learning:** Predict risk based on new inputs
- **Real-time Data:** Integrate with live sensor data
- **AR/VR:** Augmented reality visualization
- **Mobile App:** Native iOS/Android app

---

## References

### Standards
- **UL 4600** — Safety of Cyber-Physical Systems
- **ISO 21448 (SOTIF)** — Safety of the Intended Functionality
- **ISO 26262** — Functional Safety
- **ISO 21002** — Safety of Automated Road Transport Systems
- **NHTSA Publications** — FARS/CISS data access

### Research Papers
- **Coles, S. (2001).** An Introduction to Statistical Modeling of Extreme Values
- **Society of Automotive Engineers (SAE).** J3016 Taxonomy of Roadway User Behaviors

### Portfolio Integration
- **Featured Scenarios:** 2 per conflict type (16 total)
- **"View All Scenarios":** 62+ scenarios
- **Risk Metrics:** 42 surrogate safety indicators
- **Jurisdictions:** USA, Canada, England

---

## Troubleshooting

### Issue: Three.js fails to load
**Solution:** Check CDN connectivity, fallback to Canvas 2D mode

### Issue: Monte Carlo simulation times out
**Solution:** Reduce sample size, check browser console for errors

### Issue: Indicators not displaying
**Solution:** Verify bayesian-evt module is loaded, check kinematics data

### Issue: Slow rendering on mobile
**Solution:** Enable low-poly models, reduce sample size, switch to Canvas 2D

### Issue: Memory leaks in 3D rendering
**Solution:** Call `visualization.destroy()` before switching scenarios, clean up event listeners

---

## Related Skills

- `bayesian-evt` — Bayesian EVT computation engine
- `3d-animation` — Three.js + Canvas 2D rendering
- `portfolio-deploy` — Docker + deployment
- `validation` — Statistical validation against real crash data
- `indicator-computation` — 42 surrogate safety indicator formulas

---

**Status:** ✅ Ready to implement
**Next Steps:**
1. Create portfolio directory structure
2. Implement landing page (`index.html`)
3. Build UI logic (`app.js`)
4. Integrate bayesian-evt and 3d-animation modules
5. Test end-to-end workflow

---

*Last Updated:* 2026-06-02
*Author:* AV_Safety Team
*Skill Version:* 1.0.0