import * as THREE from 'three';
import { lerp } from './tween.js';
import { createHatchMaterial, SECTION_POCHE, capGeometry, capLines } from './hatch.js';

// Registered floor tops and the heights the web view cuts each floor at
// (scripts/prepare_data.py writes the same values into sections.json).
export const FLOOR_Y = { LM1: -5.33, L00: 0, LP1: 4.86 };
export const CUTS = { LM1: -2.35, L00: 3.0, LP1: 7.95 };
export const FLOORS = ['LM1', 'L00', 'LP1'];
const TOP = 48, BOTTOM = -60;

// Exploded axonometric: each storey keeps its slab and walls up to its own
// cut; the slab-to-slab band above the cut (ceilings, plenum, next slab's
// underside) is left out so every storey reads as an open plan from above.
const EXPLODE = [
  { lo: BOTTOM, hi: CUTS.LM1, dy: 0 },
  { lo: -0.15, hi: CUTS.L00, dy: 13 },
  { lo: 4.55, hi: CUTS.LP1, dy: 27 },
  { lo: CUTS.LP1, hi: TOP, dy: 50 },
];
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
    this.caps = {};
    this.floorGroups = {};
    this.state = 'all';
    this.lamps = [];
    this.lampLevel = 0;
    this.glass = [];
    for (const f of FLOORS) {
      const g = new THREE.Group();
      g.name = `floor-${f}`;
      g.visible = false;
      scene.add(g);
      this.floorGroups[f] = g;
    }
  }

  attach(root) {
    const tuned = new Map();
    root.traverse((o) => {
      if (!o.isMesh) return;
      const m = o.material;
      if (!tuned.has(m)) tuned.set(m, tuneMaterial(m));
      o.material = tuned.get(m);
      o.castShadow = !o.material.userData.glass;
      o.receiveShadow = true;
    });
    for (let k = 0; k < 4; k++) {
      const lo = new THREE.Plane(new THREE.Vector3(0, 1, 0), -BOTTOM);
      const hi = new THREE.Plane(new THREE.Vector3(0, -1, 0), TOP);
      const planes = [lo, hi];
      const copy = k === 0 ? root : root.clone(true);
      const local = new Map();
      copy.traverse((o) => {
        if (!o.isMesh) return;
        const m = o.material;
        if (!local.has(m)) {
          const c = k === 0 ? m : m.clone();
          c.clippingPlanes = planes;
          c.clipShadows = true;
          c.userData = { ...m.userData };
          local.set(m, c);
          if (c.userData.lamp) this.lamps.push(c);
          if (c.userData.glass) this.glass.push(c);
        }
        o.material = local.get(m);
      });
      const group = new THREE.Group();
      group.name = `band-${k}`;
      group.add(copy);
      group.visible = k === 0;
      this.scene.add(group);
      this.bands.push({ group, lo, hi, s: { lo: BOTTOM, hi: TOP, dy: 0 } });
    }
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

  // Target band layout for a view state.
  layout(state) {
    if (state === 'explode') return EXPLODE.map((b) => ({ ...b, visible: true }));
    const hi = state === 'all' ? TOP : CUTS[state];
    return [{ lo: BOTTOM, hi, dy: 0, visible: true }, ...[1, 2, 3].map(() => ({ lo: BOTTOM, hi: TOP, dy: 0, visible: false }))];
  }

  // Animate from the current layout to `state`. Returns when the cut settles.
  async setState(state, tweens, ms = 900) {
    const from = this.bands.map((b) => ({ ...b.s, visible: b.group.visible }));
    const to = this.layout(state);
    const wasExplode = this.state === 'explode';
    this.state = state;
    this.moving = true;
    if (state === 'explode' && !wasExplode) {
      // storeys separate from where they stand: switch ranges, then lift
      to.forEach((b, k) => { this.bands[k].s = { lo: b.lo, hi: b.hi, dy: 0 }; this.bands[k].group.visible = true; });
      this.apply();
      await tweens.run('building', ms * 1.2, (t) => {
        to.forEach((b, k) => { this.bands[k].s.dy = lerp(0, b.dy, t); });
        this.apply();
      });
    } else if (wasExplode && state !== 'explode') {
      // settle back together, then cut
      await tweens.run('building', ms, (t) => {
        from.forEach((b, k) => { this.bands[k].s.dy = lerp(b.dy, 0, t); });
        this.apply();
      });
      if (this.state !== state) return;
      this.bands.forEach((b, k) => { b.s = { lo: BOTTOM, hi: k === 0 ? TOP : TOP, dy: 0 }; b.group.visible = k === 0; });
      const hi = to[0].hi;
      this.bands[0].s.hi = CUTS.LP1 + 0.5;
      await tweens.run('building', hi === TOP ? 500 : 350, (t) => {
        this.bands[0].s.hi = lerp(CUTS.LP1 + 0.5, hi, t);
        this.apply();
      });
    } else {
      const h0 = this.bands[0].s.hi, h1 = to[0].hi;
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
    this.bands[3].group.visible = this.state === 'explode' ? this.roofVisible !== false : this.bands[3].group.visible;
    this.bands.forEach((b, k) => {
      // clipping planes live in world space: they travel with the lift
      b.lo.constant = -(b.s.lo + b.s.dy);
      // taken apart by material, parts rise far above the roof
      b.hi.constant = k === 0 && this.unclipped ? 1e5 : b.s.hi + b.s.dy;
      b.group.position.y = b.s.dy;
    });
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
