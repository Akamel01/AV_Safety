# 2D Canvas Fallback Renderer

Top-down orthographic 2D rendering with Canvas 2D.

## Top-Down Renderer (renderer_2d.js)

```javascript
class TopDownRenderer {
  constructor(container) {
    this.canvas = document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");
    container.appendChild(this.canvas);
    this.scale = 5; // pixels per meter
  }

  resize() {
    this.canvas.width = this.canvas.offsetWidth;
    this.canvas.height = this.canvas.offsetHeight;
  }

  render(vehicles, road, indicators, time) {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.drawRoad(road);
    vehicles.forEach(v => this.drawVehicle(v, time));
    this.drawTrajectories(vehicles);
    this.drawIndicators(indicators);
    this.drawScale();
  }

  drawVehicle(vehicle, time) {
    const scale = this.scale;
    const x = vehicle.position.x * scale;
    const y = vehicle.position.y * scale;
    const heading = vehicle.heading;

    this.ctx.save();
    this.ctx.translate(x, y);
    this.ctx.rotate(heading);

    // Vehicle body
    const w = vehicle.width * scale;
    const h = vehicle.length * scale;
    this.ctx.fillStyle = vehicle.color;
    this.ctx.fillRect(-w/2, -h/2, w, h);

    // Heading arrow (green)
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
          const x = p.x * this.scale;
          const y = p.y * this.scale;
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

## Mode Toggle (toggler.js)

```javascript
class RendererToggler {
  constructor(container) {
    this.container = container;
    this.currentMode = "3d"; // "3d" | "2d"
    this.threeCanvas = null;
    this.canvas2D = null;
  }

  toggle() {
    if (this.currentMode === "3d") {
      this.container.removeChild(this.threeCanvas);
      this.currentMode = "2d";
    } else {
      this.container.removeChild(this.canvas2D);
      this.currentMode = "3d";
    }
  }
}
```

## Monte Carlo Visualization (mc_visualizer.js)

```javascript
class MonteCarloVisualizer {
  constructor(container) {
    this.container = container;
  }

  renderMonteCarloResults(results) {
    const collisionCount = results.n_collisions;
    const totalRuns = results.n_samples;
    const collisionRate = results.collision_rate;

    // Circular gauge showing collision probability
    const angle = collisionRate * 2 * Math.PI - Math.PI / 2;
    const r = 50;
    const endX = r * Math.cos(angle);
    const endY = r * Math.sin(angle);
    // Draw gauge arc, needle at rate, CI as band

    this.renderOutcomeSummary({
      collisions: collisionCount,
      safe: totalRuns - collisionCount,
      total: totalRuns
    });

    this.renderTTCDistribution(results.TTC_values);
    this.renderSeverityDistribution(results.severity_values);
  }
}
```

## Distribution Plots (plots.js)

Use D3.js or plotly.js for:
- **TTC histogram:** X-axis = TTC values, Y-axis = frequency, color by severity
- **Severity CDF:** X-axis = collision severity, Y-axis = cumulative probability
- **Posterior samples:** X-axis = GPD parameters (xi, sigma), Y-axis = posterior density
