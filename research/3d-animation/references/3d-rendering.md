# 3D Rendering — Three.js

Three.js r160+ with WebGLRenderer, antialias, ACESFilmicToneMapping (exposure 1.0), sRGB output.

Post-processing pipeline: EffectComposer → RenderPass → UnrealBloomPass (collision flash) → FilmPass (subtle grain) → MotionBlurPass.

## Renderer Config

```javascript
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
```

## Asset Quality

| Asset | Level | Format | Details |
|---|-|-|-|
| Vehicles | High-poly | GLTF/GLB | PBR, normal maps, LOD |
| Roads | Detailed | GLTF/GLB | Lane markings, curbs, sidewalks |
| Signage | Medium | GLTF/GLB | Stop signs, traffic lights, crosswalks |
| Pedestrians | Detailed | GLTF/GLB | Human mesh, walking animation |
| Cyclists | Detailed | GLTF/GLB | Bicycle + cyclist mesh |
| Environment | Optional | GLTF/GLB | Buildings, trees, weather |
| Collision FX | High | Custom shaders | Energy release, deformation, debris |

## Vehicle Model (Vehicle.js)

```javascript
class Vehicle {
  constructor(type, color) {
    this.type = type; // sedan, suv, truck, pedestrian, cyclist
    this.mesh = new THREE.Group();

    // Body — PBR
    const bodyGeom = this.getBodyGeometry(type);
    const bodyMat = new THREE.MeshStandardMaterial({
      metalness: 0.8, roughness: 0.3, color: new THREE.Color(color)
    });
    this.body = new THREE.Mesh(bodyGeom, bodyMat);

    // Windows — transparent
    const windowMat = new THREE.MeshPhysicalMaterial({
      metalness: 0, roughness: 0, transmission: 0.9, thickness: 0.1, ior: 1.5
    });

    this.wheels = this.createWheels(type);
    this.headlights = this.createHeadlights();
    this.brakeLights = this.createBrakeLights();

    this.mesh.add(this.body);
    this.mesh.add(this.wheels);
    this.mesh.add(this.headlights);
    this.mesh.add(this.brakeLights);
  }

  animate(trajectory, speed, braking) {
    this.mesh.position.set(trajectory.x, trajectory.y, 0);
    this.mesh.rotation.y = trajectory.heading;
    this.animateWheels(speed);
    this.brakeLights.intensity = braking > 0 ? Math.min(braking / 8, 1) : 0;
    if (this.time_of_day === "night") this.headlights.castShadow = true;
  }
}
```

## Road Geometry (Road.js)

```javascript
class RoadGeometry {
  createRoad(config) {
    // Main surface
    const roadGeom = new THREE.PlaneGeometry(config.width, config.length, 64, 64);
    const roadMat = new THREE.MeshStandardMaterial({ metalness: 0.1, roughness: 0.8, color: 0x333333 });

    // Lane markings (white dashed)
    const count = Math.floor(config.length / config.lane_width);
    const pts = [];
    for (let i = -count/2; i < count/2; i++) {
      pts.push(new THREE.Vector3(i * config.lane_width, 0.01, 0));
      pts.push(new THREE.Vector3(i * config.lane_width, 0.01, config.lane_width * 0.5));
    }
    const laneMarks = new THREE.LineSegments(
      new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({ color: 0xFFFFFF })
    );

    // Center line (yellow), edge lines (white), sidewalk
    // Intersection/crosswalk as needed
    return { road, laneMarks, centerLine, edgeLines, sidewalk, intersection, crosswalk };
  }
}
```

## Lighting (Lighting.js)

```javascript
class LightingSystem {
  constructor(scene, timeOfDay) {
    // Ambient
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambient);

    // Sun
    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(50, 100, 50);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 500;
    sun.shadow.camera.left = -100;
    sun.shadow.camera.right = 100;
    sun.shadow.camera.top = 100;
    sun.shadow.camera.bottom = -100;
    scene.add(sun);

    // Hemisphere
    const hemi = new THREE.HemisphereLight(0x87CEEB, 0x362907, 0.3);
    scene.add(hemi);

    this.updateForTimeOfDay(timeOfDay);
  }

  updateForTimeOfDay(timeOfDay) {
    const configs = {
      "day":    { sunIntensity: 1.0, ambientIntensity: 0.4, skyColor: 0x87CEEB },
      "sunset": { sunIntensity: 0.7, ambientIntensity: 0.3, skyColor: 0xFF8C00 },
      "night":  { sunIntensity: 0.1, ambientIntensity: 0.1, skyColor: 0x000022 },
      "overcast": { sunIntensity: 0.5, ambientIntensity: 0.5, skyColor: 0xCCCCCC }
    };
    const config = configs[timeOfDay] || configs["day"];
    // Update lights based on config
  }
}
```

