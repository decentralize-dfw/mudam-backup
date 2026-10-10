import * as THREE from 'three';

// Malzemelere ayır: the building taken apart by material layer.
//
// Every vertex carries its fragment's centre and layer (_piece, baked by
// scripts/build-model.mjs), so the joined meshes still fly apart fragment by
// fragment. The offset is computed in the vertex shader, in the shadow (depth)
// shader and in the trail lines from the same GLSL, and once more on the CPU
// for the labels; the four must agree, which is why the formula lives here once.
export const LAYERS = ['floors', 'walls', 'ceilings', 'frames', 'glass', 'fittings'];
export const LAYER_COLOURS = { floors: '#9a7650', walls: '#c8b07e', ceilings: '#8f9a96', frames: '#38454d', glass: '#5f9fc2', fittings: '#b4533b' };

// Vertical: one tier per layer in reading order, floors at the bottom with the
// stairs and fittings that stand on them, glass on top. Within a tier the
// storeys are drawn apart a little (STRETCH per metre of height) so the
// plates read separately. Tier heights leave a clear gap between layers.
const LIFT = { floors: 0, fittings: 0, walls: 18, ceilings: 46, frames: 76, glass: 124 };
const STRETCH = 0.3;

// Hemisphere: floors and fittings stay as the core, pushed out only a
// little; every other layer settles on its own hemispherical shell around a
// point under the middle of the building, glass outermost. Shell radius =
// SHELL + SPREAD per metre the fragment stood from that point, so a shell has
// some depth and the building's plan is still legible on it.
const SHELL = { floors: 0, fittings: 0, walls: 72, ceilings: 90, frames: 108, glass: 126 };
const CORE_PUSH = 1.5;
const CORE_SPREAD = 0.08;
const SPREAD = 0.15;

export const CENTRE = new THREE.Vector3(-1, -6, 2);
const isShell = (l) => SHELL[l] > 0;

const GLSL = /* glsl */`
attribute vec4 _piece;
uniform float uVert;
uniform float uRad;
uniform vec3 uCentre;
uniform float uLift[6];
uniform float uPush[6];
uniform float uSpread[6];
uniform float uPull[6];
vec3 pieceOffset(vec4 p) {
  int L = int(p.w + 0.5);
  vec3 v = vec3(0.0, uLift[L] + ${STRETCH.toFixed(3)} * max(p.y, 0.0), 0.0);
  vec3 d = p.xyz - uCentre;
  float h = length(d.xz);
  vec3 dir = normalize(vec3(d.x, 0.9 * max(d.y, 0.0) + 0.15 * h + 1.5, d.z));
  vec3 r = dir * (uPush[L] + uSpread[L] * length(d)) - d * uPull[L];
  return uVert * v + uRad * r;
}
`;

const PUSH = LAYERS.map((l) => (isShell(l) ? SHELL[l] : CORE_PUSH));
const SPREADS = LAYERS.map((l) => (isShell(l) ? SPREAD : CORE_SPREAD));
const PULL = LAYERS.map((l) => (isShell(l) ? 1 : 0));

export function pieceOffset(p, li, vert, rad, target = new THREE.Vector3()) {
  const vy = LIFT[LAYERS[li]] + STRETCH * Math.max(p.y, 0);
  const d = p.clone().sub(CENTRE);
  const h = Math.hypot(d.x, d.z);
  const dir = new THREE.Vector3(d.x, 0.9 * Math.max(d.y, 0) + 0.15 * h + 1.5, d.z).normalize();
  const r = dir.multiplyScalar(PUSH[li] + SPREADS[li] * d.length()).addScaledVector(d, -PULL[li]);
  return target.set(0, vy * vert, 0).addScaledVector(r, rad);
}

// Trails drawn per layer.
const TRAILS = { floors: 5, walls: 7, ceilings: 5, frames: 6, glass: 6, fittings: 3 };

