import * as THREE from 'three';
import { FLOORS } from './building.js';

const FRAME = {
  kaiho: { color: 0xf3f1ec, depth: 0.045, border: 0.035 },
  vktrs: { color: 0x151515, depth: 0.05, border: 0.03 },
  forever: { color: 0xeeeae2, depth: 0.12, border: 0.0 },
};
const CELL = 170; // atlas cell, px

// Every placement from demo/data/artworks.json, drawn per floor with two
// instanced meshes (canvases sampling a thumbnail atlas, and frames), plus a
// few free-standing pieces. A focused room swaps in full-size images.
export class Artworks {
  constructor(building, rooms, base) {
    this.building = building;
    this.base = base;
    this.items = [];
    this.byId = new Map();
    this.layers = {};
    this.loader = new THREE.TextureLoader();
    this.full = new Map();
    this.highlight = null;
  }

  async init(data, roomsById) {
    this.items = data.artworks.map((a, i) => ({ ...a, floor: roomsById.get(a.room).floor, floorY: roomsById.get(a.room).y, order: i }));
    for (const a of this.items) this.byId.set(a.id, a);
    for (const f of FLOORS) this.layers[f] = this.buildFloor(f);
  }

  buildFloor(f) {
    const list = this.items.filter((a) => a.floor === f);
    const group = this.building.floorGroups[f];
    const walls = list.filter((a) => a.kind === 'wall');
    const free = list.filter((a) => a.kind !== 'wall');
    const layer = { floor: f, walls, free, built: false, group: new THREE.Group() };
    group.add(layer.group);
    // canvases: one instanced quad, uv window per instance into the atlas
    const cols = Math.ceil(Math.sqrt(Math.max(1, walls.length)));
    const size = cols * CELL;
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = Math.min(4096, THREE.MathUtils.ceilPowerOfTwo(size));
    layer.atlas = { canvas, cols, scale: CELL / canvas.width };
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#d9d4ca'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 4;
    texture.generateMipmaps = true;
    layer.texture = texture;
    const quad = new THREE.PlaneGeometry(1, 1);
    const uvRect = new Float32Array(walls.length * 4);
    walls.forEach((a, i) => {
      const cx = i % cols, cy = Math.floor(i / cols);
      uvRect.set([cx * layer.atlas.scale, 1 - (cy + 1) * layer.atlas.scale, layer.atlas.scale, layer.atlas.scale], i * 4);
    });
    quad.setAttribute('uvRect', new THREE.InstancedBufferAttribute(uvRect, 4));
    const canvasMaterial = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.82, metalness: 0 });
    canvasMaterial.onBeforeCompile = (shader) => {
      shader.vertexShader = shader.vertexShader
        .replace('#include <common>', '#include <common>\nattribute vec4 uvRect;')
        .replace('#include <uv_vertex>', '#include <uv_vertex>\n#ifdef USE_MAP\nvMapUv = uvRect.xy + uv * uvRect.zw;\n#endif');
    };
    const canvases = new THREE.InstancedMesh(quad, canvasMaterial, Math.max(1, walls.length));
    canvases.count = walls.length;
    const frames = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ roughness: 0.55 }), Math.max(1, walls.length));
    frames.count = walls.length;
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3();
    const color = new THREE.Color();
    walls.forEach((a, i) => {
      const fr = FRAME[a.exhibition];
      const n = new THREE.Vector3(...a.normal);
      q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
      p.set(...a.pos).addScaledVector(n, fr.depth + 0.004);
      s.set(a.w, a.h, 1);
      m.compose(p, q, s); canvases.setMatrixAt(i, m);
      p.set(...a.pos).addScaledVector(n, fr.depth / 2);
      s.set(a.w + fr.border * 2, a.h + fr.border * 2, fr.depth);
      m.compose(p, q, s); frames.setMatrixAt(i, m);
      frames.setColorAt(i, color.setHex(fr.color));
      a.anchor = new THREE.Vector3(...a.pos);
      a.normalV = n;
    });
    canvases.castShadow = frames.castShadow = true;
    canvases.receiveShadow = frames.receiveShadow = true;
    canvases.userData.artworks = walls;
    canvases.name = `canvases-${f}`;
    layer.canvases = canvases;
    layer.frames = frames;
    layer.group.add(canvases, frames);
    // free-standing pieces
    layer.pickables = [canvases];
    for (const a of free) {
      const obj = sculpture(a);
      obj.userData.artwork = a;
      a.anchor = new THREE.Vector3(...a.pos);
      layer.group.add(obj);
      obj.traverse((o) => { if (o.isMesh) { o.userData.artwork = a; layer.pickables.push(o); } });
    }
    // plan markers: a dot per work, read from above
    const dots = new THREE.InstancedMesh(new THREE.CircleGeometry(0.32, 20).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.85, depthTest: false }), Math.max(1, list.length));
    dots.count = list.length;
    list.forEach((a, i) => {
      const n = a.normal ? new THREE.Vector3(...a.normal) : new THREE.Vector3();
      p.set(a.pos[0], this.floorY(a) + 0.08, a.pos[2]).addScaledVector(n, 0.55);
      m.compose(p, new THREE.Quaternion(), new THREE.Vector3(1, 1, 1));
      dots.setMatrixAt(i, m);
    });
    dots.renderOrder = 6;
    dots.visible = false;
    dots.userData.artworks = list;
    layer.dots = dots;
    layer.group.add(dots);
    return layer;
  }

  floorY(a) { return a.floorY; }

  // Fill a floor's atlas with thumbnails the first time it is shown.
  async load(f, onProgress) {
    const layer = this.layers[f];
    if (!layer || layer.built) return;
    layer.built = true;
    const ctx = layer.atlas.canvas.getContext('2d');
    const px = layer.atlas.canvas.width * layer.atlas.scale;
    let done = 0;
    await Promise.all(layer.walls.map((a, i) => new Promise((resolve) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => {
        const cx = i % layer.atlas.cols, cy = Math.floor(i / layer.atlas.cols);
        ctx.drawImage(img, cx * px, cy * px, px, px);
        done++; onProgress?.(done / layer.walls.length);
        resolve();
      };
      img.onerror = resolve;
      img.src = `${this.base}art/${a.id}-s.webp`;
    })));
    layer.texture.needsUpdate = true;
  }

  // Full-size image as a separate quad in front of the atlas copy.
  async focusRoom(roomId) {
    for (const [id, mesh] of this.full) {
      if (mesh.userData.room !== roomId) { mesh.parent?.remove(mesh); mesh.material.map?.dispose(); mesh.material.dispose(); this.full.delete(id); }
    }
    const list = this.items.filter((a) => a.room === roomId && a.kind === 'wall');
    await Promise.all(list.map((a) => this.fullImage(a)));
  }

  async fullImage(a) {
    if (this.full.has(a.id)) return this.full.get(a.id);
    const map = await this.loader.loadAsync(`${this.base}art/${a.id}.webp`);
    map.colorSpace = THREE.SRGBColorSpace;
    map.anisotropy = 8;
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(a.w, a.h), new THREE.MeshStandardMaterial({ map, roughness: 0.8 }));
    const fr = FRAME[a.exhibition];
    mesh.position.copy(a.anchor).addScaledVector(a.normalV, fr.depth + 0.008);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), a.normalV);
    mesh.receiveShadow = true;
    mesh.userData.room = a.room;
    mesh.userData.artwork = a;
    this.layers[a.floor].group.add(mesh);
    this.full.set(a.id, mesh);
    return mesh;
  }

  setPlanMarkers(on) {
    for (const l of Object.values(this.layers)) l.dots.visible = on;
  }

  pick(raycaster, floors) {
    const objects = [];
    for (const f of floors) {
      const l = this.layers[f];
      if (!l || !l.group.parent?.visible) continue;
      objects.push(...l.pickables);
      if (l.dots.visible) objects.push(l.dots);
    }
    const hit = raycaster.intersectObjects(objects, false)[0];
    if (!hit) return null;
    if (hit.object.isInstancedMesh) return hit.object.userData.artworks[hit.instanceId] ?? null;
    return hit.object.userData.artwork ?? null;
  }

  // Where to stand to look at a work, in world space (explode offset applied).
  viewpoint(a) {
    const lift = this.building.lift(a.floor);
    const at = a.anchor.clone(); at.y += lift;
    const floorY = this.floorY(a) + lift;
    let eye;
    if (a.kind === 'wall') {
      const d = Math.max(3.4, Math.max(a.w, a.h) * 2.1);
      eye = at.clone().addScaledVector(a.normalV, d);
      eye.y = floorY + 1.6;
      at.y = Math.max(at.y, floorY + 1.45);
    } else {
      const d = Math.max(3.6, a.h * 2.4);
      const dir = new THREE.Vector3(Math.cos(a.seed), 0, Math.sin(a.seed));
      eye = at.clone().addScaledVector(dir, d);
      eye.y = floorY + 1.6;
    }
    return { eye, at };
  }
}

