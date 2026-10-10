import * as THREE from 'three';
import { lerp } from './tween.js';
import { createHatchMaterial, SECTION_POCHE, capGeometry, capLines } from './hatch.js';

// Registered floor tops and the heights the web view cuts each floor at
// (scripts/prepare_data.py writes the same values into sections.json).
export const FLOOR_Y = { LM1: -5.33, L00: 0, LP1: 4.86 };
export const CUTS = { LM1: -2.35, L00: 3.0, LP1: 7.95 };
export const FLOORS = ['LM1', 'L00', 'LP1'];
const TOP = 48, BOTTOM = -60;

// The building is drawn as four bands, one per storey and the roof. A band
// shows the parts whose ORIGINAL height (before the band is lifted and before
// any material view moves them) lies in its range; the test runs per pixel in
// the materials' shaders. So bands can carry their parts anywhere, lifted with
// a storey or flown out by layer, without being cut, and floors and materials
// can come apart at the same time.
//
// PARTITION: four ranges that meet; together they are the whole building.
const PARTITION = [
  { lo: BOTTOM, hi: -0.15 },
  { lo: -0.15, hi: 4.55 },
  { lo: 4.55, hi: CUTS.LP1 },
  { lo: CUTS.LP1, hi: TOP },
];
// Exploded axonometric: each storey keeps its slab and walls up to its own
// cut; the slab-to-slab band above the cut (ceilings, plenum, next slab's
// underside) is left out so every storey reads as an open plan from above.
const EXPLODE = [
  { lo: BOTTOM, hi: CUTS.LM1, dy: 0 },
  { lo: -0.15, hi: CUTS.L00, dy: 36 },
  { lo: 4.55, hi: CUTS.LP1, dy: 74 },
  { lo: CUTS.LP1, hi: TOP, dy: 116 },
];
// the whole building, or cut at height h, as the four bands
const clamped = (h) => PARTITION.map((p) => ({ lo: p.lo, hi: Math.max(p.lo, Math.min(p.hi, h)), dy: 0 }));
export const FLOOR_BAND = { LM1: 0, L00: 1, LP1: 2 };

const GLASS = /GLASS|GLAZING/i;
const LAMP = /DIFFUSER|LUMINOUS|_LENS/i;

