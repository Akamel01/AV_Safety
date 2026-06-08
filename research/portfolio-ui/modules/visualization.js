/**
 * visualization.js — 3D + 2D Visualization Module
 *
 * Renders collision scenarios in Three.js (3D) with Canvas 2D fallback.
 * Handles scene creation, vehicle models, road geometry, lighting, camera modes,
 * and HUD overlay for safety metrics.
 */

/**
 * Three.js 3D rendering module.
 * Delegates to the 3d-animation skill for full rendering.
 */
const visualization = {
  /**
   * Render a collision scenario.
   * @param {Object} params
   * @param {string} params.conflictType - Conflict type (e.g., 'rear-end')
   * @param {Object} params.parameters - Kinematic parameters
   * @param {'3d'|'2d'} params.mode - Rendering mode
   * @param {string} params.containerId - DOM container ID
   * @returns {Promise<{canvas: Element, hud: HTMLElement, collisionFX: Object|null}>}
   */
  async render(params) {
    const { conflictType, parameters, mode = '3d', containerId = 'canvas-container' } = params;

    if (mode === '3d') {
      return await this._render3D(params);
    }
    return await this._render2D(params);
  },

  /**
   * 3D rendering via Three.js — delegates to 3d-animation skill.
   */
  async _render3D(params) {
    // Check if Three.js is available
    if (typeof THREE === 'undefined') {
      console.warn('Three.js not loaded, falling back to 2D');
      return this._render2D({ ...params, mode: '2d' });
    }

    const container = document.getElementById(params.containerId);
    if (!container) {
      throw new Error(`Container #${params.containerId} not found`);
    }

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    scene.add(directionalLight);

    // Road geometry
    const roadGeom = new THREE.PlaneGeometry(200, 200);
    const roadMat = new THREE.MeshPhongMaterial({ color: 0x333333 });
    const road = new THREE.Mesh(roadGeom, roadMat);
    road.rotation.x = -Math.PI / 2;
    road.position.y = -0.1;
    scene.add(road);

    // Lane markings
    const lineGeom = new THREE.PlaneGeometry(200, 0.2);
    const lineMat = new THREE.MeshPhongMaterial({ color: 0xffffff });
    const centerLine = new THREE.Mesh(lineGeom, lineMat);
    centerLine.rotation.x = -Math.PI / 2;
    centerLine.position.y = 0;
    scene.add(centerLine);

    // Vehicle models (simplified boxes for now)
    const vehA = this._createVehicle(params, 0xff4444, 'Vehicle A');
    const vehB = this._createVehicle(params, 0x4488ff, 'Vehicle B');
    scene.add(vehA, vehB);

    camera.position.set(0, 30, 50);
    camera.lookAt(0, 0, 0);

    // HUD overlay
    const hud = this._createHUD(container);

    return {
      canvas: renderer.domElement,
      hud,
      collisionFX: null,
      scene,
      camera,
      renderer,
      destroy: () => this._cleanup(renderer, container),
    };
  },

  /**
   * 2D Canvas fallback rendering.
   */
  async _render2D(params) {
    const container = document.getElementById(params.containerId);
    if (!container) {
      throw new Error(`Container #${params.containerId} not found`);
    }

    const canvas = document.createElement('canvas');
    canvas.width = container.clientWidth || 800;
    canvas.height = container.clientHeight || 400;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    container.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    // Draw road
    ctx.fillStyle = '#333';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw vehicles
    const v1 = params.parameters?.v1 || 30;
    const v2 = params.parameters?.v2 || 27;
    const headway = params.parameters?.headway || 30;

    const xA = 100 + v1 * 2;
    const xB = xA + headway;

    this._drawCar(ctx, xA, canvas.height / 2 - 10, 0xff4444, 'A');
    this._drawCar(ctx, xB, canvas.height / 2 - 10, 0x4488ff, 'B');

    // Lane markings
    ctx.strokeStyle = '#fff';
    ctx.setLineDash([20, 15]);
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // HUD
    const hud = this._createHUD(canvas.parentElement);

    return { canvas, hud, collisionFX: null, scene: null, camera: null, renderer: null, destroy: () => {} };
  },

  /**
   * Create vehicle 3D model.
   */
  _createVehicle(params, color, label) {
    const group = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(4, 1.5, 2),
      new THREE.MeshPhongMaterial({ color })
    );
    body.position.y = 0.75;
    group.add(body);
    return group;
  },

  /**
   * Draw a car on 2D canvas.
   */
  _drawCar(ctx, x, y, color, label) {
    ctx.fillStyle = color;
    ctx.fillRect(x - 20, y - 5, 40, 25);
    ctx.fillStyle = '#fff';
    ctx.font = '12px sans-serif';
    ctx.fillText(label, x - 5, y + 15);
  },

  /**
   * Create HUD overlay div.
   */
  _createHUD(container) {
    const hud = document.createElement('div');
    hud.className = 'hud-overlay';
    hud.style.cssText = `
      position: absolute; top: 10px; left: 10px;
      background: rgba(0,0,0,0.7); color: #fff;
      padding: 10px; border-radius: 8px; font-family: monospace;
      font-size: 12px; pointer-events: none; z-index: 10;
    `;
    hud.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 5px;">HUD</div>
      <div id="hud-ttc">TTC: --</div>
      <div id="hud-drac">DRAC: --</div>
      <div id="hud-ssd">SSD: --</div>
      <div id="hud-psdr">PSdR: --</div>
    `;
    if (container) container.style.position = 'relative';
    if (container) container.appendChild(hud);
    return hud;
  },

  /**
   * Cleanup Three.js resources.
   */
  _cleanup(renderer, container) {
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    }
    if (container && container.querySelector('.hud-overlay')) {
      container.querySelector('.hud-overlay').remove();
    }
  },

  /**
   * Destroy visualization and clean up.
   */
  destroy(result) {
    if (result && result.destroy) result.destroy();
  },

  /**
   * Update HUD with current metrics.
   */
  updateHUD(hud, metrics) {
    if (!hud) return;
    const updates = {
      'hud-ttc': `TTC: ${metrics.ttc?.toFixed(2) || '--'}s`,
      'hud-drac': `DRAC: ${metrics.drac?.toFixed(2) || '--'} m/s²`,
      'hud-ssd': `SSD: ${metrics.ssd?.toFixed(1) || '--'}m`,
      'hud-psdr': `PSdR: ${metrics.psdr?.toFixed(2) || '--'}%`,
    };
    for (const [id, text] of Object.entries(updates)) {
      const el = hud.querySelector(`#${id}`) || hud.querySelector(`[id="${id}"]`);
      if (el) el.textContent = text;
    }
  },
};

export default visualization;