// k fragments far apart from each other, larger ones first (farthest-point
// sampling weighted by size).
function spread(list, k) {
  if (list.length <= k) return list;
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const sorted = [...list].sort((a, b) => b[4] - a[4]);
  const out = [sorted[0]];
  const d = sorted.map((p) => dist(p, sorted[0]));
  while (out.length < k) {
    let bi = 0;
    for (let i = 1; i < sorted.length; i++) if (d[i] * Math.sqrt(sorted[i][4]) > d[bi] * Math.sqrt(sorted[bi][4])) bi = i;
    const q = sorted[bi];
    out.push(q);
    for (let i = 0; i < sorted.length; i++) d[i] = Math.min(d[i], dist(sorted[i], q));
  }
  return out;
}

// Mid radius of a layer's shell, where its guide arc and label sit.
const shellRadius = (l) => SHELL[l] + SPREAD * 34;

export class MaterialExplode {
  constructor(scene) {
    this.scene = scene;
    this.uniforms = {
      uVert: { value: 0 },
      uRad: { value: 0 },
      uCentre: { value: CENTRE.clone() },
      uLift: { value: LAYERS.map((l) => LIFT[l]) },
      uPush: { value: PUSH },
      uSpread: { value: SPREADS },
      uPull: { value: PULL },
    };
    this.mode = 'off';
    this.layerGroups = {};
    this.hidden = new Set();
    this.glass = [];
    this.right = new THREE.Vector3(1, 0, 0);
    // shadows follow the parts: same offset in the depth pass
    this.depthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });
    this.depthMaterial.onBeforeCompile = (shader) => this.inject(shader);
    this.depthMaterial.customProgramCacheKey = () => 'mudam-explode-depth';
  }

  inject(shader) {
    Object.assign(shader.uniforms, this.uniforms);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', `#include <common>\n${GLSL}`)
      .replace('#include <begin_vertex>', '#include <begin_vertex>\ntransformed += pieceOffset(_piece);');
  }

  // Patch the visible building's materials and meshes (band 0).
  attach(root) {
    const seen = new Set();
    root.traverse((o) => {
      if (!o.isMesh || !o.geometry.attributes._piece) return;
      o.customDepthMaterial = this.depthMaterial;
      // explosion leaves the bounding volumes behind
      o.frustumCulled = false;
      const layer = findLayer(o);
      if (layer) (this.layerGroups[layer] ??= []).push(o);
      if (layer && this.hidden.has(layer)) o.visible = false;
      const m = o.material;
      if (seen.has(m)) return;
      seen.add(m);
      // taken apart, the panes need a little more body to be read
      if (m.userData.glass) this.glass.push({ m, base: m.opacity });
      const prev = m.onBeforeCompile;
      m.onBeforeCompile = (shader, renderer) => { prev?.call(m, shader, renderer); this.inject(shader); };
      m.customProgramCacheKey = () => 'mudam-explode';
      m.needsUpdate = true;
    });
  }

  // Dashed trails from where a fragment was to where it goes (the dash runs
  // along the travelled distance): only a few per layer, spread over the
  // plan, so they read as a diagram rather than a mesh. For the hemisphere
  // also the shells' outlines, like the arcs of a section drawing.
  build(data, key = 1) {
    const kept = LAYERS.flatMap((l, li) => spread(data.pieces.filter((p) => p[3] === li && p[4] >= 3), TRAILS[l]));
    const n = kept.length;
    const piece = new Float32Array(n * 2 * 4), end = new Float32Array(n * 2), pos = new Float32Array(n * 2 * 3), col = new Float32Array(n * 2 * 3);
    const c = new THREE.Color();
    kept.forEach((p, k) => {
      c.set(LAYER_COLOURS[LAYERS[p[3]]]).convertSRGBToLinear();
      for (let e = 0; e < 2; e++) {
        const v = k * 2 + e;
        piece.set([p[0], p[1], p[2], p[3]], v * 4);
        pos.set([p[0], p[1], p[2]], v * 3);
        col.set([c.r * 0.6, c.g * 0.6, c.b * 0.6], v * 3);
        end[v] = e;
      }
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('_piece', new THREE.BufferAttribute(piece, 4));
    g.setAttribute('aEnd', new THREE.BufferAttribute(end, 1));
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const material = new THREE.ShaderMaterial({
      uniforms: { ...this.uniforms, uHidden: { value: LAYERS.map((l) => (this.hidden.has(l) ? 1 : 0)) } },
      transparent: true,
      depthWrite: false,
      vertexShader: /* glsl */`${GLSL}
        attribute float aEnd;
        attribute vec3 color;
        uniform float uHidden[6];
        varying float vDist;
        varying vec3 vColour;
        varying float vHide;
        void main() {
          vec3 o = pieceOffset(_piece);
          vDist = aEnd * length(o);
          vColour = color;
          vHide = uHidden[int(_piece.w + 0.5)];
          gl_Position = projectionMatrix * viewMatrix * vec4(_piece.xyz + o * aEnd, 1.0);
        }`,
      fragmentShader: /* glsl */`
        uniform float uVert;
        uniform float uRad;
        varying float vDist;
        varying vec3 vColour;
        varying float vHide;
        void main() {
          if (vHide > 0.5) discard;
          if (mod(vDist, 3.4) > 2.0) discard;
          float a = smoothstep(0.05, 0.6, max(uVert, uRad));
          gl_FragColor = vec4(vColour, 0.6 * a);
        }`,
    });
    const trails = new THREE.LineSegments(g, material);
    trails.frustumCulled = false;
    trails.renderOrder = 7;
    trails.visible = false;
    this.scene.add(trails);

    // per-layer label anchors: weighted centre of the fragments
    const anchors = LAYERS.map((_, li) => {
      const list = data.pieces.filter((p) => p[3] === li);
      const w = list.reduce((s, p) => s + p[4], 0) || 1;
      const centre = list.reduce((acc, p) => acc.add(new THREE.Vector3(p[0], p[1], p[2]).multiplyScalar(p[4] / w)), new THREE.Vector3());
      return { centre, count: list.length };
    });
    // one set of trails per model source (Çevre 1, Çevre 2)
    this.sets ??= {};
    this.sets[key] = { trails, anchors };
    if (!this.trails || key === this.key) this.use(key);
    if (this.arcs) return;

    // shell outlines: a dashed half circle per shell, turned to face the
    // camera, and the ground line they stand on
    this.arcs = new THREE.Group();
    this.arcs.position.copy(CENTRE);
    this.arcs.visible = false;
    const outer = shellRadius('glass') + 10;
    const lineOf = (points, colour) => {
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), new THREE.LineDashedMaterial({ color: colour, dashSize: 2.2, gapSize: 1.6, transparent: true, opacity: 0, depthWrite: false }));
      line.computeLineDistances();
      line.renderOrder = 7;
      this.arcs.add(line);
      return line;
    };
    this.arcLines = {};
    for (const l of LAYERS.filter(isShell)) {
      const r = shellRadius(l), pts = [];
      for (let i = 0; i <= 96; i++) { const a = (Math.PI * i) / 96; pts.push(new THREE.Vector3(Math.cos(a) * r, Math.sin(a) * r, 0)); }
      this.arcLines[l] = lineOf(pts, new THREE.Color(LAYER_COLOURS[l]).multiplyScalar(0.6));
    }
    this.baseLine = lineOf([new THREE.Vector3(-outer, 0, 0), new THREE.Vector3(outer, 0, 0)], new THREE.Color(0x56605c));
    this.scene.add(this.arcs);
    this.applyAmount();
  }

  // Trails and label anchors of the model source on screen.
  use(key) {
    const set = this.sets?.[key];
    if (!set) return;
    const shown = this.trails?.visible ?? false;
    if (this.trails && this.trails !== set.trails) this.trails.visible = false;
    this.key = key;
    this.trails = set.trails;
    this.trails.visible = shown;
    this.anchors = set.anchors;
    this.onChange?.();
  }

  // Keep the shell outlines facing the camera.
  update(camera) {
    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
    right.y = 0;
    if (right.lengthSq() < 1e-6) return;
    right.normalize();
    this.right.copy(right);
    if (this.arcs) this.arcs.rotation.y = Math.atan2(-right.z, right.x);
  }

  // Where a layer's label sits in the current blend. Vertical: beside its
  // tier, toward the camera's right. Hemisphere: on its shell, along a ray
  // 50 degrees above the ground on the right; core layers at their centre.
  labelPosition(li) {
    const l = LAYERS[li], a = this.anchors[li];
    const vert = this.uniforms.uVert.value, rad = this.uniforms.uRad.value;
    const base = a.centre.clone();
    const v = base.clone().addScaledVector(this.right, 48);
    v.y = base.y + LIFT[l] + STRETCH * Math.max(base.y, 0) + (l === 'fittings' ? -9 : 5);
    let r;
    if (isShell(l)) {
      const R = shellRadius(l), e = THREE.MathUtils.degToRad(50);
      r = CENTRE.clone().addScaledVector(this.right, Math.cos(e) * R).add(new THREE.Vector3(0, Math.sin(e) * R, 0));
    } else {
      r = base.clone().add(pieceOffset(base, li, 0, 1)).addScaledVector(this.right, l === 'fittings' ? 34 : 50);
      r.y += l === 'fittings' ? -10 : 12;
    }
    return base.multiplyScalar(1 - vert - rad).addScaledVector(v, vert).addScaledVector(r, rad);
  }

  get amount() { return Math.max(this.uniforms.uVert.value, this.uniforms.uRad.value); }

  applyAmount() {
    const rad = this.uniforms.uRad.value;
    for (const g of this.glass) g.m.opacity = g.base + 0.2 * this.amount;
    if (this.arcs) {
      this.arcs.visible = rad > 0.02;
      const a = THREE.MathUtils.smoothstep(rad, 0.35, 1);
      for (const [l, line] of Object.entries(this.arcLines)) {
        line.material.opacity = 0.85 * a;
        line.visible = !this.hidden.has(l);
      }
      this.baseLine.material.opacity = 0.45 * a;
    }
  }

  async set(mode, tweens, ms = 1600) {
    this.mode = mode;
    const u = this.uniforms;
    const from = { v: u.uVert.value, r: u.uRad.value };
    const to = { v: mode === 'vertical' ? 1 : 0, r: mode === 'radial' ? 1 : 0 };
    if (this.trails) this.trails.visible = true;
    const done = await tweens.run('explode', ms, (t) => {
      u.uVert.value = from.v + (to.v - from.v) * t;
      u.uRad.value = from.r + (to.r - from.r) * t;
      this.applyAmount();
      this.onChange?.();
    });
    if (this.trails && mode === 'off' && this.mode === 'off') this.trails.visible = false;
    return done;
  }

  setLayerVisible(layer, on) {
    if (on) this.hidden.delete(layer); else this.hidden.add(layer);
    for (const m of this.layerGroups[layer] ?? []) m.visible = on;
    const hidden = LAYERS.map((l) => (this.hidden.has(l) ? 1 : 0));
    for (const set of Object.values(this.sets ?? {})) set.trails.material.uniforms.uHidden.value = hidden;
    this.applyAmount();
    this.onChange?.();
  }

  resetLayers() {
    for (const l of LAYERS) if (this.hidden.has(l)) this.setLayerVisible(l, true);
  }
}

function findLayer(o) {
  let p = o.parent;
  while (p) { if (p.name?.startsWith('LAYER_')) return p.name.slice(6); p = p.parent; }
  return null;
}