export function tuneMaterial(material) {
  if (GLASS.test(material.name) || material.transmission > 0) {
    const glass = new THREE.MeshPhysicalMaterial({
      name: material.name,
      color: new THREE.Color(0xdbe6e6),
      metalness: 0,
      roughness: 0.05,
      transparent: true,
      opacity: 0.2,
      envMapIntensity: 1.6,
      specularIntensity: 1,
      ior: 1.5,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
    glass.userData.glass = true;
    return glass;
  }
  material.side = THREE.DoubleSide;
  material.shadowSide = THREE.DoubleSide;
  if (material.map) material.map.anisotropy = 8;
  if (LAMP.test(material.name)) {
    material.userData.lamp = true;
    material.emissive = new THREE.Color(1, 0.86, 0.68);
    material.emissiveIntensity = 0;
  }
  return material;
}

export class Building {
  constructor(scene, renderer) {
    this.scene = scene;
    this.renderer = renderer;
    this.bands = [];
    // one set of bands per model source (Çevre 1, Çevre 2); `bands` is the
    // one on screen
    this.sources = {};
    this.source = 1;
    this.caps = {};
    this.floorGroups = {};
    this.state = 'all';
    this.lamps = [];
    this.lampLevel = 0;
    // extra shader code for every building material (the material views)
    this.hooks = [];
    this.glass = [];
    for (const f of FLOORS) {
      const g = new THREE.Group();
      g.name = `floor-${f}`;
      g.visible = false;
      scene.add(g);
      this.floorGroups[f] = g;
    }
  }

  attach(root, key = 1) {
    const tuned = new Map();
    root.traverse((o) => {
      if (!o.isMesh) return;
      const m = o.material;
      if (!tuned.has(m)) tuned.set(m, tuneMaterial(m));
      o.material = tuned.get(m);
      o.castShadow = !o.material.userData.glass;
      o.receiveShadow = true;
    });
    const bands = [];
    for (let k = 0; k < 4; k++) {
      const band = { uniforms: { uBandLo: { value: BOTTOM }, uBandHi: { value: TOP }, uBandDy: { value: 0 } }, s: { lo: BOTTOM, hi: TOP, dy: 0 } };
      // shadows: the same range test in the depth pass
      band.depth = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });
      this.patch(band.depth, band, 'depth');
      const copy = k === 0 ? root : root.clone(true);
      const local = new Map();
      copy.traverse((o) => {
        if (!o.isMesh) return;
        o.customDepthMaterial = band.depth;
        // parts leave their bounding volumes in the exploded views
        o.frustumCulled = false;
        const m = o.material;
        if (!local.has(m)) {
          const c = k === 0 ? m : m.clone();
          c.userData = { ...m.userData };
          this.patch(c, band, 'band');
          local.set(m, c);
          if (c.userData.lamp) this.lamps.push(c);
          if (c.userData.glass) this.glass.push(c);
        }
        o.material = local.get(m);
      });
      band.materials = [...local.values(), band.depth];
      band.group = new THREE.Group();
      band.group.name = `band-${key}-${k}`;
      band.group.add(copy);
      band.group.visible = k === 0 && key === this.source;
      this.scene.add(band.group);
      bands.push(band);
    }
    this.sources[key] = bands;
    if (key === this.source) { this.bands = bands; this.apply(); }
    return bands;
  }

  // Band range test (and the hooks) in a material's shaders.
  patch(material, band, kind) {
    const prev = material.onBeforeCompile;
    material.onBeforeCompile = (shader, renderer) => {
      prev?.call(material, shader, renderer);
      Object.assign(shader.uniforms, band.uniforms);
      for (const hook of this.hooks) hook(shader, material, kind);
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nuniform float uBandDy;\nvarying float vBandY;')
        // height before the band's lift and before the hooks move the part
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvBandY = (modelMatrix * vec4(transformed, 1.0)).y - uBandDy;');
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uBandLo;\nuniform float uBandHi;\nvarying float vBandY;')
        .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\nif (vBandY < uBandLo || vBandY > uBandHi) discard;');
    };
    material.customProgramCacheKey = () => `mudam-${kind}-${this.hooks.length}`;
    material.needsUpdate = true;
  }

  // Add shader code to every building material, e.g. the material views.
  addHook(hook) {
    this.hooks.push(hook);
    for (const bands of Object.values(this.sources)) for (const b of bands) for (const m of b.materials) m.needsUpdate = true;
  }

  // Show the other model source in the same state (cut, lift, visibility).
  useSource(key) {
    const next = this.sources[key];
    if (!next || next === this.bands) return;
    this.bands.forEach((b, k) => {
      next[k].s = { ...b.s };
      next[k].group.visible = b.group.visible;
      b.group.visible = false;
    });
    this.bands = next;
    this.source = key;
    this.apply();
  }

  attachSections(data) {
    const material = createHatchMaterial(SECTION_POCHE);
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x15140f });
    for (const cut of data.cuts) {
      const group = new THREE.Group();
      group.name = `cap-${cut.id}`;
      const mesh = new THREE.Mesh(capGeometry(cut), material);
      mesh.renderOrder = 2;
      const lines = new THREE.LineSegments(capLines(cut), lineMaterial);
      lines.position.y = 0.004;
      lines.renderOrder = 3;
      group.add(mesh, lines);
      group.visible = false;
      this.scene.add(group);
      this.caps[cut.id] = { group, y: cut.y };
    }
  }

  // Cut height of a view state (TOP: the whole building).
  cutOf(state) { return state === 'all' || state === 'explode' ? TOP : CUTS[state]; }

  // One band showing everything up to h: the resting form of every state but
  // 'explode'. It looks exactly like clamped(h), so the two swap unseen.
  compact(h) {
    this.bands.forEach((b, k) => { b.s = { lo: BOTTOM, hi: k === 0 ? h : TOP, dy: 0 }; b.group.visible = k === 0; });
  }

  // Animate from the current layout to `state`. Returns when it settles.
  async setState(state, tweens, ms = 900) {
    const wasExplode = this.state === 'explode';
    const h0 = wasExplode ? TOP : this.bands[0].s.hi;
    this.state = state;
    this.moving = true;
    if (state === 'explode' && !wasExplode) {
      // the building as four bands that meet (unchanged on screen), then each
      // storey lifts and narrows to its open plan
      const from = clamped(h0), to = EXPLODE;
      this.bands.forEach((b, k) => { b.s = { ...from[k] }; b.group.visible = true; });
      this.apply();
      await tweens.run('building', ms * 1.4, (t) => {
        this.bands.forEach((b, k) => { for (const f of ['lo', 'hi', 'dy']) b.s[f] = lerp(from[k][f], to[k][f], t); });
        this.apply();
      });
    } else if (wasExplode && state !== 'explode') {
      // storeys settle and close up into the whole building (or its cut)
      const from = this.bands.map((b) => ({ ...b.s })), to = clamped(this.cutOf(state));
      this.bands.forEach((b) => { b.group.visible = true; });
      await tweens.run('building', ms * 1.2, (t) => {
        this.bands.forEach((b, k) => { for (const f of ['lo', 'hi', 'dy']) b.s[f] = lerp(from[k][f], to[k][f], t); });
        this.apply();
      });
      if (this.state !== state) return;
      this.compact(this.cutOf(state));
    } else if (state !== 'explode') {
      // one cut to another: a single plane sweeps (from the building's top,
      // not from TOP, so it starts moving at once)
      this.compact(h0);
      const h1 = this.cutOf(state);
      const a = Math.min(h0, TOP - 14), b = Math.min(h1, TOP - 14);
      await tweens.run('building', ms, (t) => {
        // the visible range of the cut is the building's height, not TOP
        let h = lerp(a, b, t);
        if (t >= 1) h = h1; else if (h0 >= TOP && t < 0.02) h = h0;
        this.bands[0].s.hi = h;
        this.apply();
      });
    }
    if (this.state === state) { this.moving = false; this.apply(); }
  }

  apply() {
    if (this.state === 'explode' && this.roofVisible === false) this.bands[3].group.visible = false;
    for (const b of this.bands) {
      b.uniforms.uBandLo.value = b.s.lo;
      b.uniforms.uBandHi.value = b.s.hi;
      b.uniforms.uBandDy.value = b.s.dy;
      b.group.position.y = b.s.dy;
    }
    // a cap shows on whichever visible band currently ends at that floor's cut
    for (const [f, cap] of Object.entries(this.caps)) {
      const band = this.bands.find((b) => b.group.visible && Math.abs(b.s.hi - cap.y) < 0.02);
      cap.group.visible = Boolean(band) && !this.moving;
      if (band) cap.group.position.y = cap.y + band.s.dy + 0.003;
    }
    for (const f of FLOORS) {
      const g = this.floorGroups[f];
      const explode = this.state === 'explode';
      g.visible = explode || this.state === f || this.visitFloor === f;
      g.position.y = explode ? this.bands[FLOOR_BAND[f]].s.dy : 0;
    }
    this.renderer.shadowMap.needsUpdate = true;
    this.onChange?.();
  }

  // Offset applied to a point on floor f in the current layout.
  lift(f) {
    return this.state === 'explode' ? this.bands[FLOOR_BAND[f]].s.dy : 0;
  }

  setLamps(level) {
    this.lampLevel = level;
    for (const m of this.lamps) m.emissiveIntensity = level * 2.2;
  }
}
