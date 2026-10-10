import * as THREE from 'three';
import { ease } from './tween.js';

// Walking inside the building, first person. The ground comes from
// demo/data/walk.json (scripts/build-walk.mjs): standing heights on a 0.25 m
// grid, several per cell where storeys or a stair and its landing overlap.
// A step goes to the height nearest the feet within one riser (stairs are
// ramps in the data), stops at walls and glass and slides along them; there is
// no mesh raycasting while walking.
//
// The grid is read as a smooth field, not cell by cell: each standing height
// knows how far it is to the nearest cell one cannot step to (its clearance),
// and the clearance and the height are interpolated between the four nearest
// cell centres. So a wall at 45°, drawn in cells as a staircase, is a straight
// edge to walk along, and a ramp rises evenly instead of in 10 to 30 cm jumps.
const NONE = -2147483648;
const HALF = 0.5;  // cells: clearance 0 lies on the edge between two cells
const REACH = 8;   // cells: clearance further from a wall is not needed
const AROUND8 = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, Math.SQRT2], [1, -1, Math.SQRT2], [-1, 1, Math.SQRT2], [-1, -1, Math.SQRT2]];

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
    this.clear = null;
  }

  // Layer of the height in cell i within one step of h (mm), or -1.
  within(i, h) {
    const max = this.maxStep * 1000;
    for (let k = 0; k < this.layers.length; k++) {
      const v = this.layers[k][i];
      if (v !== NONE && Math.abs(v - h) <= max) return k;
    }
    return -1;
  }

  // Clearance of every standing height, in cells: the distance to the nearest
  // neighbour cell it cannot step to, spread over the floor (Dijkstra on the
  // eight neighbours, up to REACH).
  clearance() {
    if (this.clear) return this.clear;
    const { width: W, height: H } = this.grid, N = W * H, L = this.layers.length;
    const dist = new Float32Array(N * L).fill(REACH);
    const heap = [];
    const push = (d, id) => {
      heap.push([d, id]);
      for (let i = heap.length - 1; i > 0;) {
        const up = (i - 1) >> 1;
        if (heap[up][0] <= heap[i][0]) break;
        [heap[up], heap[i]] = [heap[i], heap[up]];
        i = up;
      }
    };
    const pop = () => {
      const top = heap[0], last = heap.pop();
      if (heap.length) {
        heap[0] = last;
        for (let i = 0; ;) {
          const a = 2 * i + 1, b = a + 1;
          let m = i;
          if (a < heap.length && heap[a][0] < heap[m][0]) m = a;
          if (b < heap.length && heap[b][0] < heap[m][0]) m = b;
          if (m === i) break;
          [heap[m], heap[i]] = [heap[i], heap[m]];
          i = m;
        }
      }
      return top;
    };
    const each = (i, fn) => {
      const c = i % W, r = (i - c) / W;
      for (const [dc, dr, w] of AROUND8) {
        const nc = c + dc, nr = r + dr;
        fn(nc < 0 || nr < 0 || nc >= W || nr >= H ? -1 : nr * W + nc, w);
      }
    };
    for (let k = 0; k < L; k++) {
      for (let i = 0; i < N; i++) {
        const h = this.layers[k][i];
        if (h === NONE) continue;
        let d = REACH;
        each(i, (j, w) => { if (j < 0 || this.within(j, h) < 0) d = Math.min(d, w); });
        if (d < REACH) { dist[k * N + i] = d; push(d, k * N + i); }
      }
    }
    while (heap.length) {
      const [d, id] = pop();
      if (d > dist[id]) continue;
      const k = Math.floor(id / N), i = id % N, h = this.layers[k][i];
      each(i, (j, w) => {
        if (j < 0) return;
        const m = this.within(j, h);
        if (m < 0) return;
        const nid = m * N + j;
        if (d + w < dist[nid]) { dist[nid] = d + w; push(d + w, nid); }
      });
    }
    this.clear = dist;
    return dist;
  }

  // The smooth field at (x, z) for feet at `foot`: clearance in metres
  // (>= 0: one can stand here) and the floor height, both bilinear between
  // the four nearest cell centres.
  field(x, z, foot) {
    const { x: gx, z: gz, step, width, height } = this.grid, N = width * height, dist = this.clearance();
    const u = (x - gx) / step - 0.5, v = (z - gz) / step - 0.5;
    const c0 = Math.floor(u), r0 = Math.floor(v), fu = u - c0, fv = v - r0;
    let clear = 0, hw = 0, hs = 0;
    for (const [dc, dr, w] of [[0, 0, (1 - fu) * (1 - fv)], [1, 0, fu * (1 - fv)], [0, 1, (1 - fu) * fv], [1, 1, fu * fv]]) {
      const c = c0 + dc, r = r0 + dr;
      let k = -1, gap = Infinity;
      if (c >= 0 && r >= 0 && c < width && r < height) {
        for (let m = 0; m < this.layers.length; m++) {
          const t = this.layers[m][r * width + c];
          if (t === NONE) continue;
          const d = Math.abs(t / 1000 - foot);
          if (d <= this.maxStep && d < gap) { gap = d; k = m; }
        }
      }
      if (k < 0) { clear -= w * HALF; continue; }
      const i = r * width + c;
      clear += w * (dist[k * N + i] - HALF);
      hw += w;
      hs += w * (this.layers[k][i] / 1000);
    }
    return { clear: clear * step, height: hw ? hs / hw : null };
  }

  // Floor height at (x, z) if one can stand there, else null.
  ground(x, z, foot) {
    const f = this.field(x, z, foot);
    return f.clear >= 0 ? f.height : null;
  }

  // Move the eye by (dx, dz) in short steps. A step that ends inside a wall
  // is pushed back out along the field's gradient (twice, for corners): what
  // is left is the part of the step that runs along the wall, so the visitor
  // slides along walls at any angle and stops when walking straight into one.
  move(p, dx, dz) {
    const n = Math.max(1, Math.ceil(Math.hypot(dx, dz) / (this.grid.step * 0.25)));
    const sx = dx / n, sz = dz / n, e = 0.05;
    let moved = false;
    for (let i = 0; i < n; i++) {
      const foot = p.y - this.eye;
      let qx = p.x + sx, qz = p.z + sz, f = this.field(qx, qz, foot);
      // standing inside an edge (a sculpture placed after arriving): any step out is fine
      const here = this.field(p.x, p.z, foot).clear;
      if (here < 0 && f.height !== null && f.clear > here) { p.x = qx; p.z = qz; p.y = f.height + this.eye; moved = true; continue; }
      for (let k = 0; k < 2 && f.clear < 0; k++) {
        const gx = this.field(qx + e, qz, foot).clear - this.field(qx - e, qz, foot).clear;
        const gz = this.field(qx, qz + e, foot).clear - this.field(qx, qz - e, foot).clear;
        const g = Math.hypot(gx, gz);
        if (g < 1e-9) break;
        const back = -f.clear / Math.max(0.3, g / (2 * e)) + 0.002;
        qx += (gx / g) * back; qz += (gz / g) * back;
        f = this.field(qx, qz, foot);
      }
      // stuck, or pushed back the way it came: stop here
      if (f.clear < 0 || f.height === null || (qx - p.x) * sx + (qz - p.z) * sz <= 1e-9) break;
      p.x = qx; p.z = qz; p.y = f.height + this.eye;
      moved = true;
    }
    return moved;
  }
}

