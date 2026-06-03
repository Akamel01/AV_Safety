# Skill: 3D Animation Engine

**Purpose:** Render parameterized collision scenarios in high-fidelity 3D (Three.js) with fallback 2D mode, driven by computed trajectories and collision probability.

## 1. Technology Stack

### 1.1 3D Rendering — Three.js
```json
{
  "engine": "three.js r160+",
  "renderer": {
    "type": "WebGLRenderer",
    "antialias": true,
    "alpha": false,
    "toneMapping": "ACESFilmicToneMapping",
    "toneMappingExposure": 1.0,
    "outputFormat": "sRGB"
  },
  "post-processing": [
    "EffectComposer",
    "RenderPass",
    "UnrealBloomPass (collision flash)",
    "FilmPass (subtle grain)",
    "MotionBlurPass"
  ]
}
```

### 1.2 2D Fallback — Canvas 2D
```javascript
{
  "renderer": "Canvas2D",
  "view": "top-down orthographic",
  "features": [
    "smooth trajectory interpolation",
    "color-coded indicators",
    "scale reference bar",
    "real-time indicator overlay"
  ]
}
```

### 1.3 Asset Quality — High Fidelity

| Asset Type | Level | Format | Details |
|---|-|-|-|
| Vehicles | High-poly | GLTF/GLB | PBR materials, normal maps, LOD levels |
| Roads | Detailed | GLTF/GLB | Lane markings, centerlines, curbs, sidewalks |
| Signage | Medium | GLTF/GLB | Stop signs, traffic lights, crosswalks |
| Pedestrians | Detailed | GLTF/GLB | Human mesh, walking animation |
| Cyclists | Detailed | GLTF/GLB | Bicycle + cyclist mesh |
| Environment | Optional | GLTF/GLB | Buildings, trees, weather |
| Collision FX | High | Custom shaders | Energy release, deformation, debris |

## 2. Scene Architecture

### 2.1 Scene Manager

```javascript
class ScenarioScene {
  constructor(config) {
    this.renderer = this.createRenderer();
    this.camera = new THREE.PerspectiveCamera();
    this.clock = new THREE.Clock();
    this.animationMixers = [];
    this.indicators = {};
  }
  
  createRenderer() {
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding;
    return renderer;
  }
  
  async loadScenario(scenarioConfig) {
    // Load scenario-specific assets
    const [vehicles, road, signage, environment] = await Promise.all([
      this.loadVehicles(scenarioConfig.road_users),
      this.loadRoad(scenarioConfig.geometry),
      this.loadSignage(scenarioConfig.infrastructure),
      this.loadEnvironment(scenarioConfig.time_of_day)
    ]);
    
    this.setupScene(vehicles, road, signage, environment);
    this.setupLighting(scenarioConfig.time_of_day);
  }
  
  setupScene(vehicles, road, signage, environment) {
    this.vehicles = vehicles;  // Array of GLTF vehicle meshes
    this.road = road;
    this.signage = signage;
    this.environment = environment;
  }
}
```

### 2.2 Vehicle Model (GLTF)

```javascript
// Vehicle mesh with PBR materials
class Vehicle {
  constructor(type, color) {
    this.type = type;  // "sedan", "suv", "truck", "pedestrian", "cyclist"
    this.mesh = new THREE.Group();
    
    // Main body (PBR)
    const bodyGeom = this.getBodyGeometry(type);
    const bodyMat = new THREE.MeshStandardMaterial({
      metalness: 0.8,
      roughness: 0.3,
      color: new THREE.Color(color)
    });
    this.body = new THREE.Mesh(bodyGeom, bodyMat);
    
    // Windows (transparent)
    const windowMat = new THREE.MeshPhysicalMaterial({
      metalness: 0,
      roughness: 0,
      transmission: 0.9,
      thickness: 0.1,
      ior: 1.5
    });
    
    // Wheels
    this.wheels = this.createWheels(type);
    
    // Lights (emissive)
    this.headlights = this.createHeadlights();
    this.brakeLights = this.createBrakeLights();
    
    this.mesh.add(this.body);
    this.mesh.add(this.wheels);
    this.mesh.add(this.headlights);
    this.mesh.add(this.brakeLights);
  }
  
  animate(trajectory, speed, braking) {
    // Map trajectory to 3D position and heading
    this.mesh.position.set(trajectory.x, trajectory.y, 0);
    this.mesh.rotation.y = trajectory.heading;
    
    // Animate wheels based on speed
    this.animateWheels(speed);
    
    // Brake lights based on braking intensity
    this.brakeLights.intensity = braking > 0 ? Math.min(braking / 8, 1) : 0;
    
    // Headlights based on time of day
    if (this.time_of_day === "night") {
      this.headlights.castShadow = true;
    }
  }
}
```

