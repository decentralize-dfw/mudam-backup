import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// The plateau around the museum: a site-plan drawing on the ground (roads,
// paths, parks and walls from the OSM extract) and pale extruded massing for
// the neighbouring buildings. Massing heights are OSM tags or storey counts;
// it is context, not a survey.
export class Context {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'context';
    scene.add(this.group);
  }

  async init(base, data, ground) {
    const tex = await new THREE.TextureLoader().loadAsync(`${base}context/ground.webp`);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    const R = ground.radius;
    // the drawing, with the museum footprint and the sunken moats cut out
    const outline = new THREE.Shape();
    for (let i = 0; i <= 96; i++) { const a = (i / 96) * Math.PI * 2; const p = [Math.cos(a) * R, Math.sin(a) * R]; i ? outline.lineTo(...p) : outline.moveTo(...p); }
    for (const hole of ground.holes ?? []) outline.holes.push(new THREE.Path(hole.map(([x, z]) => new THREE.Vector2(x, -z))));
    const geo = new THREE.ShapeGeometry(outline, 2).rotateX(-Math.PI / 2);
    const disc = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.96, metalness: 0 }));
    // texture u runs with +x, v with +z (top row = -R)
    const uv = disc.geometry.attributes.uv;
    const pos = disc.geometry.attributes.position;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, (pos.getX(i) + R) / (2 * R), 1 - (pos.getZ(i) + R) / (2 * R));
    disc.position.y = -0.45;
    disc.receiveShadow = true;
    disc.name = 'ground';
    this.ground = disc;
    // fade the drawing out at its edge into the background
    disc.material.onBeforeCompile = (shader) => {
      shader.uniforms.uR = { value: R };
      shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vGround;')
        .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvGround = (modelMatrix * vec4(transformed,1.0)).xz;');
      shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec2 vGround; uniform float uR;')
        .replace('#include <dithering_fragment>', '#include <dithering_fragment>\nfloat edge = smoothstep(uR*0.97, uR*0.55, length(vGround));\ngl_FragColor.a *= edge;');
      disc.material.userData.shader = shader;
    };
    disc.material.transparent = true;
    disc.material.depthWrite = true;
    this.group.add(disc);

    const geos = [];
    for (const b of data.buildings) {
      const pts = [];
      for (let i = 0; i < b.p.length; i += 2) pts.push(new THREE.Vector2(b.p[i], -b.p[i + 1]));
      const shape = new THREE.Shape(pts);
      const g = new THREE.ExtrudeGeometry(shape, { depth: b.h, bevelEnabled: false });
      g.rotateX(-Math.PI / 2);
      g.translate(0, -0.3, 0);
      geos.push(g);
    }
    if (geos.length) {
      const merged = mergeGeometries(geos.map((g) => { g.deleteAttribute('uv'); return g; }));
      merged.computeVertexNormals();
      this.massing = new THREE.Mesh(merged, new THREE.MeshStandardMaterial({ color: 0xece8df, roughness: 0.9 }));
      this.massing.castShadow = this.massing.receiveShadow = true;
      this.massing.name = 'context-massing';
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(merged, 30), new THREE.LineBasicMaterial({ color: 0x8f8a80, transparent: true, opacity: 0.55 }));
      this.edges = edges;
      this.group.add(this.massing, edges);
    }
  }

  // Light canopies for the forecourt trees, from the source foliage volumes.
  addCanopies(trees) {
    const geos = [];
    const rnd = (i) => { const x = Math.sin(i * 127.1) * 43758.5453; return x - Math.floor(x); };
    const tones = [0x6b7a35, 0x8a8a32, 0xa9822f, 0x56693a, 0x93702c].map((c) => new THREE.Color(c).convertSRGBToLinear());
    const needle = [0x2f4a2c, 0x3b5631, 0x34502f].map((c) => new THREE.Color(c).convertSRGBToLinear());
    trees.forEach((t, k) => {
      const [cx, cy, cz] = t.c, [sx, sy, sz] = t.s;
      if (t.kind === 'needle') {
        // pines on the forecourt: stacked cones inside the source needle volume
        const tiers = 3;
        for (let j = 0; j < tiers; j++) {
          const f = j / tiers;
          const r = Math.max(sx, sz) * (1 - 0.28 * j) * (0.92 + 0.12 * rnd(k * 7 + j));
          const h = sy * 2 * 0.52;
          const g = new THREE.ConeGeometry(r, h, 9, 1).toNonIndexed();
          g.rotateY(rnd(k + j) * Math.PI);
          g.translate(cx + (rnd(k * 3 + j) - 0.5) * 0.4, cy - sy + h / 2 + f * sy * 0.95, cz + (rnd(k * 5 + j) - 0.5) * 0.4);
          const c = needle[(k + j) % needle.length];
          const col = new Float32Array(g.attributes.position.count * 3);
          for (let i = 0; i < g.attributes.position.count; i++) col.set([c.r, c.g, c.b], i * 3);
          g.setAttribute('color', new THREE.BufferAttribute(col, 3));
          g.deleteAttribute('uv');
          geos.push(g);
        }
        return;
      }
      for (let j = 0; j < 5; j++) {
        const g = new THREE.IcosahedronGeometry(1, 1);
        const p = g.attributes.position;
        for (let i = 0; i < p.count; i++) {
          const n = 0.82 + 0.3 * rnd(k * 97 + j * 13 + i);
          p.setXYZ(i, p.getX(i) * n, p.getY(i) * n, p.getZ(i) * n);
        }
        const r = 0.55 + 0.2 * rnd(k + j * 7);
        g.scale(sx * r, sy * r * 0.9, sz * r);
        g.translate(cx + (rnd(k * 3 + j) - 0.5) * sx * 0.9, cy + (rnd(k * 5 + j) - 0.3) * sy * 0.6, cz + (rnd(k * 11 + j) - 0.5) * sz * 0.9);
        const c = tones[(k + j) % tones.length];
        const col = new Float32Array(p.count * 3);
        for (let i = 0; i < p.count; i++) col.set([c.r, c.g, c.b], i * 3);
        g.setAttribute('color', new THREE.BufferAttribute(col, 3));
        g.deleteAttribute('uv');
        geos.push(g);
      }
    });
    const merged = mergeGeometries(geos);
    merged.computeVertexNormals();
    const mesh = new THREE.Mesh(merged, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, flatShading: true }));
    mesh.castShadow = mesh.receiveShadow = true;
    mesh.name = 'canopies';
    return mesh;
  }

  setMassing(level) {
    this.massingLevel = level;
    this.applyMassing();
  }

  applyMassing() {
    if (!this.massing) return;
    const level = (this.massingLevel ?? 1) * (this.massingFade ?? 1);
    this.massing.visible = this.edges.visible = level > 0.001;
    this.massing.material.opacity = level;
    const transparent = level < 1;
    if (this.massing.material.transparent !== transparent) { this.massing.material.transparent = transparent; this.massing.material.needsUpdate = true; }
    this.massing.material.depthWrite = level > 0.5;
    this.edges.material.opacity = 0.55 * level;
  }
}
