import * as THREE from 'three';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { hatchWire } from './hatch.js';

// Line drawing for the exploded views: white edges on black, hidden lines
// removed (no x-ray). Surfaces stay in the depth buffer but fade to black, so
// they hide what is behind them; their feature edges are drawn on top in
// white. Building lines carry the same shader as their parts (band range,
// material offset), so they follow every cut and explosion. The surroundings
// draw their lines at 20 %, and thinner. uWire fades the whole drawing in and
// out. While it shows, the scene is drawn at twice the resolution and scaled
// down (pipeline.setScale): the building's one-pixel lines become half a
// pixel, and the surroundings' (screen-space lines, CONTEXT_WIDTH) thinner
// still.
const WHITE = new THREE.Color(1, 1, 1);
const BLACK = new THREE.Color(0, 0, 0);
const BUILDING_ANGLE = Math.cos(THREE.MathUtils.degToRad(35));
const CONTEXT_ANGLE = Math.cos(THREE.MathUtils.degToRad(45));
export const CONTEXT_LINES = 0.2;
// Lines blend in linear light: an alpha of 0.2 reads as a grey near half
// brightness. The surroundings get the alpha that reads as 20 %.
const CONTEXT_ALPHA = THREE.MathUtils.clamp(Math.pow(CONTEXT_LINES, 2.2), 0, 1);
// CSS pixels (LineSegments2 sizes its lines against the canvas): under the
// building's lines, which are one pixel of the doubled drawing (0.5)
const CONTEXT_WIDTH = 0.35;
const SUPERSAMPLE = 2;

export class WireMode {
  constructor(stage) {
    this.stage = stage;
    this.uWire = hatchWire;
    this.lines = [];          // every line object, shown only while uWire > 0
    this.lineMaterials = [];  // [material, full opacity]
    this.tinted = [];         // [material, colour in normal mode] lerped to white
    this.replaced = [];       // original lines that the white copies replace
    this.patched = new WeakSet();
    this.done = new WeakSet(); // roots whose lines exist (or are being made)
    this.cache = new Map();   // geometry uuid -> Promise<edge index>
    this.jobs = new Map();
    this.nextJob = 0;
    this.context = new LineMaterial({ color: WHITE, linewidth: CONTEXT_WIDTH, transparent: true, opacity: 0, depthWrite: false });
    this.lineMaterials.push([this.context, CONTEXT_ALPHA]);
    // fills fade to black in the building's own shaders
    stage.building.addHook((shader, material, kind) => this.fillHook(shader, material, kind));
  }

  get amount() { return this.uWire.value; }

  worker() {
    if (!this.w) {
      this.w = new Worker(new URL('./edges.worker.js', import.meta.url), { type: 'module' });
      this.w.onmessage = (e) => { const job = this.jobs.get(e.data.id); this.jobs.delete(e.data.id); job?.(e.data.edges); };
    }
    return this.w;
  }

  // Feature-edge index of a geometry (shared by every mesh that uses it).
  edges(geometry, cos) {
    let p = this.cache.get(geometry.uuid);
    if (p) return p;
    const pos = geometry.attributes.position.array.slice();
    const index = geometry.index ? new Uint32Array(geometry.index.array) : null;
    const piece = geometry.attributes._piece ? geometry.attributes._piece.array.slice() : null;
    const id = this.nextJob++;
    p = new Promise((resolve) => { this.jobs.set(id, resolve); });
    this.worker().postMessage({ id, pos, index, piece, cos }, [pos.buffer, ...(index ? [index.buffer] : []), ...(piece ? [piece.buffer] : [])]);
    this.cache.set(geometry.uuid, p);
    return p;
  }

