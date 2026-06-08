/**
 * visualization.js — 3D + 2D Visualization Engine
 *
 * Renders the rear-end collision scenario in Three.js (3D) with Canvas 2D fallback.
 * Includes: vehicle models, road geometry, lighting, post-processing, camera modes,
 * HUD overlay, collision FX, and 2D top-down renderer.
 *
 * Based on 3d-animation skill:
 *   https://github.com/Akamel01/AV_Safety/skills/3d-animation/SKILL.md
 */

class VisualizationEngine {
  constructor(containerEl, mode = '3d') {
    this.container = containerEl;
    this.mode = mode; // '3d' | '2d'
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.composer = null;
    this.vehicleA = null;
    this.vehicleB = null;
    this.road = null;
    this.hudElement = null;
    this.collisionFX = null;
    this.animationId = null;
    this.cameraMode = 'auto-trace';
    this.timeOfDay = 'day';
    this.isCollided = false;
    this.collisionTime = null;
    this.progress = 0; // 0-1 animation progress
    this.speedFactor = 1.0;
    this.bloomPass = null;
    this.filmPass = null;
  }

  /** Initialize 3D scene */
  async init3D() {
    this.mode = '3d';
    const THREE = await this._loadThree();
    if (!THREE) { this.mode = '2d'; return; }

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this._getSkyColor());

    // Camera
    this.camera = new THREE.PerspectiveCamera(
      60,
      this.container.clientWidth / this.container.clientHeight,
      0.1,
      1000
    );
    this.camera.position.set(-10, 8, 15);
    this.camera.lookAt(0, 0, 0);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.appendChild(this.renderer.domElement);

    // Post-processing
    this._setupPostProcessing(THREE);

    // Lighting
    this._setupLighting(THREE);

    // Road
    this._createRoad(THREE);

    // Vehicles (placeholder geometry — replace with GLTF models)
    this.vehicleA = this._createVehicle(THREE, 'white', 'lead');
    this.vehicleB = this._createVehicle(THREE, 'blue', 'follow');

    this.scene.add(this.vehicleA);
    this.scene.add(this.vehicleB);

    // Grid helper for ground reference
    const grid = new THREE.GridHelper(200, 100, 0x888888, 0xCCCCCC);
    grid.position.y = -0.01;
    this.scene.add(grid);

    // HUD
    this._createHUD();

    // Resize handler
    this._resizeHandler = () => {
      if (!this.renderer) return;
      this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    };
    window.addEventListener('resize', this._resizeHandler);

