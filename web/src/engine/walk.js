import * as THREE from 'three';
import { ease } from './tween.js';

// Walking inside the building, first person. The ground comes from
// demo/data/walk.json (scripts/build-walk.mjs): standing heights on a 0.25 m
// grid, several per cell where storeys or a stair and its landing overlap.
// A step goes to the height nearest the feet within one riser, so the visitor
// climbs stairs, stops at walls and glass, and slides along them; there is no
// mesh raycasting while walking.
const NONE = -2147483648;

export class WalkSurface {
  constructor(data) {
    this.data = data;
    this.grid = data.grid;
    this.eye = data.eye_height_m;
    this.maxStep = data.maximum_step_m;
    const { width, height } = data.grid;
    this.layers = data.layers.map((layer) => {
      const h = new Int32Array(width * height).fill(NONE);
      layer.rows.forEach((runs, row) => runs.forEach(([start, n, mm]) => h.fill(mm, row * width + start, row * width + start + n)));
      return h;
    });
  }

  index(x, z) {
    const { x: gx, z: gz, step, width, height } = this.grid;
    const col = Math.floor((x - gx) / step), row = Math.floor((z - gz) / step);
    return col < 0 || row < 0 || col >= width || row >= height ? -1 : row * width + col;
  }

  // Standing height nearest the feet, at most maxStep away; null: no footing.
  sample(x, z, foot, maxStep = this.maxStep) {
    const i = this.index(x, z);
    if (i < 0) return null;
    let best = null, gap = Infinity;
    for (const layer of this.layers) {
      if (layer[i] === NONE) continue;
      const h = layer[i] / 1000, d = Math.abs(h - foot);
      if (d <= maxStep && d < gap) { best = h; gap = d; }
    }
    return best;
  }

  // Highest standing height in the cell at or below `top`.
  below(x, z, top) {
    const i = this.index(x, z);
    if (i < 0) return null;
    let best = null;
    for (const layer of this.layers) {
      if (layer[i] === NONE) continue;
      const h = layer[i] / 1000;
      if (h <= top && (best === null || h > best)) best = h;
    }
    return best;
  }

  // Nearest standing point to (x, z) on the floor at about height y, within
  // `radius` metres: [x, floor height, z] or null.
  nearest(x, z, y, radius = 1.5) {
    const { x: gx, z: gz, step, width, height } = this.grid;
    const c0 = Math.floor((x - gx) / step), r0 = Math.floor((z - gz) / step), n = Math.ceil(radius / step);
    let best = null, dist = Infinity;
    for (let r = Math.max(0, r0 - n); r <= Math.min(height - 1, r0 + n); r++) {
      for (let c = Math.max(0, c0 - n); c <= Math.min(width - 1, c0 + n); c++) {
        const px = gx + (c + 0.5) * step, pz = gz + (r + 0.5) * step;
        const d = (px - x) ** 2 + (pz - z) ** 2;
        if (d >= dist || d > radius * radius) continue;
        for (const layer of this.layers) {
          const v = layer[r * width + c];
          if (v !== NONE && Math.abs(v / 1000 - y) <= 0.6) { best = [px, v / 1000, pz]; dist = d; break; }
        }
      }
    }
    return best;
  }

  // Nothing to stand on within `r` of (x, z) at about height y (a sculpture).
  block(x, z, y, r) {
    const { x: gx, z: gz, step, width, height } = this.grid;
    for (let row = Math.max(0, Math.floor((z - r - gz) / step)); row <= Math.min(height - 1, Math.floor((z + r - gz) / step)); row++) {
      for (let col = Math.max(0, Math.floor((x - r - gx) / step)); col <= Math.min(width - 1, Math.floor((x + r - gx) / step)); col++) {
        for (const layer of this.layers) {
          const i = row * width + col;
          if (layer[i] !== NONE && Math.abs(layer[i] / 1000 - y) < 0.6) layer[i] = NONE;
        }
      }
    }
  }

  // Move the eye by (dx, dz) in short steps; blocked along one axis, slide
  // along the other. Returns whether anything moved.
  move(p, dx, dz) {
    const n = Math.max(1, Math.ceil(Math.hypot(dx, dz) / (this.grid.step * 0.4)));
    const sx = dx / n, sz = dz / n;
    let moved = false;
    for (let i = 0; i < n; i++) {
      const foot = p.y - this.eye;
      let h = this.sample(p.x + sx, p.z + sz, foot);
      if (h !== null) { p.x += sx; p.z += sz; p.y = h + this.eye; moved = true; continue; }
      h = this.sample(p.x + sx, p.z, foot);
      if (h !== null && sx) { p.x += sx; p.y = h + this.eye; moved = true; }
      h = this.sample(p.x, p.z + sz, p.y - this.eye);
      if (h !== null && sz) { p.z += sz; p.y = h + this.eye; moved = true; }
    }
    return moved;
  }
}

const SPEED = 1.9;   // m/s, an unhurried walk through the rooms
const SPRINT = 2.4;  // Shift
const LOOK = 0.004;  // rad per pixel dragged
const HORIZONTAL_FOV = 90;
const KEYS = { KeyW: 'forward', ArrowUp: 'forward', KeyS: 'back', ArrowDown: 'back', KeyA: 'left', ArrowLeft: 'left', KeyD: 'right', ArrowRight: 'right' };

