/**
 * app.js — Main Application Entry Point for RE-CA-001 Demo
 *
 * Wires together:
 *  - kinematics.js   (RearEndKinematics)
 *  - monte-carlo.js  (MonteCarloEngine)
 *  - bayesian-evt.js (BayesianEVT)
 *  - risk-scoring.js (RiskScorer)
 *  - visualization.js (VisualizationEngine)
 *
 * Usage: Open index.html in a browser.
 * All computation runs client-side. No server required.
 */

// ============================================================
// Global State
// ============================================================
const AppState = {
  scenario: null,
  kinematics: null,
  mcEngine: null,
  bayesianEVT: null,
  riskScorer: null,
  vizEngine: null,
  gpdParams: null,
  threshold: null,
  postPred: null,
  simRunning: false,
  mcRunning: false,
  evtRunning: false,
  animRunning: false,
  animFrameId: null,
  time: 0,
  frameIdx: 0,
  mode: '3d',
};

// ============================================================
// Initialization
// ============================================================
async function init() {
  const statusEl = document.getElementById('status-bar');

  try {
    // 1. Load scenario data
    statusEl.textContent = 'Loading scenario data...';
    const resp = await fetch('data/scenario-RE-CA-001.json');
    AppState.scenario = await resp.json();
    console.log('[app] Scenario loaded:', AppState.scenario.scenario.id);

    // 2. Initialize visualization
    const canvasContainer = document.getElementById('canvas-container');
    if (canvasContainer) {
      AppState.vizEngine = new VisualizationEngine(canvasContainer, '3d');
      await AppState.vizEngine.init3D();
      console.log('[app] 3D engine initialized, mode:', AppState.vizEngine.mode);
    }

    // 3. Initialize Bayesian EVT
    AppState.bayesianEVT = new BayesianEVT();
    await AppState.bayesianEVT.init();
    console.log('[app] EVT engine ready');

    // 4. Initialize risk scorer
    AppState.riskScorer = new RiskScorer();

    // 5. Wire up UI controls
    wireUpControls();

    // 6. Run nominal simulation
    await runNominalSimulation();

    statusEl.textContent = 'Ready — adjust parameters and run Monte Carlo.';
    console.log('[app] Application initialized.');
  } catch (e) {
    console.error('[app] Initialization failed:', e);
    if (statusEl) statusEl.textContent = `Error: ${e.message}`;
  }
}

// ============================================================
// Parameter Management
// ============================================================
function getParameterValues() {
  return {
    v_a0: parseFloat(document.getElementById('p-v-a0').value),
    v_b0: parseFloat(document.getElementById('p-v-b0').value),
    headway: parseFloat(document.getElementById('p-headway').value),
    reaction_time: parseFloat(document.getElementById('p-reaction').value),
    a_lead: parseFloat(document.getElementById('p-a-lead').value),
    a_follow_max: parseFloat(document.getElementById('p-a-follow').value),
    brake_lag: parseFloat(document.getElementById('p-brake-lag')?.value || 0.15),
    sim_duration: 15.0,
  };
}

function updateParameterDisplays() {
  const sliderIdMap = [
    ['p-v-a0', 'v-v-a0', v => `${v.toFixed(1)} m/s`],
    ['p-a-lead', 'v-a-lead', v => `${v.toFixed(2)} m/s²`],
    ['p-t-brake', 'v-t-brake', v => `${v.toFixed(1)} s`],
    ['p-v-b0', 'v-v-b0', v => `${v.toFixed(1)} m/s`],
    ['p-headway', 'v-headway', v => `${v.toFixed(1)} m`],
    ['p-reaction', 'v-reaction', v => `${v.toFixed(1)} s`],
    ['p-a-follow', 'v-a-follow', v => `${v.toFixed(2)} m/s²`],
    ['p-brake-lag', 'v-brake-lag', v => `${v.toFixed(2)} s`],
  ];

  for (const [inputId, displayId, fmt] of sliderIdMap) {
    const input = document.getElementById(inputId);
    const display = document.getElementById(displayId);
    if (input && display) {
      display.textContent = fmt(parseFloat(input.value));
    }
  }
}