const SPEED = 1.9;   // m/s, an unhurried walk through the rooms
const SETTLE = 0.09; // s: the eye follows the floor height with this lag
const SPRINT = 2.4;  // Shift
const LOOK = 0.004;  // rad per pixel dragged
const HORIZONTAL_FOV = 90;
const KEYS = { KeyW: 'forward', ArrowUp: 'forward', KeyS: 'back', ArrowDown: 'back', KeyA: 'left', ArrowLeft: 'left', KeyD: 'right', ArrowRight: 'right' };

export class Walker {
  constructor(stage, surface) {
    this.stage = stage;
    this.surface = surface;
    this.camera = stage.rig.persp;
    this.body = new THREE.Vector3(); // where the visitor stands (eye height); the camera follows
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
      // a focused slider (the daylight) does not keep the arrows from walking
      if (!(this.active || this.arriving) || e.altKey || e.ctrlKey || e.metaKey || e.target.matches?.('textarea, select, input:not([type=range])') || e.target.isContentEditable) return;
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

  get foot() { return this.body.y - this.surface.eye; }

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
    this.body.set(at[0], at[1] + this.surface.eye, at[2]);
    this.camera.position.copy(this.body);
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
    if (!this.active || !dt) return false;
    const f = (this.held.has('forward') ? 1 : 0) - (this.held.has('back') ? 1 : 0);
    const s = (this.held.has('right') ? 1 : 0) - (this.held.has('left') ? 1 : 0);
    const len = Math.hypot(f, s);
    let moved = false;
    if (len) {
      const v = SPEED * (this.sprint ? SPRINT : 1) * dt / len;
      const sin = Math.sin(this.yaw), cos = Math.cos(this.yaw);
      moved = this.surface.move(this.body, (-sin * f + cos * s) * v, (-cos * f - sin * s) * v);
    }
    // the eye glides to the floor height (a step onto a landing, a threshold)
    const cam = this.camera.position, dy = this.body.y - cam.y;
    const settling = Math.abs(dy) > 0.001;
    if (!moved && !settling) return false;
    cam.x = this.body.x; cam.z = this.body.z;
    cam.y = settling ? cam.y + dy * (1 - Math.exp(-dt / SETTLE)) : this.body.y;
    this.camera.updateMatrixWorld();
    this.stage.dirty = true;
    return moved;
  }
}