### 2.3 Road Geometry

```javascript
class RoadGeometry {
  createRoad(config) {
    // Main road surface
    const roadGeom = new THREE.PlaneGeometry(config.width, config.length, 64, 64);
    const roadMat = new THREE.MeshStandardMaterial({
      metalness: 0.1,
      roughness: 0.8,
      color: 0x333333
    });
    
    // Lane markings (white dashed lines)
    const laneMarks = this.createLaneMarkings(config);
    
    // Center line (yellow)
    const centerLine = this.createCenterLine(config);
    
    // Edge lines (white)
    const edgeLines = this.createEdgeLines(config);
    
    // Sidewalk
    const sidewalk = this.createSidewalk(config);
    
    // Intersection (if applicable)
    if (config.intersection) {
      const intersection = this.createIntersection(config.intersection);
    }
    
    // Crosswalk
    if (config.crosswalk) {
      const crosswalk = this.createCrosswalk(config.crosswalk);
    }
    
    return { road, laneMarks, centerLine, edgeLines, sidewalk, intersection, crosswalk };
  }
  
  createLaneMarkings(config) {
    const count = Math.floor(config.length / config.lane_width);
    const points = [];
    for (let i = -count/2; i < count/2; i++) {
      points.push(new THREE.Vector3(i * config.lane_width, 0.01, 0));
      points.push(new THREE.Vector3(i * config.lane_width, 0.01, config.lane_width * 0.5));
    }
    
    const geom = new THREE.BufferGeometry().setFromPoints(points);
    const mat = new THREE.LineBasicMaterial({ color: 0xFFFFFF });
    return new THREE.LineSegments(geom, mat);
  }
}
```

### 2.4 Lighting System

```javascript
class LightingSystem {
  constructor(scene, timeOfDay) {
    this.timeOfDay = timeOfDay;
    
    // Ambient light
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambient);
    
    // Sun (directional light)
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
    scene.add(sun);
    
    // Hemisphere light for sky/ground color variation
    const hemi = new THREE.HemisphereLight(0x87CEEB, 0x362907, 0.3);
    scene.add(hemi);
    
    this.updateForTimeOfDay(timeOfDay);
  }
  
  updateForTimeOfDay(timeOfDay) {
    const configs = {
      "day": { sunIntensity: 1.0, ambientIntensity: 0.4, skyColor: 0x87CEEB },
      "sunset": { sunIntensity: 0.7, ambientIntensity: 0.3, skyColor: 0xFF8C00 },
      "night": { sunIntensity: 0.1, ambientIntensity: 0.1, skyColor: 0x000022 },
      "overcast": { sunIntensity: 0.5, ambientIntensity: 0.5, skyColor: 0xCCCCCC }
    };
    
    const config = configs[timeOfDay] || configs["day"];
    // Update lights based on config
  }
}
```

## 3. Animation System

### 3.1 Trajectory-to-Animation Mapping