// ============================================================
// UI Wiring
// ============================================================
function wireUpControls() {
  // Parameter sliders — update displays + debounced nominal run
  const sliders = document.querySelectorAll('.controller-input');
  let nominalDebounceTimer = null;
  for (const slider of sliders) {
    slider.addEventListener('input', () => {
      updateParameterDisplays();
      clearTimeout(nominalDebounceTimer);
      nominalDebounceTimer = setTimeout(runNominalSimulation, 250);
    });
  }

  // Monte Carlo button
  const btnMC = document.getElementById('btn-run-mc');
  if (btnMC) {
    btnMC.addEventListener('click', runMonteCarlo);
  }

  // Bayesian EVT button
  const btnEVT = document.getElementById('btn-evt');
  if (btnEVT) {
    btnEVT.addEventListener('click', runBayesianEVT);
  }

  // 3D/2D toggle
  const btnMode = document.getElementById('btn-mode');
  if (btnMode) {
    btnMode.addEventListener('click', () => {
      if (AppState.vizEngine) {
        AppState.vizEngine.toggleMode();
        btnMode.textContent = AppState.vizEngine.mode === '3d' ? '🌐 3D' : '📐 2D';
      }
    });
  }

  // Download CSV
  const btnCSV = document.getElementById('btn-download');
  if (btnCSV) {
    btnCSV.addEventListener('click', () => {
      if (AppState.mcResults) {
        downloadCSV(AppState.mcResults);
      } else {
        alert('Run Monte Carlo first to export results.');
      }
    });
  }

  // Share
  const btnShare = document.getElementById('btn-share');
  if (btnShare) {
    btnShare.addEventListener('click', shareScenario);
  }

  // Initial display update
  updateParameterDisplays();

  // Restore from URL params if present
  restoreFromURL();
}

// ============================================================
// Nominal Simulation
// ============================================================
async function runNominalSimulation() {
  if (AppState.simRunning) return;
  AppState.simRunning = true;

  try {
    const params = getParameterValues();
    AppState.kinematics = new RearEndKinematics(params);
    const result = AppState.kinematics.run();
    AppState.nominalResult = result;

    // Update nominal indicators panel
    const indicators = result.indicators;
    if (indicators) {
      setText('val-ttc-nominal', indicators.ttc ? `${indicators.ttc.toFixed(2)}s` : 'N/A');
      setText('val-gap-nominal', indicators.min_spatial_gap ? `${indicators.min_spatial_gap.toFixed(1)}m` : 'N/A');
      setText('val-dv-nominal', indicators.delta_v ? `${(indicators.delta_v * 3.6).toFixed(1)} km/h` : 'None');
      setText('val-drac-nominal', indicators.drac ? `${indicators.drac.toFixed(2)} m/s²` : 'N/A');
      setText('val-rla-nominal', indicators.rla ? `${indicators.rla.toFixed(2)} m/s²` : 'N/A');
    }

    // Status badge
    const statusEl = document.getElementById('nominal-status');
    if (statusEl) {
      if (result.collision) {
        statusEl.textContent = '⚠ COLLISION';
        statusEl.className = 'status-badge critical';
      } else {
        statusEl.textContent = '✓ SAFE';
        statusEl.className = 'status-badge safe';
      }
    }

    // Animate visualization
    if (AppState.vizEngine) {
      animateNominal(result.trajectory);
    }

    // Update status bar
    const statusEl = document.getElementById('status-bar');
    if (statusEl) statusEl.textContent = 'Nominal simulation complete.';

  } catch (e) {
    console.error('[app] Nominal simulation failed:', e);
  } finally {
    AppState.simRunning = false;
  }
}

function animateNominal(trajectory) {
  if (!AppState.vizEngine) return;
  AppState.animRunning = true;
  AppState.time = 0;
  AppState.frameIdx = 0;

  const n = trajectory.t.length;
  if (n === 0) { AppState.animRunning = false; return; }

  function frame() {
    if (!AppState.animRunning) return;

    AppState.time += 0.02; // ~50 FPS
    AppState.frameIdx = Math.min(n - 1,
      Math.floor(AppState.time / 15.0 * n)
    );

    const t = trajectory.t[AppState.frameIdx];
    const x_a = trajectory.x_a[AppState.frameIdx];
    const x_b = trajectory.x_b[AppState.frameIdx];
    const v_a = trajectory.v_a[AppState.frameIdx];
    const v_b = trajectory.v_b[AppState.frameIdx];
    const gap = trajectory.gap[AppState.frameIdx];
    const ttc = trajectory.ttc[AppState.frameIdx];
    const isCol = trajectory.collision[AppState.frameIdx];

    // Update HUD in visualization
    AppState.vizEngine.updateHUD({
      time: t,
      gap: gap,
      v_a: v_a,
      v_b: v_b,
      ttc: ttc,
      collision: isCol,
    });

    // Animate frame
    AppState.vizEngine.animateFrame({
      x: x_a - x_b,
      v_a, v_b,
      collision: isCol,
      time: t,
    });

    if (AppState.time < 15.0) {
      AppState.animFrameId = requestAnimationFrame(frame);
    } else {
      AppState.animRunning = false;
    }
  }

  frame();
}

