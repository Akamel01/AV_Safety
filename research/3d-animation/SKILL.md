---
name: 3d-animation
description: "Render parameterized collision scenarios in high-fidelity 3D (Three.js) with Canvas 2D fallback, driven by computed trajectories and collision probability."
---

# 3D Animation Engine

Render parameterized collision scenarios in high-fidelity 3D (Three.js) with fallback 2D mode, driven by computed trajectories and collision probability.

## 1. Technology Stack

### 3D Rendering
- **Three.js r160+** — WebGLRenderer with antialias, alpha, ACESFilmicToneMapping (exposure 1.0), sRGB output
- **Post-processing:** EffectComposer → RenderPass → UnrealBloomPass (collision flash) → FilmPass (grain) → MotionBlurPass

### 2D Fallback
- Canvas 2D, top-down orthographic view
- Smooth trajectory interpolation, color-coded indicators, scale reference bar, real-time overlay

### Asset Quality
| Asset | Level | Format | Details |
|---|-|---|---|
| Vehicles | High-poly | GLTF/GLB | PBR materials, normal maps, LOD |
| Roads | Detailed | GLTF/GLB | Lane markings, centerlines, curbs, sidewalks |
| Signage | Medium | GLTF/GLB | Stop signs, traffic lights, crosswalks |
| Pedestrians | Detailed | GLTF/GLB | Human mesh, walking animation |
| Cyclists | Detailed | GLTF/GLB | Bicycle + cyclist mesh |
| Environment | Optional | GLTF/GLB | Buildings, trees, weather |
| Collision FX | High | Custom shaders | Energy release, deformation, debris |

## 2. Core Systems

### Scene Manager
- Loads scenario assets in parallel: vehicles, road, signage, environment
- Configures renderer: ACESFilmicToneMapping, PCFSoftShadowMap, sRGBEncoding
- Time-of-day config: day (sun 1.0, ambient 0.4), sunset (0.7/0.3), night (0.1/0.1), overcast (0.5/0.5)

### Vehicle Model
- **Body:** MeshStandardMaterial — metalness 0.8, roughness 0.3, PBR color
- **Windows:** MeshPhysicalMaterial — transmission 0.9, thickness 0.1, ior 1.5
- **Lights:** Emissive headlights (shadow-cast at night), brakeLights intensity = min(braking/8, 1)
- **Types:** sedan, suv, truck, pedestrian, cyclist

### Lighting
- Ambient (0.4) + Directional sun (1.0) at (50, 100, 50) with 2048×2048 shadow map, frustum [-100, 100]
- Hemisphere sky/ground: 0x87CEEB → 0x362907 (intensity 0.3)

### Camera Modes
1. **auto-trace** — Follow leading vehicle from behind/above (offset -5, 3, 5), lerp 0.05
2. **free-look** — Orbit around collision point (radius 15, height 8)
3. **top-down** — Orthographic at (0, 50, 0)

### HUD Indicators
- TTC, DRAC, ΔV, CPI, CP, PCE
- Color scale: safe (#228B22) → moderate (#FFA500) → dangerous (#FF0000) → critical (#8B0000)
- TTC thresholds: < 1.0s critical, < 2.0s dangerous, < 3.0s moderate, else safe

### Probability-Driven Animation Decision
| Collision Prob | Mode | Speed | Slow-mo |
|---|-|-|-|
| ≥ 0.95 | certain-collision | 1.0 | normal |
| ≥ 0.70 | likely-collision | 0.8 | slight |
| ≥ 0.30 | possible-collision | 0.5 | significant |
| ≥ 0.10 | near-miss | 0.3 | dramatic |
| < 0.10 | safe-pass | 0.5 | none |

## 3. 2D Canvas Fallback Details

- Scale: 5 pixels per meter
- Vehicles: colored rectangles with heading arrow (green) and speed label
- Trajectories: white dashed lines (opacity 0.3)
- Indicators overlay in top-left corner (TTC, DRAC, ΔV)
- Smooth interpolation between trajectory points

## 4. Performance

| Area | Strategy |
|---|-|
| LOD | Switch mesh complexity by camera distance |
| Culling | Frustum culling only |
| Particles | GPU point sprites |
| Shadows | Cascade shadow maps |
| Textures | ASTC/ETC2 compression, texture atlasing |
| Physics | Fixed timestep dt = 0.01s |
| Animation | requestAnimationFrame, BufferGeometry batching |
| Memory | Asset streaming, object pooling, GC monitoring |

## 5. Integration Points

### Inputs
| From Skill | Data | Used For |
|---|-|-|
| scenario-taxonomy | Scenario parameters, severity levels | Scene configuration |
| kinematics-engine | Trajectory arrays (x, y, heading, speed) | Animation positions |
| indicator-computation | Real-time indicator values | HUD overlay |
| stochastic-simulation | Monte Carlo collision outcomes | Animation decision |
| bayesian-evt | Bayesian posterior results | Distribution plots |

### Outputs
| Format | Consumed By |
|---|-|
| 3D scene (HTML/JS/CSS) | Portfolio UI |
| 2D scene (Canvas 2D) | Portfolio UI |
| Indicator HUD (HTML overlay) | Portfolio UI |
| Distribution plots (D3.js/plotly.js) | Portfolio UI |

## 6. Quality Requirements

- **Visual:** PBR materials, PCF soft shadows, bloom post-processing, motion blur, ACES filmic tone mapping, sRGB
- **Animation:** Cubic Hermite interpolation, accurate physics, proper collision timing, realistic deformation, particle/debris/shockwave FX
- **UI:** Clean modern HUD, color-coded severity, responsive layout, accessible contrast

## Cross-Skill Dependencies

- **scenario-taxonomy** (upstream) — conflict types define scene configuration
- **kinematics-engine** (upstream) — trajectory arrays drive animation positions
- **indicator-computation** (upstream) — real-time indicator values drive HUD overlay
- **stochastic-simulation** (upstream) — Monte Carlo collision outcomes drive animation decisions
- **bayesian-evt** (upstream) — Bayesian posterior results drive distribution plots
- **portfolio-ui** (downstream) — 3D/2D scenes become portfolio visualization components

## File Structure (target — when src/animation/ package is created)

```
src/animation/
├── js/scene.js          Scene manager
├── js/vehicle.js        Vehicle class
├── js/road.js           Road geometry
├── js/lighting.js       Lighting system
├── js/camera.js         Camera controller
├── js/animation.js      Animation controller
├── js/collision_fx.js   Collision effects
├── js/indicators.js     HUD overlay
├── js/plots.js          Distribution plots
├── js/mc_visualizer.js  Monte Carlo visualization
├── js/renderer_3d.js    Three.js renderer
├── js/renderer_2d.js    Canvas 2D fallback
├── js/toggler.js        3D/2D toggle
├── js/loader.js         Asset loader
└── assets/vehicles/     sedan.glb, suv.glb, truck.glb, pedestrian.glb
    ├── assets/roads/    urban_intersection.glb, highway_segment.glb, freeway.glb
    └── assets/environment/ buildings.glb, trees.glb
```