## Camera (Camera.js)

```javascript
class CameraController {
  constructor(camera) {
    this.camera = camera;
    this.mode = "auto-trace"; // auto-trace, free-look, top-down
  }

  update(dt, vehicles) {
    switch (this.mode) {
      case "auto-trace":
        const targetPos = vehicles[0].mesh.position;
        const offset = new THREE.Vector3(-5, 3, 5);
        this.camera.position.lerp(targetPos.clone().add(offset), 0.05);
        this.camera.lookAt(targetPos);
        break;
      case "free-look":
        const angle = performance.now() * 0.0005;
        this.camera.position.set(Math.cos(angle)*15, 8, Math.sin(angle)*15);
        this.camera.lookAt(new THREE.Vector3(0, 0, 0));
        break;
      case "top-down":
        this.camera.position.set(0, 50, 0);
        this.camera.lookAt(new THREE.Vector3(0, 0, 0));
        break;
    }
  }
}
```

## Animation (Animation.js)

```javascript
class AnimationController {
  constructor(scene, vehicles, trajectories) {
    this.vehicles = vehicles;
    this.trajectories = trajectories; // [{x, y, heading, speed, braking, t}, ...]
    this.progress = 0;
    this.collisionOccurred = false;
  }

  update(dt) {
    this.progress += dt;
    const idx = this.findTrajectoryIndex(this.progress);
    const nextIdx = idx + 1;
    if (idx < 0 || !this.trajectories[idx]) return;

    const t = (this.progress - this.trajectories[idx].t) /
              (this.trajectories[nextIdx].t - this.trajectories[idx].t);

    for (let i = 0; i < this.vehicles.length; i++) {
      const tr = this.trajectories.filter(x => x.vehicleId === i)[idx];
      this.vehicles[i].animate(tr, tr.speed, tr.braking);
    }

    if (!this.collisionOccurred && this.progress >= this.collisionTime) {
      this.triggerCollision();
    }
  }

  triggerCollision() {
    this.collisionOccurred = true;
    this.createCollisionEffect();
    this.createShockwave();
    this.createDebris();
    this.animationSpeed = 0.1; // slow-mo
  }

  createDebris() {
    const debrisCount = 20;
    const geom = new THREE.BoxGeometry(0.1, 0.1, 0.1);
    const mat = new THREE.MeshStandardMaterial({ color: 0x444444 });
    for (let i = 0; i < debrisCount; i++) {
      const debris = new THREE.Mesh(geom, mat);
      debris.position.copy(this.collisionPoint);
      debris.velocity = new THREE.Vector3(
        (Math.random()-0.5)*10, Math.random()*5, (Math.random()-0.5)*10
      );
      // Animate: gravity + bounce + friction
    }
  }
}
```

## Collision Effects (collision_fx.js)

```javascript
createCollisionEffect() {
  const energy = computeKineticEnergy(this.vehicles);
  const flashIntensity = Math.min(energy / 10000, 1.0);

  // Flash light at collision point
  const flash = new THREE.PointLight(0xFF4500, flashIntensity * 10, 50);
  flash.position.copy(this.vehicles[0].mesh.position);
  this.scene.add(flash);

  // Bloom post-processing handles glow
  // Vehicle deformation: deform mesh vertices by deltaV
}
```

## Performance

| Strategy | Detail |
|---|-|
| LOD | Switch mesh complexity by camera distance |
| Frustum Culling | Only render objects in viewport |
| Instanced Rendering | Repeated elements (trees, poles) |
| Texture Atlasing | Combine textures to reduce draw calls |
| Shadows | Cascade shadow maps |
| Physics | Fixed timestep dt = 0.01s |
| GPU Particles | Point sprites for debris |
| Geometry | BufferGeometry batching |
| Sync | requestAnimationFrame |
| Memory | Asset streaming, object pooling, GC monitoring |
| Compression | ASTC/ETC2 textures |

## Post-Processing

```javascript
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(resolution, strength, radius, threshold));
composer.addPass(new FilmPass(0.1, 0.025, 64, false));
composer.addPass(new MotionBlurPass(0.016, 1.0));
```