// ============================================================
// Monte Carlo
// ============================================================
async function runMonteCarlo() {
  if (AppState.mcRunning) return;
  AppState.mcRunning = true;

  const btnMC = document.getElementById('btn-run-mc');
  const statusEl = document.getElementById('status-bar');
  const progressFill = document.getElementById('mc-progress-fill');

  try {
    const params = getParameterValues();
    AppState.kinematics = new RearEndKinematics(params);

    // Build scenario spec for MC engine (needs parameter distributions)
    const scenarioSpec = buildMCSpec(params);
    AppState.mcEngine = new MonteCarloEngine(scenarioSpec, RearEndKinematics);

    // Update UI
    btnMC.disabled = true;
    btnMC.textContent = '⏳ Running...';
    if (statusEl) statusEl.textContent = 'Running Monte Carlo...';
    if (progressFill) progressFill.style.width = '0%';

    // Run MC
    const nSamples = parseInt(document.getElementById('n-mc-samples')?.value) || 10000;
    const mcResults = await AppState.mcEngine.run(nSamples, (progress) => {
      if (progressFill) progressFill.style.width = `${progress * 100}%`;
    });

    AppState.mcResults = mcResults;

    // Update dashboard
    updateMCResults(mcResults);

    // Auto-run EVT if enough collisions
    if (mcResults.collisions >= 10) {
      if (statusEl) statusEl.textContent = 'Monte Carlo complete — running EVT...';
      await runBayesianEVT(mcResults);
    }

    // Compute risk score
    computeRiskScore(mcResults);

    if (statusEl) statusEl.textContent = 'Monte Carlo simulation complete.';

  } catch (e) {
    console.error('[app] Monte Carlo failed:', e);
    if (statusEl) statusEl.textContent = `Error: ${e.message}`;
  } finally {
    AppState.mcRunning = false;
    btnMC.disabled = false;
    btnMC.textContent = '▶ Monte Carlo';
    if (progressFill) progressFill.style.width = '0%';
  }
}

function buildMCSpec(params) {
  // Build parameter distribution spec from nominal parameters
  return {
    seed: 42,
    parameters: {
      v_a0: { mu: params.v_a0, sigma: 1.0, lo: 15, hi: 35 },
      v_b0: { mu: params.v_b0, sigma: 1.0, lo: 15, hi: 35 },
      headway: { mu: params.headway, sigma: 5.0, lo: 5, hi: 60 },
      reaction_time: { mu: params.reaction_time, sigma: 0.3, lo: 0.5, hi: 4.0 },
      a_lead: { mu: params.a_lead, sigma: 1.0, lo: -8, hi: -2 },
      a_follow_max: { mu: params.a_follow_max, sigma: 1.0, lo: -10, hi: -3 },
      brake_lag: { mu: 0.15, sigma: 0.02, lo: 0.05, hi: 0.3 },
      vehicle_length: { mu: 4.3, sigma: 0.1, lo: 3.5, hi: 5.0 },
      lane_width: { mu: 3.7, sigma: 0.1, lo: 3.0, hi: 4.5 },
      sim_duration: { mu: 15.0, sigma: 0, lo: 15, hi: 15 },
      t_brake_event: { mu: 3.0, sigma: 0.0, lo: 3, hi: 3 },
    },
  };
}