export class Walker {
  constructor(stage, surface) {
    this.stage = stage;
    this.surface = surface;
    this.camera = stage.rig.persp;
    this.active = false;
    this.held = new Set();
    this.yaw = 0; this.pitch = -0.05;
    this.last = null;
    this.sprint = false;
    const canvas = stage.renderer.domElement;
    canvas.addEventListener('pointerdown', (e) => {
      if (!this.active || this.drag) return;
      this.drag = { id: e.pointerId, x: e.clientX, y: e.clientY };
      canvas.setPointerCapture?.(e.pointerId);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!this.drag || this.drag.id !== e.pointerId) return;
      // turn the head the way the hand moves (as in the Angora walk)
      this.yaw -= (e.clientX - this.drag.x) * LOOK;
      this.pitch = THREE.MathUtils.clamp(this.pitch - (e.clientY - this.drag.y) * LOOK, -1.2, 1.2);
      this.drag.x = e.clientX; this.drag.y = e.clientY;
      this.pose();
    });
    const release = (e) => { if (this.drag?.id === e.pointerId) this.drag = null; };
    canvas.addEventListener('pointerup', release);
    canvas.addEventListener('pointercancel', release);
    canvas.addEventListener('lostpointercapture', release);
    addEventListener('keydown', (e) => {
      if (!(this.active || this.arriving) || e.altKey || e.ctrlKey || e.metaKey || e.target.closest?.('input,select,textarea')) return;
      this.sprint = e.shiftKey;
      const k = KEYS[e.code];
      if (k) { e.preventDefault(); this.held.add(k); this.stage.dirty = true; }
    });
    addEventListener('keyup', (e) => { this.sprint = e.shiftKey; const k = KEYS[e.code]; if (k) this.held.delete(k); });
    addEventListener('blur', () => { this.held.clear(); this.drag = null; });
  }

  // On-screen arrows (touch): hold to walk.
  bindPad(buttons) {
    for (const b of buttons) {
      const k = b.dataset.walkDirection;
      const stop = () => this.held.delete(k);
      b.addEventListener('pointerdown', (e) => { if (!this.active) return; e.preventDefault(); b.setPointerCapture?.(e.pointerId); this.held.add(k); this.stage.dirty = true; });
      b.addEventListener('pointerup', stop);
      b.addEventListener('pointercancel', stop);
      b.addEventListener('lostpointercapture', stop);
      b.addEventListener('keydown', (e) => { if (this.active && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); this.held.add(k); } });
      b.addEventListener('keyup', (e) => { if (e.key === 'Enter' || e.key === ' ') stop(); });
      b.addEventListener('blur', stop);
    }
  }

  get foot() { return this.camera.position.y - this.surface.eye; }

  pose() {
    this.camera.rotation.set(this.pitch, this.yaw, 0, 'YXZ');
    this.camera.updateMatrixWorld();
    this.stage.dirty = true;
  }

  // Field of view held across the screen: a room fits in the frame on a
  // laptop and on a phone held upright.
  fov(w, h) {
    const aspect = w / Math.max(1, h);
    const v = 2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(HORIZONTAL_FOV) / 2) / aspect);
    return THREE.MathUtils.clamp(THREE.MathUtils.radToDeg(v), 50, 80);
  }

  // Stand at `at` = [x, floor height, z], facing `yaw`.
  start(at, yaw) {
    this.active = true;
    this.last = null;
    this.camera.position.set(at[0], at[1] + this.surface.eye, at[2]);
    this.yaw = yaw; this.pitch = -0.05;
    this.pose();
  }

  // Come down to eye height at `at`, then walk.
  async arrive(at, yaw, tweens, ms = 900) {
    this.stop();
    const y = at[1] + this.surface.eye, rise = 1.1, look = -0.6;
    this.yaw = yaw;
    this.arriving = true; // keys pressed meanwhile count
    this.camera.position.set(at[0], y + rise, at[2]);
    const done = await tweens.run('camera', ms, (t) => {
      this.camera.position.y = y + rise * (1 - t);
      this.pitch = look + (-0.05 - look) * t;
      this.pose();
    }, ease.out);
    this.arriving = false;
    if (done) this.start(at, yaw);
    return done;
  }

  stop() {
    this.active = false;
    this.held.clear();
    this.drag = null;
  }

  // Frame step: true when the camera moved.
  update(now) {
    const dt = this.last === null ? 0 : Math.min(0.12, (now - this.last) / 1000);
    this.last = now;
    if (!this.active || !this.held.size) return false;
    const f = (this.held.has('forward') ? 1 : 0) - (this.held.has('back') ? 1 : 0);
    const s = (this.held.has('right') ? 1 : 0) - (this.held.has('left') ? 1 : 0);
    const len = Math.hypot(f, s);
    if (!len || !dt) return false;
    const v = SPEED * (this.sprint ? SPRINT : 1) * dt / len;
    const sin = Math.sin(this.yaw), cos = Math.cos(this.yaw);
    const dx = (-sin * f + cos * s) * v, dz = (-cos * f - sin * s) * v;
    const moved = this.surface.move(this.camera.position, dx, dz);
    if (moved) { this.camera.updateMatrixWorld(); this.stage.dirty = true; }
    return moved;
  }
}