```javascript
class AnimationController {
  constructor(scene, vehicles, trajectories) {
    this.scene = scene;
    this.vehicles = vehicles;
    this.trajectories = trajectories;  // Array of {x, y, heading, speed, t}
    this.clock = new THREE.Clock();
    this.animationProgress = 0;
    this.collisionOccurred = false;
    this.collisionTime = null;
  }
  
  update(dt) {
    this.animationProgress += dt;
    
    // Find current trajectory index
    const currentIndex = this.findTrajectoryIndex(this.animationProgress);
    const nextIndex = currentIndex + 1;
    
    if (currentIndex < 0 || !this.trajectories[currentIndex]) {
      return;  // Animation complete
    }
    
    // Interpolate between current and next trajectory point
    const t = (this.animationProgress - this.trajectories[currentIndex].t) / 
              (this.trajectories[nextIndex].t - this.trajectories[currentIndex].t);
    
    const current = this.trajectories[currentIndex];
    const next = this.trajectories[nextIndex];
    
    for (let i = 0; i < this.vehicles.length; i++) {
      const vehicle = this.vehicles[i];
      const trajectory = this.trajectories.filter(t => t.vehicleId === i)[currentIndex];
      
      vehicle.animate(trajectory.position, trajectory.speed, trajectory.braking);
    }
    
    // Check if collision time has been reached
    if (!this.collisionOccurred && this.animationProgress >= this.collisionTime) {
      this.triggerCollision();
    }
  }
  
  triggerCollision() {
    this.collisionOccurred = true;
    
    // Create collision effect
    this.createCollisionEffect();
    
    // Trigger shockwave
    this.createShockwave();
    
    // Create debris particles
    this.createDebris();
    
    // Slow down remaining animation
    this.animationSpeed = 0.1;
  }
  
  createCollisionEffect() {
    // Kinetic energy visualization
    const energy = computeKineticEnergy(this.vehicles);
    const flashIntensity = Math.min(energy / 10000, 1.0);  // Normalize
    
    // Flash light at collision point
    const flash = new THREE.PointLight(0xFF4500, flashIntensity * 10, 50);
    flash.position.copy(this.vehicles[0].mesh.position);
    this.scene.add(flash);
    
    // Bloom post-processing for glow effect
    // (handled by EffectComposer)
    
    // Vehicle deformation
    this.vehicles.forEach(v => this.deformVehicle(v, energy));
  }
  
  createDebris() {
    const debrisCount = 20;
    const debrisGeom = new THREE.BoxGeometry(0.1, 0.1, 0.1);
    const debrisMat = new THREE.MeshStandardMaterial({ color: 0x444444 });
    
    for (let i = 0; i < debrisCount; i++) {
      const debris = new THREE.Mesh(debrisGeom, debrisMat);
      debris.position.copy(this.collisionPoint);
      
      const velocity = new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        Math.random() * 5,
        (Math.random() - 0.5) * 10
      );
      
      // Animate debris falling
      const debrisAnim = {
        update(dt) {
          debris.position.add(velocity.clone().multiplyScalar(dt));
          velocity.y -= 9.81 * dt;  // gravity
          if (debris.position.y < 0) {
            debris.position.y = 0;
            velocity.y *= -0.5;  // bounce
            velocity.multiplyScalar(0.8);  // friction
          }
        }
      };
      
      this.scene.add(debris);
      debrisAnims.push(debrisAnim);
    }
  }
}
```

### 3.2 Camera System

```javascript
class CameraController {
  constructor(camera, scene) {
    this.camera = camera;
    this.scene = scene;
    this.mode = "auto-trace";  // "auto-trace", "free-look", "top-down"
    this.autoTraceTarget = null;
    this.freeLookTarget = new THREE.Vector3(0, 0, 0);
  }
  
  update(dt) {
    switch (this.mode) {
      case "auto-trace":
        // Follow the leading vehicle
        if (this.autoTraceTarget) {
          const targetPos = this.autoTraceTarget.mesh.position;
          const offset = new THREE.Vector3(-5, 3, 5);  // Behind and above
          const desiredPos = targetPos.clone().add(offset);
          
          this.camera.position.lerp(desiredPos, 0.05);
          this.camera.lookAt(targetPos);
        }
        break;
        
      case "free-look":
        // Camera orbit around collision point
        const angle = performance.now() * 0.0005;
        const radius = 15;
        this.camera.position.set(
          Math.cos(angle) * radius,
          8,
          Math.sin(angle) * radius
        );
        this.camera.lookAt(this.freeLookTarget);
        break;
        
      case "top-down":
        // Orthographic view (used for 2D fallback)
        this.camera.position.set(0, 50, 0);
        this.camera.lookAt(new THREE.Vector3(0, 0, 0));
        break;
    }
  }
}
```

## 4. Indicator Display

### 4.1 HUD Overlay