function updateMCResults(mcResults) {
  const stats = mcResults.collapseResults();
  const n = mcResults.n;

  // Collision rate
  const ratePct = ((mcResults.collisions / n) * 100).toFixed(1);
  setText('val-mc-rate', `${ratePct}%`);
  setText('val-mc-n', `N = ${n}`);

  // TTC distribution
  if (stats.ttc) {
    setText('val-mc-ttc-dist', `${stats.ttc.median.toFixed(2)}s`);
    setText('val-mc-ttc-p5', `P5 = ${stats.ttc.p5.toFixed(2)}s`);
  }

  // Delta-V distribution
  if (stats.delta_v) {
    setText('val-mc-dv-dist', `${stats.delta_v.p50.toFixed(1)} m/s`);
    setText('val-mc-dv-p95', `P95 = ${stats.delta_v.p95.toFixed(1)} m/s`);
  }

  // Severity distribution
  const nSev = mcResults.indicatorHistory.expected_severity?.length || n;
  const sevArr = mcResults.indicatorHistory.expected_severity || [];
  const pdo = Math.round(sevArr.filter(s => s < 0.25).length / nSev * 100) || 0;
  const minor = Math.round(sevArr.filter(s => s >= 0.25 && s < 0.5).length / nSev * 100) || 0;
  const mod = Math.round(sevArr.filter(s => s >= 0.5 && s < 0.75).length / nSev * 100) || 0;
  const sev = Math.round(sevArr.filter(s => s >= 0.75).length / nSev * 100) || 0;

  setText('val-sev-pdo', `${pdo}%`);
  setText('val-sev-minor', `${minor}%`);
  setText('val-sev-mais3', `${mod}%`);
  setText('val-sev-fatal', `${sev}%`);

  // Jurisdiction comparison
  const scenarioRate = mcResults.collisions / n;
  const per100M = (scenarioRate * 1e6 * 3.6).toFixed(3); // rough scaling
  setText('val-vs-baseline', `${scenarioRate.toFixed(3)} sim / ${per100M}/100M`);
}

// ============================================================
// Bayesian EVT
// ============================================================
async function runBayesianEVT(mcResultsInput) {
  if (AppState.evtRunning) return;
  AppState.evtRunning = true;

  const btnEVT = document.getElementById('btn-evt');
  const statusEl = document.getElementById('status-bar');

  try {
    const mc = mcResultsInput || AppState.mcResults;
    if (!mc) {
      alert('Run Monte Carlo first.');
      return;
    }

    // Extract TTC excess values (TTC < 2s threshold)
    const ttcHistory = mc.indicatorHistory.ttc || [];
    const threshold = 2.0;

    const excesses = ttcHistory
      .filter(t => t !== Infinity && t < threshold)
      .map(t => threshold - t)
      .sort((a, b) => b - a); // descending

    if (excesses.length < 10) {
      console.warn(`[EVT] Only ${excesses.length} exceedances (need 10+)`);
      if (statusEl) statusEl.textContent = 'Insufficient data for EVT.';
      return;
    }

    // Step 1: MRL threshold selection
    const mrlResult = AppState.bayesianEVT.selectThresholdMRL(excesses);
    AppState.threshold = mrlResult.u;

    // Step 2: GPD fitting
    const gpd = AppState.bayesianEVT.fitGPD(excesses, mrlResult.u);
    AppState.gpdParams = gpd;

    // Step 3: Profile likelihood
    const profile = AppState.bayesianEVT.fitGPDProfileLikelihood(excesses, mrlResult.u);
    AppState.profileLikelihood = profile;

    // Step 4: Posterior predictive check
    const ppd = AppState.bayesianEVT.posteriorPredictiveCheck(gpd, excesses);
    AppState.postPred = ppd;

    console.log('[EVT] Fit complete:', {
      threshold: mrlResult.u,
      xi: gpd.xi,
      sigma: gpd.sigma,
      n_excess: excesses.length,
      ks_stat: ppd.ks_stat,
    });

    if (statusEl) statusEl.textContent = `EVT fitted: ξ=${gpd.xi.estimate.toFixed(3)}, σ=${gpd.sigma.estimate.toFixed(3)}, n=${excesses.length}`;

  } catch (e) {
    console.error('[EVT] Failed:', e);
    if (statusEl) statusEl.textContent = `EVT error: ${e.message}`;
  } finally {
    AppState.evtRunning = false;
    btnEVT.disabled = false;
    btnEVT.textContent = '📊 Bayesian EVT';
  }
}