// A placeholder object for a free-standing work: plinth, vitrine or a
// standing form. Shapes and finishes are seeded per placement.
function sculpture(a) {
  const rnd = mulberry(a.seed);
  const g = new THREE.Group();
  const floorY = a.pos[1] - a.h / 2 - 0.25;
  g.position.set(a.pos[0], floorY, a.pos[2]);
  g.rotation.y = rnd() * Math.PI * 2;
  const white = new THREE.MeshStandardMaterial({ color: 0xefede8, roughness: 0.7 });
  const finishes = [
    new THREE.MeshStandardMaterial({ color: 0x8a6a3f, metalness: 0.85, roughness: 0.35 }),
    new THREE.MeshStandardMaterial({ color: 0xd8d4cc, roughness: 0.4 }),
    new THREE.MeshStandardMaterial({ color: [0xc8361f, 0x1f4aa0, 0xe2b31b, 0x161616][Math.floor(rnd() * 4)], roughness: 0.45 }),
    new THREE.MeshStandardMaterial({ color: 0x9aa3a6, metalness: 1, roughness: 0.18 }),
  ];
  const finish = finishes[Math.floor(rnd() * finishes.length)];
  const shapes = [
    () => new THREE.TorusKnotGeometry(0.28, 0.08, 96, 12, 2 + Math.floor(rnd() * 3), 3),
    () => new THREE.IcosahedronGeometry(0.34, 0),
    () => new THREE.TorusGeometry(0.32, 0.07, 16, 48),
    () => new THREE.CylinderGeometry(0.05, 0.22, 0.8, 5),
    () => new THREE.SphereGeometry(0.3, 32, 16),
    () => new THREE.BoxGeometry(0.3, 0.6, 0.3),
  ];
  if (a.kind === 'plinth' || a.kind === 'vitrine') {
    const w = Math.min(1.2, a.w * 0.6), ph = 0.9;
    const plinth = new THREE.Mesh(new THREE.BoxGeometry(w, ph, w), white);
    plinth.position.y = ph / 2;
    g.add(plinth);
    const obj = new THREE.Mesh(shapes[Math.floor(rnd() * shapes.length)](), finish);
    obj.position.y = ph + 0.38;
    obj.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3);
    g.add(obj);
    if (a.kind === 'vitrine') {
      const glass = new THREE.Mesh(new THREE.BoxGeometry(w * 0.96, 0.85, w * 0.96), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.16, roughness: 0.05, depthWrite: false }));
      glass.position.y = ph + 0.43;
      glass.castShadow = false;
      g.add(glass);
    }
  } else {
    const kind = Math.floor(rnd() * 3);
    if (kind === 0) {
      // stacked blocks
      let y = 0;
      for (let i = 0; i < 3 + Math.floor(rnd() * 4); i++) {
        const s = 0.35 + rnd() * 0.5, h = 0.2 + rnd() * 0.45;
        const b = new THREE.Mesh(new THREE.BoxGeometry(s, h, s * (0.6 + rnd() * 0.6)), i % 2 ? finish : white);
        b.position.y = y + h / 2; b.rotation.y = rnd() * 0.6; y += h; g.add(b);
      }
    } else if (kind === 1) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(a.h * 0.42, 0.06, 16, 64), finish);
      ring.position.y = a.h * 0.45 + 0.08;
      g.add(ring);
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.3), finish);
      base.position.y = 0.04; g.add(base);
    } else {
      // suspended-looking veil of thin rods
      for (let i = 0; i < 26; i++) {
        const h = a.h * (0.5 + rnd() * 0.5);
        const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, h, 6), finish);
        const r = 0.35 + rnd() * 0.25, t = (i / 26) * Math.PI * 2;
        rod.position.set(Math.cos(t) * r, h / 2, Math.sin(t) * r);
        g.add(rod);
      }
    }
  }
  g.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  return g;
}

function mulberry(seed) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}