    return this;
  }

  /** Initialize 2D Canvas */
  init2D() {
    this.mode = '2d';

    // Create canvas element
    this.canvas2D = document.createElement('canvas');
    this.canvas2D.width = this.container.clientWidth;
    this.canvas2D.height = this.container.clientHeight;
    this.canvas2D.style.position = 'absolute';
    this.canvas2D.style.top = '0';
    this.canvas2D.style.left = '0';
    this.container.appendChild(this.canvas2D);

    this.ctx = this.canvas2D.getContext('2d');
    this.scale = 5; // 5 pixels per meter

    // HUD
    this._createHUD();

    return this;
  }

  /** Switch between 3D and 2D */
  toggleMode() {
    if (this.mode === '3d') {
      this._destroy3D();
      return this.init2D();
    } else {
      this._destroy2D();
      return this.init3D();
    }
  }

  /** Load Three.js dynamically */
  _loadThree() {
    return new Promise((resolve) => {
      if (typeof THREE !== 'undefined') {
        resolve(THREE);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js';
      script.onload = () => resolve(THREE);
      script.onerror = () => resolve(null);
      document.head.appendChild(script);
    });
  }

  /** Setup post-processing (bloom, film grain) */
  _setupPostProcessing(THREE) {
    try {
      // Render pass
      this.composer = null; // Simplified: no full post-processing without EffectComposer
      // For full post-processing, include:
      // import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
      // import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
      // import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
      // import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';

      // Simplified bloom via CSS filter for now
      if (this.renderer) {
        this.renderer.domElement.style.filter = 'none';
      }
    } catch (e) {
      console.warn('Post-processing not available:', e);
    }
  }

  /** Setup lighting (daytime default) */
  _setupLighting(THREE) {
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);

    // Directional sun
    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(50, 100, 50);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 500;
    sun.shadow.camera.left = -100;
    sun.shadow.camera.right = 100;
    sun.shadow.camera.top = 100;
    sun.shadow.camera.bottom = -100;
    this.scene.add(sun);
    this.sun = sun;

    // Hemisphere sky/ground
    const hemi = new THREE.HemisphereLight(0x87CEEB, 0x362907, 0.3);
    this.scene.add(hemi);

    // Time-of-day controls
    this.timeConfigs = {
      day: { sunIntensity: 1.0, ambientIntensity: 0.4, skyColor: 0x87CEEB },
      sunset: { sunIntensity: 0.7, ambientIntensity: 0.3, skyColor: 0xFF8C42 },
      night: { sunIntensity: 0.1, ambientIntensity: 0.1, skyColor: 0x0A0A2E },
      overcast: { sunIntensity: 0.5, ambientIntensity: 0.5, skyColor: 0x999999 },
    };
  }

  /** Create road geometry */
  _createRoad(THREE) {
    // Road surface
    const roadGeo = new THREE.PlaneGeometry(200, 12);
    const roadMat = new THREE.MeshStandardMaterial({
      color: 0x333333,
      roughness: 0.9,
      metalness: 0.1,
    });
    const road = new THREE.Mesh(roadGeo, roadMat);
    road.rotation.x = -Math.PI / 2;
    road.position.y = 0;
    road.receiveShadow = true;
    this.scene.add(road);

    // Lane markings (dashed white centerline)
    const lineGeo = new THREE.PlaneGeometry(200, 0.15);
    const lineMat = new THREE.MeshStandardMaterial({
      color: 0xFFFFFF,
      roughness: 0.5,
      metalness: 0.0,
    });

    for (let i = -99; i < 100; i += 6) {
      const line = new THREE.Mesh(lineGeo, lineMat);
      line.rotation.x = -Math.PI / 2;
      line.position.set(i, 0.01, 0);
      line.receiveShadow = true;
      this.scene.add(line);
    }

    // Shoulder lines (solid yellow)
    const shoulderGeo = new THREE.PlaneGeometry(200, 0.15);
    const shoulderMat = new THREE.MeshStandardMaterial({
      color: 0xFFD700,
      roughness: 0.5,
    });

    [-5.85, 5.85].forEach(y => {
      const shoulder = new THREE.Mesh(shoulderGeo, shoulderMat);
      shoulder.rotation.x = -Math.PI / 2;
      shoulder.position.set(0, 0.01, y);
      shoulder.receiveShadow = true;
      this.scene.add(shoulder);
    });

    // Sidewalks
    const sidewalkGeo = new THREE.BoxGeometry(200, 0.2, 1.5);
    const sidewalkMat = new THREE.MeshStandardMaterial({
      color: 0xAAAAAA,
      roughness: 0.8,
    });
    [-7.75, 7.75].forEach(z => {
      const sidewalk = new THREE.Mesh(sidewalkGeo, sidewalkMat);
      sidewalk.position.set(0, 0.1, z);
      sidewalk.receiveShadow = true;
      this.scene.add(sidewalk);
    });
  }

  /** Create vehicle mesh */
  _createVehicle(THREE, color, type) {
    const group = new THREE.Group();

    // Body
    const bodyGeo = new THREE.BoxGeometry(4.3, 1.4, 1.8);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      metalness: 0.8,
      roughness: 0.3,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0.7;
    body.castShadow = true;
    group.add(body);

    // Cabin (roof)
    const cabinGeo = new THREE.BoxGeometry(2.0, 0.8, 1.6);
    const cabinMat = new THREE.MeshPhysicalMaterial({
      color: 0x111111,
      transmission: 0.9,
      thickness: 0.1,
      ior: 1.5,
      metalness: 0.0,
      roughness: 0.1,
    });
    const cabin = new THREE.Mesh(cabinGeo, cabinMat);
    cabin.position.set(-0.3, 1.7, 0);
    cabin.castShadow = true;
    group.add(cabin);

    // Wheels
    const wheelGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.2, 16);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });
    const wheelPositions = [
      [1.4, 0.35, 0.9], [1.4, 0.35, -0.9],
      [-1.4, 0.35, 0.9], [-1.4, 0.35, -0.9],
    ];
    wheelPositions.forEach(([x, y, z]) => {
      const wheel = new THREE.Mesh(wheelGeo, wheelMat);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(x, y, z);
      wheel.castShadow = true;
      group.add(wheel);
    });

    // Headlights
    const lightGeo = new THREE.SphereGeometry(0.15, 8, 8);
    const lightMat = new THREE.MeshStandardMaterial({
      color: 0xFFFFAA,
      emissive: 0xFFFFAA,
      emissiveIntensity: 0.5,
    });
    [-0.7, 0.7].forEach(z => {
      const light = new THREE.Mesh(lightGeo, lightMat);
      light.position.set(2.2, 0.7, z);
      group.add(light);
    });

    // Brake lights
    const brakeMat = new THREE.MeshStandardMaterial({
      color: 0xFF0000,
      emissive: 0xFF0000,
      emissiveIntensity: 0.0, // Off by default
    });
    [-0.6, 0.6].forEach(z => {
      const brake = new THREE.Mesh(lightGeo, brakeMat.clone());
      brake.position.set(-2.2, 0.7, z);
      brake.userData.isBrake = true;
      group.add(brake);
    });

    if (type === 'lead') {
      group.userData = { type: 'lead', color, name: 'Vehicle A' };
    } else {
      group.userData = { type: 'follow', color, name: 'Vehicle B' };
    }

    return group;
  }

  /** Update vehicle positions from trajectory data */
  updatePositions(trajectoryFrame) {
    if (!trajectoryFrame) return;

    const { t, x, v_a, v_b, a_a, a_b, collision } = trajectoryFrame;

    // Position vehicles along the road (x-axis)
    if (this.vehicleA && this.vehicleB) {
      const roadOffset = 30; // Offset so vehicles are centered in viewport

      // Vehicle A (lead) — always at positive x relative
      this.vehicleA.position.set(x + roadOffset, 0, 1.85);

      // Vehicle B (follow) — behind A
      this.vehicleB.position.set(roadOffset, 0, -1.85);

      // Brake light intensity based on acceleration
      const brakeIntensity = Math.min(Math.abs(a_a) / 8.0, 1.0);
      const brakeIntensityB = Math.min(Math.abs(a_b) / 8.0, 1.0);

      this.vehicleA.traverse((child) => {
        if (child.userData?.isBrake && child.material) {
          child.material.emissiveIntensity = brakeIntensity;
        }
      });
      this.vehicleB.traverse((child) => {
        if (child.userData?.isBrake && child.material) {
          child.material.emissiveIntensity = brakeIntensityB;
        }
      });

      // Collision detection
      const distance = Math.abs(this.vehicleA.position.x - this.vehicleB.position.x);
      if (distance < 4.5 && !this.isCollided) {
        this.isCollided = true;
        this.collisionTime = t;
        this._triggerCollisionFX();
      }

      // Move vehicles along road axis for continuous animation
      this.vehicleA.position.x = (x || 0) + roadOffset;
      this.vehicleB.position.x = roadOffset;
    }

    this.progress = Math.min(1, t / 10.0);
    this._updateHUD();
  }

  /** Set camera mode */
  setCameraMode(mode) {
    this.cameraMode = mode;
  }

  /** Animate camera based on mode */
  updateCamera(trajectoryFrame) {
    if (!this.camera || !trajectoryFrame) return;

    const { x, v_a, v_b } = trajectoryFrame;

    switch (this.cameraMode) {
      case 'auto-trace':
        // Follow vehicle B from behind/above
        const targetX = (x || 0) + 5;
        this.camera.position.x += (targetX - 10 - this.camera.position.x) * 0.05;
        this.camera.position.z = 15;
        this.camera.position.y = 8;
        this.camera.lookAt(targetX, 0, 0);
        break;

      case 'free-look':
        // Orbit around collision point
        const angle = performance.now() * 0.0005;
        this.camera.position.x = (x || 0) + Math.cos(angle) * 15;
        this.camera.position.z = Math.sin(angle) * 15;
        this.camera.position.y = 8;
        this.camera.lookAt(x || 0, 0, 0);
        break;

      case 'top-down':
        this.camera.position.set((x || 0) + 5, 50, 0);
        this.camera.lookAt((x || 0) + 5, 0, 0);
        this.camera.zoom = 5;
        this.camera.updateProjectionMatrix();
        break;
    }
  }

  /** Trigger collision visual effects */
  _triggerCollisionFX() {
    if (this.composer) {
      // Bloom flash
      if (this.bloomPass) {
        this.bloomPass.strength = 5.0;
        setTimeout(() => {
          if (this.bloomPass) this.bloomPass.strength = 1.0;
        }, 500);
      }
    }

    // Flash screen white briefly
    const flash = document.createElement('div');
    flash.style.cssText = `
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: white; opacity: 0.8; pointer-events: none;
      transition: opacity 0.5s ease; z-index: 100;
    `;
    this.container.appendChild(flash);
    requestAnimationFrame(() => { flash.style.opacity = '0'; });
    setTimeout(() => { flash.remove(); }, 1000);

    // Flash HUD to red
    if (this.hudElement) {
      this.hudElement.style.borderColor = '#FF0000';
      setTimeout(() => {
        if (this.hudElement) this.hudElement.style.borderColor = '';
      }, 2000);
    }
  }

  /** Create HUD overlay */
  _createHUD() {
    // Remove existing HUD
    if (this.hudElement) this.hudElement.remove();

    this.hudElement = document.createElement('div');
    this.hudElement.style.cssText = `
      position: absolute; top: 10px; left: 10px; z-index: 50;
      background: rgba(0,0,0,0.75); color: white; padding: 12px;
      border-radius: 6px; font: 12px/1.6 monospace; min-width: 180px;
      pointer-events: none;
    `;
    this.hudElement.id = 'scenario-hud';
    this.container.appendChild(this.hudElement);

    this._updateHUD();
  }

  /** Update HUD with current metrics */
  _updateHUD() {
    if (!this.hudElement) return;

    // Will be updated by the app via a separate method
    this.hudElement.innerHTML = `
      <div style="font-weight:bold;margin-bottom:4px;">HUD</div>
      <div id="hud-ttc">TTC: --</div>
      <div id="hud-drac">DRAC: --</div>
      <div id="hud-dv">ΔV: --</div>
      <div id="hud-cp">CP: --</div>
      <div id="hud-cpi">CPI: --</div>
      <div id="hud-status" style="margin-top:8px;">Status: Running</div>
    `;
  }

  /** Update HUD values — legacy API (called by app) */
  updateHUDValues(ttc, drac, dv, cp, cpi) {
    if (!this.hudElement) return;
    const setVal = (id, val, color) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = val;
      el.style.color = color || 'white';
    };

    setVal('hud-ttc', `TTC: ${ttc?.toFixed(2) || '--'}s`,
      this._getTTCColor(ttc));
    setVal('hud-drac', `DRAC: ${drac?.toFixed(1) || '--'} m/s²`,
      this._getDRACColor(drac));
    setVal('hud-dv', `ΔV: ${dv?.toFixed(1) || '--'} m/s`,
      this._getDVColor(dv));
    setVal('hud-cp', `CP: ${cp?.toFixed(1) || '--'}%`,
      this._getCPColor(cp));
    setVal('hud-cpi', `CPI: ${cpi?.toFixed(2) || '--'}`,
      this._getCPIColor(cpi));
  }

  /** Update HUD with full trajectory frame data (called by app.animateNominal) */
  updateHUD(frame) {
    if (!this.hudElement) return;
    const { ttc, collision } = frame;
    // Compute DRAC from velocity change rate
    const v_a = frame.v_a || 0;
    const v_b = frame.v_b || 0;
    const t = frame.time || 0;
    // Use stored previous state to estimate drac
    if (!this._prevV_b) this._prevV_b = v_b;
    if (!this._prevT) this._prevT = t;
    const dt = t - this._prevT;
    const drac = dt > 0.05 ? Math.abs((v_b - this._prevV_b) / dt) : 0;
    this._prevV_b = v_b;
    this._prevT = t;

    const cp = collision ? 100 : 0;
    const cpi = collision ? 1.0 : (ttc !== null && ttc > 0 ? Math.max(0, 1 - ttc / 10) : 0.5);
    this.updateHUDValues(ttc, drac, 0, cp, cpi);
  }

  /** Color coding helpers */
  _getTTCColor(ttc) {
    if (ttc === null || ttc === undefined) return 'white';
    if (ttc < 1.0) return '#8B0000';
    if (ttc < 2.0) return '#FF0000';
    if (ttc < 3.0) return '#FFA500';
    return '#228B22';
  }

  _getDRACColor(drac) {
    if (drac === null || drac === undefined) return 'white';
    if (drac > 8) return '#8B0000';
    if (drac > 5) return '#FF0000';
    if (drac > 3) return '#FFA500';
    return '#228B22';
  }

  _getDVColor(dv) {
    if (dv === null || dv === undefined) return 'white';
    if (dv > 15) return '#8B0000';
    if (dv > 10) return '#FF0000';
    if (dv > 5) return '#FFA500';
    return '#228B22';
  }

  _getCPColor(cp) {
    if (cp === null || cp === undefined) return 'white';
    if (cp > 50) return '#8B0000';
    if (cp > 30) return '#FF0000';
    if (cp > 10) return '#FFA500';
    return '#228B22';
  }

  _getCPIColor(cpi) {
    if (cpi === null || cpi === undefined) return 'white';
    if (cpi > 0.8) return '#8B0000';
    if (cpi > 0.5) return '#FF0000';
    if (cpi > 0.3) return '#FFA500';
    return '#228B22';
  }

  /** Get sky color for time of day */
  _getSkyColor() {
    const config = this.timeConfigs[this.timeOfDay] || this.timeConfigs.day;
    return config.skyColor;
  }

  /** Set time of day */
  setTimeOfDay(tod) {
    this.timeOfDay = tod;
    const config = this.timeConfigs[tod];
    if (!config) return;
    if (this.sun) this.sun.intensity = config.sunIntensity;
    this.scene?.background && (this.scene.background = new THREE.Color(config.skyColor));
  }

  /** Render frame (called in animation loop) */
  render() {
    if (this.mode === '3d' && this.renderer && this.camera && this.scene) {
      this.renderer.render(this.scene, this.camera);
    }
  }

  /** 2D rendering (top-down) */
  render2D(trajectoryFrame) {
    if (!this.ctx) return;

    const { t, x, v_a, v_b, a_a, a_b, collision } = trajectoryFrame;
    const w = this.canvas2D.width;
    const h = this.canvas2D.height;
    const cx = w / 2;
    const cy = h / 2;

    // Clear
    this.ctx.fillStyle = '#87CEEB';
    this.ctx.fillRect(0, 0, w, h);

    // Road
    this.ctx.fillStyle = '#333333';
    this.ctx.fillRect(0, cy - 40, w, 80);

    // Lane markings
    this.ctx.strokeStyle = '#FFFFFF';
    this.ctx.setLineDash([15, 10]);
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(0, cy);
    this.ctx.lineTo(w, cy);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // Shoulder lines
    this.ctx.strokeStyle = '#FFD700';
    this.ctx.lineWidth = 2;
    [cy - 40, cy + 40].forEach(y => {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(w, y);
      this.ctx.stroke();
    });

    // Vehicle A (lead) — white rectangle
    const ax = cx + (x || 0) * this.scale * 0.3;
    this.ctx.fillStyle = '#FFFFFF';
    this.ctx.fillRect(ax - 20, cy + 10, 40, 20);
    // Brake lights
    if (a_a && Math.abs(a_a) > 0.5) {
      this.ctx.fillStyle = `rgba(255, 0, 0, ${Math.min(Math.abs(a_a) / 8, 1)})`;
      this.ctx.fillRect(ax - 22, cy + 12, 4, 6);
      this.ctx.fillRect(ax - 22, cy + 22, 4, 6);
    }
    // Label
    this.ctx.fillStyle = 'black';
    this.ctx.font = '10px monospace';
    this.ctx.fillText('A', ax - 4, cy + 24);

    // Vehicle B (follow) — blue rectangle
    const bx = cx + 0 * this.scale * 0.3;
    this.ctx.fillStyle = '#4169E1';
    this.ctx.fillRect(bx - 20, cy - 30, 40, 20);
    // Brake lights
    if (a_b && Math.abs(a_b) > 0.5) {
      this.ctx.fillStyle = `rgba(255, 0, 0, ${Math.min(Math.abs(a_b) / 8, 1)})`;
      this.ctx.fillRect(bx - 22, cy - 28, 4, 6);
      this.ctx.fillRect(bx - 22, cy - 18, 4, 6);
    }
    // Label
    this.ctx.fillStyle = 'white';
    this.ctx.fillText('B', bx - 4, cy - 16);

    // Trajectory lines
    this.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([5, 5]);
    this.ctx.beginPath();
    this.ctx.moveTo(0, cy + 20);
    this.ctx.lineTo(w, cy + 20);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // HUD overlay (top-left)
    this.ctx.fillStyle = 'rgba(0,0,0,0.7)';
    this.ctx.fillRect(10, 10, 160, 80);
    this.ctx.fillStyle = 'white';
    this.ctx.font = '11px monospace';
    this.ctx.fillText(`t: ${(t || 0).toFixed(1)}s`, 18, 30);
    this.ctx.fillText(`gap: ${((x || 0) + 4.3).toFixed(1)}m`, 18, 48);
    this.ctx.fillText(`v_A: ${(v_a || 0).toFixed(1)} m/s`, 18, 66);
    this.ctx.fillText(`v_B: ${(v_b || 0).toFixed(1)} m/s`, 18, 84);

    // Collision marker
    if (collision) {
      this.ctx.fillStyle = 'rgba(255,0,0,0.3)';
      this.ctx.beginPath();
      this.ctx.arc(ax, cy + 20, 30, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.fillStyle = 'white';
      this.ctx.font = 'bold 14px monospace';
      this.ctx.fillText('COLLISION!', ax - 40, cy + 25);
    }
  }

  /** Destroy renderer and clean up */
  destroy() {
    this._destroy3D();
    this._destroy2D();
    if (this.hudElement) {
      this.hudElement.remove();
      this.hudElement = null;
    }
  }

  _destroy3D() {
    if (this.renderer) {
      this.renderer.dispose();
      if (this.renderer.domElement.parentNode === this.container) {
        this.container.removeChild(this.renderer.domElement);
      }
      this.renderer = null;
    }
    if (this._resizeHandler) {
      window.removeEventListener('resize', this._resizeHandler);
      this._resizeHandler = null;
    }
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  _destroy2D() {
    if (this.canvas2D && this.canvas2D.parentNode === this.container) {
      this.container.removeChild(this.canvas2D);
    }
    this.canvas2D = null;
    this.ctx = null;
  }

  /** Animate — called in requestAnimationFrame loop */
  animate(trajectoryFrame, onFrameEnd) {
    try {
      if (this.mode === '3d') {
        this.updateCamera(trajectoryFrame);
        this.render();
      } else {
        this.render2D(trajectoryFrame);
      }

      if (onFrameEnd) onFrameEnd();
      this.animationId = requestAnimationFrame(() => this.animate(trajectoryFrame, onFrameEnd));
    } catch (err) {
      // Error boundary: log but don't kill the animation loop
      console.error('[VisualizationEngine] Animation frame error:', err);
      // Attempt recovery: reset animation id to restart the loop
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
      // Restart animation after a brief pause to allow error recovery
      setTimeout(() => {
        if (this.mode === '3d' && this.renderer && this.camera && this.scene) {
          this.animationId = requestAnimationFrame(() => this.animate(trajectoryFrame, onFrameEnd));
        } else if (this.mode === '2d' && this.ctx) {
          this.animationId = requestAnimationFrame(() => this.animate(trajectoryFrame, onFrameEnd));
        }
      }, 100);
    }
  }

  /** Stop animation loop */
  stopAnimation() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  /** Get camera modes for UI */
  getCameraModes() {
    return ['auto-trace', 'free-look', 'top-down'];
  }

  /** Get time-of-day modes for UI */
  getTimeOfDayModes() {
    return ['day', 'sunset', 'night', 'overcast'];
  }

  /** Set scene fog (for depth) */
  setFog(fogEnabled, color = 0x87CEEB, near = 50, far = 200) {
    if (!this.scene) return;
    this.scene.fog = fogEnabled
      ? new THREE.Fog(color, near, far)
      : null;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VisualizationEngine };
}