// ============================================================
// Risk Scoring
// ============================================================
function computeRiskScore(mcResults) {
  const stats = mcResults.collapseResults();
  const collisionRate = mcResults.collisions / mcResults.n;

  // Compute components
  const evt = AppState.gpdParams || { xi: { estimate: 0.3 }, sigma: { estimate: 1.5 } };
  const n = mcResults.n;

  const score = AppState.riskScorer.compute({
    collisionRate: collisionRate,
    n: n,
    collapsedResults: stats,
  }, {
    gpd_params: evt,
    severity: { expected_severity: {} },
    collision_rate: { estimate: collisionRate },
  }, AppState.kinematics ? {
    ttc: stats.ttc?.median || 5,
    min_spatial_gap: stats.min_gap?.median || 20,
    delta_v: stats.delta_v?.p50 || 0,
  } : {}, { headway: getParameterValues().headway });

  // Update UI
  setText('risk-score-value', score.composite.score.toFixed(1));
  setText('risk-score-class', score.composite.classification);

  const comp = score.components;
  setText('comp-collision', comp.collision_rate.score.toFixed(1));
  setText('comp-severity', comp.severity.score.toFixed(1));
  setText('comp-uncertainty', comp.uncertainty.score.toFixed(1));
  setText('comp-compliance', comp.threshold_compliance.score.toFixed(1));
}

// ============================================================
// CSV Export
// ============================================================
function downloadCSV(mcResults) {
  const header = 'sim,collision,ttc,delta_v,min_gap,drac,rla,cpi,severity,headway,reaction_time,v_a0,v_b0';
  const rows = [];

  for (let i = 0; i < mcResults.n; i++) {
    rows.push([
      i,
      mcResults.collisionArr[i],
      (mcResults.ttcArr[i] || 0).toFixed(3),
      (mcResults.deltaVArr[i] || 0).toFixed(3),
      (mcResults.gapMinArr[i] || 0).toFixed(3),
      (mcResults.dracArr[i] || 0).toFixed(3),
      (mcResults.rlaArr[i] || 0).toFixed(3),
      (mcResults.cpiArr[i] || 0).toFixed(3),
      (mcResults.sevArr[i] || 0).toFixed(3),
      (mcResults.paramSamples?.[i]?.headway || 0).toFixed(1),
      (mcResults.paramSamples?.[i]?.reaction_time || 0).toFixed(2),
      (mcResults.paramSamples?.[i]?.v_a0 || 0).toFixed(1),
      (mcResults.paramSamples?.[i]?.v_b0 || 0).toFixed(1),
    ].join(','));
  }

  const csv = header + '\n' + rows.join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `${AppState.scenario.scenario.id || 'RE-CA-001'}-mc-${mcResults.n}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// ============================================================
// Sharing
// ============================================================
function shareScenario() {
  const params = getParameterValues();
  const url = new URL(window.location.href);
  url.searchParams.set('v_a0', params.v_a0);
  url.searchParams.set('v_b0', params.v_b0);
  url.searchParams.set('headway', params.headway);
  url.searchParams.set('reaction', params.reaction_time);
  url.searchParams.set('a_lead', params.a_lead);
  url.searchParams.set('a_follow', params.a_follow_max);

  window.history.pushState({}, '', url);
  navigator.clipboard.writeText(url.toString());

  const btnShare = document.getElementById('btn-share');
  if (btnShare) {
    const orig = btnShare.textContent;
    btnShare.textContent = '✓ Copied!';
    setTimeout(() => { btnShare.textContent = orig; }, 2000);
  }
}

// ============================================================
// URL Parameter Restoration
// ============================================================
function restoreFromURL() {
  const params = new URLSearchParams(window.location.search);
  const idMap = [
    ['v_a0', 'p-v-a0'],
    ['v_b0', 'p-v-b0'],
    ['headway', 'p-headway'],
    ['reaction', 'p-reaction'],
    ['a_lead', 'p-a-lead'],
    ['a_follow', 'p-a-follow'],
  ];

  for (const [key, id] of idMap) {
    const val = params.get(key);
    if (val) {
      const el = document.getElementById(id);
      if (el) el.value = val;
    }
  }
}

// ============================================================
// Utility
// ============================================================
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// ============================================================
// Start on DOM ready
// ============================================================
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