```javascript
class IndicatorHUD {
  constructor(container) {
    this.container = container;
    this.indicators = [];
    this.createElements();
  }
  
  createElements() {
    this.container.innerHTML = `
      <div class="hud-panel">
        <h3>Real-Time Indicators</h3>
        <div class="indicator-row"><span class="label">TTC:</span><span class="value" id="ttc">--</span></div>
        <div class="indicator-row"><span class="label">DRAC:</span><span class="value" id="drac">--</span></div>
        <div class="indicator-row"><span class="label">ΔV:</span><span class="value" id="delta_v">--</span></div>
        <div class="indicator-row"><span class="label">CPI:</span><span class="value" id="cpi">--</span></div>
        <div class="indicator-row"><span class="label">CP:</span><span class="value" id="cp">--</span></div>
        <div class="indicator-row"><span class="label">PCE:</span><span class="value" id="pce">--</span></div>
      </div>
    `;
  }
  
  update(indicators) {
    // Update individual indicator values
    document.getElementById("ttc").textContent = `${indicators.TTC.toFixed(2)}s`;
    document.getElementById("drac").textContent = `${indicators.DRAC.toFixed(1)} m/s²`;
    document.getElementById("delta_v").textContent = `${indicators.delta_v.toFixed(1)} m/s`;
    document.getElementById("cpi").textContent = indicators.CPI.toFixed(3);
    document.getElementById("cp").textContent = (indicators.CP * 100).toFixed(1) + "%";
    document.getElementById("pce").textContent = `${indicators.PCE.toFixed(0)} J`;
    
    // Color-code by severity
    this.colorCodeBySeverity(indicators);
  }
  
  colorCodeBySeverity(indicators) {
    const colorScale = {
      "safe": "#228B22",
      "moderate": "#FFA500",
      "dangerous": "#FF0000",
      "critical": "#8B0000"
    };
    
    // Set background colors based on TTC severity
    const ttcColor = indicators.TTC < 1.0 ? "critical" :
                     indicators.TTC < 2.0 ? "dangerous" :
                     indicators.TTC < 3.0 ? "moderate" : "safe";
    
    document.getElementById("ttc").style.backgroundColor = colorScale[ttcColor];
    // ... similar for other indicators
  }
}
```

### 4.2 Distribution Plots

```javascript
class DistributionPlots {
  constructor(container) {
    this.container = container;
    this.createPlotPanels();
  }
  
  createPlotPanels() {
    // TTC histogram
    const ttcPanel = this.createElement("ttc_histogram");
    // Severity CDF
    const sevPanel = this.createElement("severity_cdf");
    // Posterior samples
    const postPanel = this.createElement("posterior_samples");
  }
  
  renderTTCHistogram(data) {
    // D3.js or plotly.js for histogram
    // X-axis: TTC values
    // Y-axis: frequency
    // Color: based on severity level
  }
  
  renderSeverityCDF(data) {
    // D3.js or plotly.js for CDF
    // X-axis: collision severity
    // Y-axis: cumulative probability
  }
  
  renderPosteriorSamples(data) {
    // D3.js or plotly.js for posterior distribution
    // X-axis: GPD parameters (xi, sigma)
    // Y-axis: posterior density
  }
}
```

## 5. 2D Fallback Mode

### 5.1 Top-Down Canvas 2D

```javascript
class TopDownRenderer {
  constructor(container) {
    this.canvas = document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");
    container.appendChild(this.canvas);
    this.resize();
  }
  
  resize() {
    this.canvas.width = this.canvas.offsetWidth;
    this.canvas.height = this.canvas.offsetHeight;
  }
  
  render(vehicles, road, indicators, time) {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw road
    this.drawRoad(road);
    
    // Draw vehicles
    vehicles.forEach(v => {
      this.drawVehicle(v, time);
    });
    
    // Draw trajectories
    this.drawTrajectories(vehicles);
    
    // Draw indicators
    this.drawIndicators(indicators);
    
    // Draw scale reference
    this.drawScale();
  }
  
  drawVehicle(vehicle, time) {
    const scale = 5;  // pixels per meter
    const x = vehicle.position.x * scale;
    const y = vehicle.position.y * scale;
    const heading = vehicle.heading;
    
    this.ctx.save();
    this.ctx.translate(x, y);
    this.ctx.rotate(heading);
    
    // Vehicle body (rectangle)
    const w = vehicle.width * scale;
    const h = vehicle.length * scale;
    this.ctx.fillStyle = vehicle.color;
    this.ctx.fillRect(-w/2, -h/2, w, h);
    
    // Heading arrow
    this.ctx.beginPath();
    this.ctx.moveTo(w/2, 0);
    this.ctx.lineTo(w/2 + 15, -8);
    this.ctx.lineTo(w/2 + 15, 8);
    this.ctx.closePath();
    this.ctx.fillStyle = "#00FF00";
    this.ctx.fill();
    
    // Speed label
    this.ctx.fillStyle = "#FFFFFF";
    this.ctx.font = "12px monospace";
    this.ctx.fillText(`${vehicle.speed.toFixed(1)} m/s`, -w/2, -h/2 - 5);
    
    this.ctx.restore();
  }
  
  drawTrajectories(vehicles) {
    this.ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
    this.ctx.lineWidth = 2;
    
    vehicles.forEach(v => {
      if (v.trail.length > 1) {
        this.ctx.beginPath();
        v.trail.forEach((p, i) => {
          const x = p.x * 5;
          const y = p.y * 5;
          if (i === 0) this.ctx.moveTo(x, y);
          else this.ctx.lineTo(x, y);
        });
        this.ctx.stroke();
      }
    });
  }
  
  drawIndicators(indicators) {
    this.ctx.fillStyle = "#FFFFFF";
    this.ctx.font = "14px monospace";
    this.ctx.fillText(`TTC: ${indicators.TTC.toFixed(2)}s`, 10, 20);
    this.ctx.fillText(`DRAC: ${indicators.DRAC.toFixed(1)} m/s²`, 10, 38);
    this.ctx.fillText(`ΔV: ${indicators.delta_v.toFixed(1)} m/s`, 10, 56);
  }
}
```