  lineGeometry(geometry, edges) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', geometry.attributes.position);
    if (geometry.attributes._piece) g.setAttribute('_piece', geometry.attributes._piece);
    g.setIndex(new THREE.BufferAttribute(edges, 1));
    return g;
  }

  addLines(mesh, line) {
    line.frustumCulled = false;
    line.visible = this.amount > 0;
    line.renderOrder = 1;
    line.userData.wire = true;
    mesh.add(line);
    this.lines.push(line);
    this.stage.dirty = true;
  }

  // Building colour materials: darker with uWire, glass clears; plus a small
  // depth bias so the edges drawn on a face win against the face itself.
  fillHook(shader, material, kind) {
    if (kind !== 'band') return;
    shader.uniforms.uWire = this.uWire;
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uWire;')
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>\ngl_FragColor.rgb *= 1.0 - uWire;${material.transparent ? '\ngl_FragColor.a *= 1.0 - uWire;' : ''}`);
    material.polygonOffset = true;
    material.polygonOffsetFactor = 1;
    material.polygonOffsetUnits = 1;
  }

  // Any other material (surroundings, artworks, rooms): fade to black.
  patchFill(material) {
    if (this.patched.has(material) || material.isLineBasicMaterial || material.isShaderMaterial) return;
    this.patched.add(material);
    const prev = material.onBeforeCompile;
    // taken now (by default the source of the material's own onBeforeCompile):
    // materials with different edits must not share a program
    const base = material.customProgramCacheKey();
    material.onBeforeCompile = (shader, renderer) => {
      prev?.call(material, shader, renderer);
      shader.uniforms.uWire = this.uWire;
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform float uWire;')
        .replace('#include <dithering_fragment>', `#include <dithering_fragment>\ngl_FragColor.rgb *= 1.0 - uWire;${material.transparent && material.userData.glass ? '\ngl_FragColor.a *= 1.0 - uWire;' : ''}`);
    };
    material.customProgramCacheKey = () => `wire|${base}`;
    material.polygonOffset = true;
    material.polygonOffsetFactor = 1;
    material.polygonOffsetUnits = 1;
    material.needsUpdate = true;
  }

  // Lines for one model source's four bands.
  async buildBuilding(bands) {
    if (this.done.has(bands)) return;
    this.done.add(bands);
    for (const band of bands) {
      if (!band.line) {
        band.line = new THREE.LineBasicMaterial({ color: WHITE, transparent: true, opacity: 0, depthWrite: false });
        this.stage.building.patch(band.line, band, 'line');
        this.lineMaterials.push([band.line, 1]);
      }
    }
    const meshes = [];
    bands[0].group.traverse((o) => { if (o.isMesh && !o.userData.wire) meshes.push(o); });
    for (const m of meshes) {
      const edges = await this.edges(m.geometry, BUILDING_ANGLE);
      if (!edges.length) continue;
      const g = this.lineGeometry(m.geometry, edges);
      // the same mesh in each band (clones share the geometry)
      for (const band of bands) {
        band.group.traverse((o) => {
          if (o.isMesh && o.geometry === m.geometry && !o.children.some((c) => c.userData.wire)) this.addLines(o, new THREE.LineSegments(g, band.line));
        });
      }
    }
  }

  // Lines and black fills for surroundings, artworks, caps and arrows.
  async buildRoot(root, { lines = true, cos = CONTEXT_ANGLE, material = this.context } = {}) {
    if (!root || this.done.has(root)) return;
    this.done.add(root);
    const meshes = [];
    root.traverse((o) => {
      if (!o.isMesh || o.userData.wire) return;
      for (const m of Array.isArray(o.material) ? o.material : [o.material]) this.patchFill(m);
      meshes.push(o);
    });
    if (!lines) return;
    for (const m of meshes) {
      if (m.isInstancedMesh) { this.instancedLines(m, material); continue; }
      const edges = await this.edges(m.geometry, cos);
      if (!edges.length) continue;
      if (material === this.context) {
        const p = m.geometry.attributes.position, seg = new Float32Array(edges.length * 3);
        for (let i = 0; i < edges.length; i++) { seg[i * 3] = p.getX(edges[i]); seg[i * 3 + 1] = p.getY(edges[i]); seg[i * 3 + 2] = p.getZ(edges[i]); }
        this.addLines(m, this.thin(seg));
      } else this.addLines(m, new THREE.LineSegments(this.lineGeometry(m.geometry, edges), material));
    }
  }

  // Thin lines for the surroundings: segment end points, pairwise.
  thin(positions) {
    return new LineSegments2(new LineSegmentsGeometry().setPositions(positions), this.context);
  }

  // One line set for all instances of an instanced mesh (picture frames).
  instancedLines(mesh, material) {
    const e = new THREE.EdgesGeometry(mesh.geometry, 30).attributes.position.array;
    const out = new Float32Array(e.length * mesh.count);
    const m = new THREE.Matrix4(), v = new THREE.Vector3();
    for (let i = 0; i < mesh.count; i++) {
      mesh.getMatrixAt(i, m);
      for (let k = 0; k < e.length; k += 3) {
        v.set(e[k], e[k + 1], e[k + 2]).applyMatrix4(m);
        out.set([v.x, v.y, v.z], i * e.length + k);
      }
    }
    if (material === this.context) { this.addLines(mesh, this.thin(out)); return; }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(out, 3));
    this.addLines(mesh, new THREE.LineSegments(g, material));
  }

  // A line object made elsewhere (massing edges, cap outlines) joins in white.
  addExisting(line, opacity = 1) {
    const l = opacity === 1 ? new THREE.LineSegments(line.geometry, this.full ??= this.makeFull()) : this.thin(line.geometry.attributes.position.array);
    l.position.copy(line.position);
    this.addLines(line.parent, l);
    this.replaced.push(line);
  }

  makeFull() {
    const m = new THREE.LineBasicMaterial({ color: WHITE, transparent: true, opacity: 0, depthWrite: false });
    this.lineMaterials.push([m, 1]);
    return m;
  }

  // Materials that should turn white (arrows, guide arcs).
  tint(material) {
    if (!this.tinted.some(([m]) => m === material)) this.tinted.push([material, material.color.clone()]);
  }

  // Background, line opacity, tints for the current uWire.
  apply() {
    const u = this.uWire.value;
    const st0 = this.stage;
    st0.pipeline.setScale(u > 0.001 ? SUPERSAMPLE : 1);
    for (const l of this.lines) l.visible = u > 0.001;
    // the originals (grey massing edges, dark cap outlines) give way
    for (const l of this.replaced) l.material.visible = u < 0.5;
    for (const [m, o] of this.lineMaterials) m.opacity = o * u;
    for (const [m, base] of this.tinted) m.color.copy(base).lerp(WHITE, u);
    const st = this.stage;
    if (u > 0.001 || this.wasOn) {
      const base = st.daylight.backgroundColor(new THREE.Color());
      st.scene.background = base.lerp(BLACK, u);
    }
    this.wasOn = u > 0.001;
    st.pipeline.aoOff = u > 0.5;
    st.renderer.shadowMap.needsUpdate = true;
    st.dirty = true;
  }

  async set(on, ms = 700) {
    const from = this.uWire.value, to = on ? 1 : 0;
    return this.stage.tweens.run('wire', ms, (t) => {
      this.uWire.value = from + (to - from) * t;
      this.apply();
    });
  }
}