## 6. Collision vs Avoidance Decision

### 6.1 Probability-Driven Animation

```javascript
class AnimationDecisionEngine {
  constructor() {
    this.thresholds = {
      certain_collision: 0.95,
      likely_collision: 0.70,
      possible_collision: 0.30,
      unlikely_collision: 0.10
    };
  }
  
  getAnimationType(collisionProbability, deltaV, impactAngle) {
    if (collisionProbability > this.thresholds.certain_collision) {
      return "certain-collision";
    } else if (collisionProbability > this.thresholds.likely_collision) {
      return "likely-collision";
    } else if (collisionProbability > this.thresholds.possible_collision) {
      return "possible-collision";
    } else if (collisionProbability > this.thresholds.unlikely_collision) {
      return "near-miss";
    } else {
      return "safe-pass";
    }
  }
  
  getAnimationConfig(type, deltaV, impactAngle) {
    const configs = {
      "certain-collision": {
        speed: 1.0,  // normal speed
        flashIntensity: Math.min(deltaV / 30, 1.0),
        debrisCount: Math.floor(30 * (deltaV / 30)),
        vehicleDeformation: 0.1 * (deltaV / 30)
      },
      "likely-collision": {
        speed: 0.8,  // slight slow-mo
        flashIntensity: Math.min(deltaV / 40, 0.8),
        debrisCount: Math.floor(20 * (deltaV / 40)),
        vehicleDeformation: 0.08 * (deltaV / 40)
      },
      "possible-collision": {
        speed: 0.5,  // significant slow-mo
        flashIntensity: Math.min(deltaV / 50, 0.6),
        debrisCount: Math.floor(10 * (deltaV / 50)),
        vehicleDeformation: 0.05 * (deltaV / 50)
      },
      "near-miss": {
        speed: 0.3,  // dramatic slow-mo
        flashIntensity: 0.0,
        debrisCount: 0,
        vehicleDeformation: 0.0,
        evasiveManeuver: true
      },
      "safe-pass": {
        speed: 0.5,
        flashIntensity: 0.0,
        debrisCount: 0,
        vehicleDeformation: 0.0
      }
    };
    
    return configs[type] || configs["safe-pass"];
  }
}
```

## 7. Monte Carlo Outcome Visualization

### 7.1 Stochastic Outcome Display

```javascript
class MonteCarloVisualizer {
  constructor(container) {
    this.container = container;
  }
  
  renderMonteCarloResults(results) {
    // Show distribution of outcomes
    const collisionCount = results.n_collisions;
    const totalRuns = results.n_samples;
    const collisionRate = results.collision_rate;
    
    // Probability gauge
    this.renderProbabilityGauge(collisionRate, results.collision_rate_ci95);
    
    // Outcome summary
    this.renderOutcomeSummary({
      collisions: collisionCount,
      safe: totalRuns - collisionCount,
      total: totalRuns
    });
    
    // TTC distribution
    this.renderTTCDistribution(results.TTC_values);
    
    // Severity distribution
    this.renderSeverityDistribution(results.severity_values);
  }
  
  renderProbabilityGauge(rate, ci) {
    // Circular gauge showing collision probability
    const angle = rate * 2 * Math.PI - Math.PI / 2;
    const r = 50;
    const endX = r * Math.cos(angle);
    const endY = r * Math.sin(angle);
    
    // Draw gauge arc
    // Draw needle at rate
    // Show CI as band around arc
  }
}
```

## 8. File Structure

```
src/animation/
├── __init__.py           # For Python backend (server-side)
├── js/
│   ├── __init__.py
│   ├── scene.js          # Scene manager
│   ├── vehicle.js        # Vehicle class
│   ├── road.js           # Road geometry
│   ├── lighting.js       # Lighting system
│   ├── camera.js         # Camera controller
│   ├── animation.js      # Animation controller
│   ├── collision_fx.js   # Collision effects
│   ├── indicators.js     # HUD overlay
│   ├── plots.js          # Distribution plots
│   ├── mc_visualizer.js  # Monte Carlo visualization
│   ├── renderer_3d.js    # Three.js renderer
│   ├── renderer_2d.js    # Canvas 2D fallback
│   ├── toggler.js        # 3D/2D mode toggle
│   └── loader.js         # Asset loader
└── assets/
    ├── vehicles/
    │   ├── sedan.glb
    │   ├── suv.glb
    │   ├── truck.glb
    │   └── pedestrian.glb
    ├── roads/
    │   ├── urban_intersection.glb
    │   ├── highway_segment.glb
    │   └── freeway.glb
    └── environment/
        ├── buildings.glb
        └── trees.glb
```

## 9. Performance Optimization

### 9.1 Rendering Performance
- **Level of Detail (LOD):** Switch mesh complexity based on camera distance
- **Frustum Culling:** Only render objects in camera viewport
- **Instanced Rendering:** For repeated elements (trees, poles)
- **Texture Atlasing:** Reduce draw calls by combining textures
- **Shadow Maps:** Use cascade shadow maps for multiple lights

### 9.2 Animation Performance
- **Fixed timestep physics:** dt = 0.01s
- **GPU particle systems:** Use point sprites for debris
- **BufferGeometry updates:** Batch vertex updates
- **RequestAnimationFrame:** Sync rendering with display refresh

### 9.3 Memory Management
- **Asset streaming:** Load only required assets
- **Object pooling:** Reuse vehicle meshes, particles
- **Texture compression:** Use ASTC/ETC2 compressed textures
- **Garbage collection:** Monitor and clean up unused objects

## 10. Integration Points

### 10.1 Input from Other Skills
| Skill | Data | Used For |
|---|-|---|
| **scenario-taxonomy** | Scenario parameters, severity levels | Scene configuration |
| **kinematics-engine** | Trajectory arrays (x, y, heading, speed) | Animation positions |
| **indicator-computation** | Real-time indicator values | HUD overlay |
| **stochastic-simulation** | Monte Carlo collision outcomes | Animation decision |
| **bayesian-evt** | Bayesian posterior results | Distribution plots |

### 10.2 Output
| Output | Format | Consumed By |
|---|-|---|
| 3D scene | HTML/JS/CSS | Portfolio UI |
| 2D scene | Canvas 2D | Portfolio UI |
| Indicator HUD | HTML overlay | Portfolio UI |
| Distribution plots | D3.js/plotly.js | Portfolio UI |
| Collision rate | JSON | Bayesian EVT |

## 11. Quality Requirements

### 11.1 Visual Polish
- PBR materials on all vehicles (metallic, roughness, normal maps)
- Shadow mapping with PCF soft shadows
- Bloom post-processing for collision flash
- Motion blur for high-speed animation
- ACES filmic tone mapping for cinematic look
- Proper color space (sRGB)

### 11.2 Animation Quality
- Smooth interpolation (cubic Hermite)
- Accurate physics (no jitter)
- Proper collision timing
- Realistic vehicle deformation
- Particle effects for debris
- Shockwave effects for impact

### 11.3 UI Quality
- Clean, modern HUD design
- Color-coded indicators by severity
- Responsive layout for all screen sizes
- Smooth transitions between states
- Accessible contrast ratios
