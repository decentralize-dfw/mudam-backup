// Mudam web model, two sets:
//
//   node scripts/build-model.mjs
//     Çevre 1: 12_Blender_Model/exports/current.glb.gz -> demo/model/{building,site,trees}.glb
//   node scripts/build-model.mjs --cevre2 [dir]
//     Çevre 2: 12_Blender_Model/exports/web_current/{building,near_context,far_context}.glb.gz
//     (R151 web clean, see 12_Blender_Model/config/r151_web_lod.json)
//     -> demo/model/cevre2/*.glb, demo/data/pieces-cevre2.json, demo/data/cevre2.json
//
// The Blender export carries 8 477 loose root nodes, each with its own mesh,
// so the browser would issue thousands of draw calls. Here every node is
// sorted into a chunk (building, site ground, trees), the chunk is joined per
// material, the heavy decorative parts are simplified, textures become WebP
// and geometry is Draco-compressed. Node identity is not needed at runtime:
// rooms, hotspots and section caps come from demo/data/*.json, derived from
// the same source by scripts/prepare_data.py.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { NodeIO, getBounds } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, join, weld, weldPrimitive, draco, textureCompress, simplify, simplifyPrimitive, flatten } from '@gltf-transform/functions';
import { MeshoptSimplifier, MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';
import draco3d from 'draco3dgltf';
import sharp from 'sharp';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const args = process.argv.slice(2);
const CEVRE2 = args.includes('--cevre2');
const R151 = path.resolve(args.find((a) => !a.startsWith('--')) ?? path.join(repo, '12_Blender_Model/exports/web_current'));
const outDir = path.join(repo, CEVRE2 ? 'demo/model/cevre2' : 'demo/model');
const dataDir = path.join(repo, 'demo/data');
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(dataDir, { recursive: true });

await MeshoptDecoder.ready;
await MeshoptEncoder.ready;
const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({
    'draco3d.decoder': await draco3d.createDecoderModule(),
    'draco3d.encoder': await draco3d.createEncoderModule(),
    'meshopt.decoder': MeshoptDecoder,
    'meshopt.encoder': MeshoptEncoder,
  });

async function readDoc(file) {
  const bytes = fs.readFileSync(file);
  return io.readBinary(new Uint8Array(file.endsWith('.gz') ? zlib.gunzipSync(bytes) : bytes));
}

function stats(doc) {
  const root = doc.getRoot();
  let tris = 0;
  for (const m of root.listMeshes()) for (const p of m.listPrimitives()) tris += (p.getIndices()?.getCount() ?? p.getAttribute('POSITION').getCount()) / 3;
  const prims = root.listMeshes().reduce((n, m) => n + m.listPrimitives().length, 0);
  const scene = root.getDefaultScene() ?? root.listScenes()[0];
  const b = scene ? getBounds(scene) : null;
  return { prims, tris: Math.round(tris), textures: root.listTextures().length, bounds: b && { min: b.min.map((v) => Math.round(v * 10) / 10), max: b.max.map((v) => Math.round(v * 10) / 10) } };
}

await MeshoptSimplifier.ready;

// Which chunk a source node belongs to. Site context (moat, park, approach)
// and the trees are separate files so the building can appear first.
function chunkOf(name, extras) {
  const level = extras?.level_id ?? '';
  // leaf and needle meshes: replaced at runtime by light canopies
  // (demo/data/context.json); the source counts ~250k triangles per pine
  if (/^R(56|130)_TREE.*(LEAVES|NEEDLES)/.test(name)) return 'none';
  if (/^R(56|130)_TREE|^R38_TREE/.test(name)) return 'trees';
  if (level === 'SITE' || level === 'L00_APPROACH') return 'site';
  return 'building';
}

// Decorative parts that are far denser than the web view needs.
// ratio = target share of the source triangles; error = allowed deviation
// relative to the primitive's own extent.
function simplifyRule(name) {
  if (/^R56_TREE.*LEAVES/.test(name)) return { ratio: 0.06, error: 0.1, lockBorder: false };
  if (/^R(56|130)_TREE.*BRANCHES/.test(name)) return { ratio: 0.25, error: 0.02, lockBorder: false };
  if (/^R20_SEAT/.test(name)) return { ratio: 0.18, error: 0.02, lockBorder: false };
  if (/^R21_/.test(name)) return { ratio: 0.2, error: 0.01, lockBorder: false };
  if (/^R51_|^R42_|^R50_/.test(name)) return { ratio: 0.5, error: 0.004, lockBorder: true };
  return null;
}

// Material layers for the exploded views (Malzemelere ayır): floors, walls,
// ceilings and roofs, steel and glazing frames, glass. There is no "other":
// a part that is walked on is a floor, a part that stands is a wall, a part
// overhead is a ceiling or roof. Glass and steel come from the material and
// the one-off classification of the element types (scripts/layers.json);
// floors, walls and ceilings are decided by the part's own geometry: how
// much of its surface faces up or down, how thick it is, and where it sits in
// its storey.
export const LAYERS = ['floors', 'walls', 'ceilings', 'frames', 'glass'];
const layerSpec = JSON.parse(fs.readFileSync(path.join(here, 'layers.json'), 'utf8'));
const layerMap = layerSpec.map;
const FLOOR_LEVELS = [-5.33, -3.83, 0, 4.86]; // slab tops: −1, the pavilion's −1, 0, +1
const WALKED = /TREAD|STAIR|STEP|RISER|NOSING|LANDING|PODIUM|SEAT|TIER|STAGE|RAMP|FLOOR|THRESHOLD|VESTIBULE_MAT|MAT_RECESS|MAT_PANEL|AISLE/;
const ROOF_Y = 9.6; // above the +1 storey: roofs, never floors
const METAL = /METAL|STEEL|ALUMIN|CHROME|BRUSHED|DARK_COATING|FRAME|MULLION|GREY_METAL/;
// parts the rules below misread, checked one by one (layers.json "named")
const NAMED = layerSpec.named.map(([re, layer]) => [new RegExp(re), layer]);

// Area-weighted orientation of a set of world-space triangles: the share
// facing up or down (|n.y| > 0.85) and the share standing (|n.y| < 0.35).
function orientation(triangles) {
  let flat = 0, upright = 0, total = 0;
  for (const [a, b, c] of triangles) {
    const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2];
    const vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    const area = Math.hypot(nx, ny, nz);
    if (!area) continue;
    const y = Math.abs(ny) / area;
    total += area;
    if (y > 0.85) flat += area; else if (y < 0.35) upright += area;
  }
  return { flat: total ? flat / total : 0, upright: total ? upright / total : 0 };
}

function* nodeTriangles(node) {
  const M = node.getWorldMatrix();
  const w = (a, i) => [M[0] * a[i] + M[4] * a[i + 1] + M[8] * a[i + 2] + M[12], M[1] * a[i] + M[5] * a[i + 1] + M[9] * a[i + 2] + M[13], M[2] * a[i] + M[6] * a[i + 1] + M[10] * a[i + 2] + M[14]];
  for (const prim of node.getMesh().listPrimitives()) {
    const a = prim.getAttribute('POSITION').getArray();
    const idx = prim.getIndices()?.getArray();
    const n = idx ? idx.length : a.length / 3;
    for (let t = 0; t + 2 < n; t += 3) {
      const i0 = idx ? idx[t] : t, i1 = idx ? idx[t + 1] : t + 1, i2 = idx ? idx[t + 2] : t + 2;
      yield [w(a, i0 * 3), w(a, i1 * 3), w(a, i2 * 3)];
    }
  }
}

// part: { name, type, materials, lo, hi, flat, upright }
function classify(part) {
  const name = part.name.toUpperCase(), type = (part.type ?? '').toUpperCase();
  const mats = part.materials.join(' ').toUpperCase();
  const named = NAMED.find(([re]) => re.test(part.name));
  if (named) return named[1];
  const mapped = layerMap[part.type];
  if (mapped === 'glass' || (/GLASS|GLAZING/.test(mats) && !/FRAME|SEAL|BEAD/.test(mats))) return 'glass';
  if (mapped === 'frames') return 'frames';
  const dx = part.hi[0] - part.lo[0], dy = part.hi[1] - part.lo[1], dz = part.hi[2] - part.lo[2];
  // railings, guards, door and lift surrounds in metal: steel
  if (mapped === 'fittings' && METAL.test(mats) && !WALKED.test(`${name} ${type}`)) return 'frames';
  // storey of the part: the highest slab top at or below its underside
  const base = FLOOR_LEVELS.filter((f) => f <= part.lo[1] + 0.5).pop() ?? FLOOR_LEVELS[0];
  const top = part.hi[1] - base, bottom = part.lo[1] - base;
  const tallUpright = dy > 2.5 && part.flat < 0.3;
  const roof = part.lo[1] > ROOF_Y;
  // stairs, seats, landings: walked on, whatever their height
  if (WALKED.test(`${name} ${type}`) && !tallUpright && !roof) return 'floors';
  // a plate: mostly facing up or down, or simply wide and thin (slatted and
  // coffered ceilings are mostly upright faces but still a horizontal layer)
  const plate = (part.flat >= 0.5 && dy <= Math.max(1.2, 0.3 * Math.min(Math.max(dx, dz), 10)))
    || (dy <= 0.6 && Math.min(dx, dz) >= 1 && Math.max(dx, dz) >= 3 * dy);
  if (plate) return top <= 1.2 && !roof ? 'floors' : 'ceilings';
  // hung from above: coffers, soffits, beams, lights, roof upstands; an
  // upright face high on a wall (a lintel, a stone band) is still wall
  // unless it is a shallow drop under the ceiling
  if (bottom >= 2.3 && dy <= 3 && (part.upright < 0.6 || dy <= 1)) return 'ceilings';
  return 'walls';
}

// World-space box of a node's mesh (root-level nodes: local = world).
function nodeBox(node) {
  const m = node.getWorldMatrix();
  const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (const prim of node.getMesh().listPrimitives()) {
    const a = prim.getAttribute('POSITION');
    const mn = a.getMin([]), mx = a.getMax([]);
    for (const x of [mn[0], mx[0]]) for (const y of [mn[1], mx[1]]) for (const z of [mn[2], mx[2]]) {
      const w = [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
      for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], w[k]); hi[k] = Math.max(hi[k], w[k]); }
    }
  }
  return { lo, hi };
}

function smoothNormals(doc, prim) {
  const pos = prim.getAttribute('POSITION').getArray();
  const idx = prim.getIndices().getArray();
  const n = new Float32Array(pos.length);
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t] * 3, b = idx[t + 1] * 3, c = idx[t + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const k of [a, b, c]) { n[k] += nx; n[k + 1] += ny; n[k + 2] += nz; }
  }
  for (let k = 0; k < n.length; k += 3) {
    const l = Math.hypot(n[k], n[k + 1], n[k + 2]) || 1;
    n[k] /= l; n[k + 1] /= l; n[k + 2] /= l;
  }
  const buffer = doc.getRoot().listBuffers()[0];
  prim.setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(n).setBuffer(buffer));
}

// Every building part is tagged for the exploded views: _PIECE = x, y, z,
// layer, written into each of its vertices, so the joined meshes can still
// fly apart on the GPU. Small neighbouring parts of one layer and storey move
// together as one fragment (an 8 m cell: a bay of mullions, a run of panes),
// so the explosion reads as pieces of the building rather than dust; parts
// longer than two cells keep their own centre. Parts are also grouped per
// layer so a layer can be hidden.
const CELL = 8;
const storeyOf = (y) => (y < -0.4 ? 0 : y < 4.5 ? 1 : y < 9.6 ? 2 : 3);
const audit = [];
function bakePieces(doc, group, piecesFile) {
  const buffer = doc.getRoot().listBuffers()[0];
  const layerNodes = Object.fromEntries(LAYERS.map((l) => {
    const n = doc.createNode(`LAYER_${l}`);
    group.addChild(n);
    return [l, n];
  }));
  const parts = [];
  for (const node of [...group.listChildren()]) {
    if (node.getName().startsWith('LAYER_')) continue;
    const mesh = node.getMesh();
    if (!mesh) continue;
    const materials = mesh.listPrimitives().map((p) => p.getMaterial()?.getName() ?? '');
    const { lo, hi } = nodeBox(node);
    const info = { name: node.getName(), type: node.getExtras()?.element_type, materials, lo, hi, ...orientation(nodeTriangles(node)) };
    const layer = classify(info);
    // AUDIT=file.tsv: one row per part, to check the classification
    if (process.env.AUDIT) audit.push([info.name, info.type, materials.join('|'), ...lo.map((v) => v.toFixed(2)), ...hi.map((v) => v.toFixed(2)), info.flat.toFixed(2), info.upright.toFixed(2), layer].join('\t'));
    const c = lo.map((v, k) => (v + hi[k]) / 2);
    const diag = Math.hypot(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]);
    const li = LAYERS.indexOf(layer);
    const key = diag > 2 * CELL ? `own:${parts.length}` : `${li}:${Math.floor(c[0] / CELL)}:${Math.floor(c[2] / CELL)}:${storeyOf(c[1])}`;
    parts.push({ node, mesh, layer, li, lo, hi, c, w: Math.max(diag, 0.05), key });
  }
  // fragments: weighted centre of their parts, size = diagonal of their box
  const frags = new Map();
  for (const p of parts) {
    let f = frags.get(p.key);
    if (!f) frags.set(p.key, (f = { li: p.li, sum: [0, 0, 0], w: 0, lo: [...p.lo], hi: [...p.hi], n: 0 }));
    for (let k = 0; k < 3; k++) { f.sum[k] += p.c[k] * p.w; f.lo[k] = Math.min(f.lo[k], p.lo[k]); f.hi[k] = Math.max(f.hi[k], p.hi[k]); }
    f.w += p.w;
    f.n++;
  }
  for (const f of frags.values()) f.c = f.sum.map((v) => Math.round((v / f.w) * 100) / 100);
  const counts = Object.fromEntries(LAYERS.map((l) => [l, 0]));
  for (const p of parts) {
    const f = frags.get(p.key);
    // meshes reused by several nodes get their own copy before tagging
    const unique = doc.createMesh(p.mesh.getName());
    for (const prim of p.mesh.listPrimitives()) {
      const q = prim.clone();
      const n = q.getAttribute('POSITION').getCount();
      const data = new Float32Array(n * 4);
      for (let i = 0; i < n; i++) data.set([f.c[0], f.c[1], f.c[2], p.li], i * 4);
      q.setAttribute('_PIECE', doc.createAccessor().setType('VEC4').setArray(data).setBuffer(buffer));
      unique.addPrimitive(q);
    }
    p.node.setMesh(unique);
    group.removeChild(p.node);
    layerNodes[p.layer].addChild(p.node);
    counts[p.layer]++;
  }
  const pieces = [...frags.values()].map((f) => [...f.c, f.li, Math.round(Math.hypot(f.hi[0] - f.lo[0], f.hi[1] - f.lo[1], f.hi[2] - f.lo[2]) * 100) / 100, f.n]);
  // [x, y, z, layer, size, parts] per fragment
  fs.writeFileSync(piecesFile, JSON.stringify({ layers: LAYERS, cell: CELL, pieces }));
  if (process.env.AUDIT) fs.writeFileSync(process.env.AUDIT, ['name\ttype\tmaterials\tx0\ty0\tz0\tx1\ty1\tz1\tflat\tupright\tlayer', ...audit].join('\n'));
  console.log('parts', parts.length, counts, 'fragments', pieces.length);
}

async function buildChunk(chunk, source, piecesFile) {
  const doc = await readDoc(source);
  // one level of root nodes with world transforms, whatever the hierarchy
  // of the export; then indexed, welded vertices for the simplifier
  await doc.transform(flatten(), weld());
  const root = doc.getRoot();
  const scene = root.getDefaultScene() ?? root.listScenes()[0];
  const group = doc.createNode(`MUDAM_${chunk.toUpperCase()}`);
  const done = new Set();
  let kept = 0;

  for (const node of [...scene.listChildren()]) {
    const extras = node.getExtras();
    if (!node.getMesh() || chunkOf(node.getName(), extras) !== chunk) { node.dispose(); continue; }
    scene.removeChild(node);
    group.addChild(node);
    kept++;
    const rule = simplifyRule(node.getName());
    const mesh = node.getMesh();
    if (rule && mesh && !done.has(mesh)) {
      done.add(mesh);
      for (const prim of mesh.listPrimitives()) {
        // Hard-edged source normals split every corner into separate
        // vertices, which leaves the simplifier nothing to collapse. Weld on
        // position alone, simplify, then rebuild smooth normals.
        const normal = prim.getAttribute('NORMAL');
        const hasTexture = prim.listSemantics().some((s) => s.startsWith('TEXCOORD'));
        if (normal && !hasTexture) { prim.setAttribute('NORMAL', null); normal.dispose(); weldPrimitive(prim, { overwrite: true }); }
        simplifyPrimitive(prim, { simplifier: MeshoptSimplifier, ...rule });
        if (!prim.getAttribute('NORMAL')) smoothNormals(doc, prim);
      }
    }
  }
  if (!kept) { console.log(`${chunk}: no source nodes in ${path.basename(source)}`); return null; }
  scene.addChild(group);
  if (chunk === 'building') bakePieces(doc, group, piecesFile);
  // provenance notes stay in the source export, not in the web copy
  group.traverse((n) => n.setExtras({}));
  // Materials and meshes only referenced by the other chunks go away here.
  await doc.transform(
    prune(),
    dedup(),
    weld(),
    join({ keepNamed: false, keepMeshes: false }),
    prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 82, resize: chunk === 'site' ? [2048, 2048] : [1024, 1024] }),
    draco({ method: 'edgebreaker', quantizePosition: 16, quantizeNormal: 10, quantizeTexcoord: 12, quantizeGeneric: 14 }),
  );
  for (const material of root.listMaterials()) material.setExtras({});
  const out = path.join(outDir, `${chunk}.glb`);
  await io.write(out, doc);
  const st = stats(doc);
  console.log(`${chunk}: ${kept} source nodes -> ${st.prims} primitives, ${st.tris} triangles, ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`, JSON.stringify(st.bounds));
  return { file: path.relative(path.join(repo, 'demo'), out), bytes: fs.statSync(out).size, ...st };
}

// Çevre 2 building. The R151 web export arrives as one node with every part
// joined per material (111 primitives), with the moat and terrain inside it.
// To cut, lift and take it apart like Çevre 1, its triangles are traced back
// to the R149 parts: connected pieces of each primitive vote with their
// vertices (1 cm) for the R149 node they came from. That node gives the
// chunk (building, site, trees) and the material layer. Pieces that changed
// after R149 (re-tessellated rods and frames, the ACT ground blend) take the
// R149 part whose box contains them, else their material name decides.
async function buildR151Building(source, piecesFile) {
  const Q = 100;
  const key = (x, y, z) => `${Math.round(x * Q)},${Math.round(y * Q)},${Math.round(z * Q)}`;
  // --- R149 parts: chunk, layer, box, vertex index
  const ref = await readDoc(path.join(repo, '12_Blender_Model/exports/current.glb.gz'));
  const refNodes = ref.getRoot().getDefaultScene().listChildren().filter((n) => n.getMesh());
  const vertexNode = new Map();
  const refParts = refNodes.map((n, ni) => {
    const mesh = n.getMesh();
    const M = n.getWorldMatrix();
    for (const prim of mesh.listPrimitives()) {
      const a = prim.getAttribute('POSITION').getArray();
      for (let i = 0; i < a.length; i += 3) {
        const x = a[i], y = a[i + 1], z = a[i + 2];
        vertexNode.set(key(M[0] * x + M[4] * y + M[8] * z + M[12], M[1] * x + M[5] * y + M[9] * z + M[13], M[2] * x + M[6] * y + M[10] * z + M[14]), ni);
      }
    }
    const materials = mesh.listPrimitives().map((p) => p.getMaterial()?.getName() ?? '');
    const { lo, hi } = nodeBox(n);
    const layer = classify({ name: n.getName(), type: n.getExtras()?.element_type, materials, lo, hi, ...orientation(nodeTriangles(n)) });
    return { chunk: chunkOf(n.getName(), n.getExtras()), layer, lo, hi, vol: (hi[0] - lo[0]) * (hi[1] - lo[1]) * (hi[2] - lo[2]) };
  });
  const containing = (c) => {
    let best = -1;
    refParts.forEach((p, i) => {
      if (c.every((v, k) => v >= p.lo[k] - 0.05 && v <= p.hi[k] + 0.05) && (best < 0 || p.vol < refParts[best].vol)) best = i;
    });
    return best;
  };

  // --- R151 pieces: connected triangles per primitive
  const doc = await readDoc(source);
  await doc.transform(flatten());
  const root = doc.getRoot();
  const buffer = root.listBuffers()[0];
  const prims = [];
  for (const node of root.listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const M = node.getWorldMatrix();
    const identity = M.every((v, i) => Math.abs(v - (i % 5 === 0 ? 1 : 0)) < 1e-9);
    if (!identity) throw new Error('Çevre 2: building node is transformed; bake transforms before export');
    for (const prim of mesh.listPrimitives()) prims.push(prim);
  }
  const parts = new Map(); // part id -> { chunk, layer, lo, hi }
  const triPart = [];
  let matchedTris = 0, totalTris = 0;
  prims.forEach((prim, pi) => {
    const pos = prim.getAttribute('POSITION').getArray();
    const idx = prim.getIndices().getArray();
    const nv = pos.length / 3, nt = idx.length / 3;
    totalTris += nt;
    const parent = new Int32Array(nv).map((_, i) => i);
    const find = (v) => { while (parent[v] !== v) { parent[v] = parent[parent[v]]; v = parent[v]; } return v; };
    for (let t = 0; t < nt; t++) {
      const a = find(idx[t * 3]), b = find(idx[t * 3 + 1]), c = find(idx[t * 3 + 2]);
      parent[b] = a; parent[find(c)] = a;
    }
    const comps = new Map();
    for (let v = 0; v < nv; v++) {
      const r = find(v);
      let c = comps.get(r);
      if (!c) comps.set(r, (c = { votes: new Map(), n: 0, lo: [Infinity, Infinity, Infinity], hi: [-Infinity, -Infinity, -Infinity] }));
      const x = pos[v * 3], y = pos[v * 3 + 1], z = pos[v * 3 + 2];
      const ni = vertexNode.get(key(x, y, z));
      if (ni !== undefined) c.votes.set(ni, (c.votes.get(ni) ?? 0) + 1);
      c.n++;
      c.lo = [Math.min(c.lo[0], x), Math.min(c.lo[1], y), Math.min(c.lo[2], z)];
      c.hi = [Math.max(c.hi[0], x), Math.max(c.hi[1], y), Math.max(c.hi[2], z)];
    }
    const material = prim.getMaterial()?.getName() ?? '';
    // orientation of each piece, for pieces that need classifying afresh
    for (let t = 0; t < nt; t++) {
      const c = comps.get(find(idx[t * 3]));
      const at = (k) => [pos[idx[t * 3 + k] * 3], pos[idx[t * 3 + k] * 3 + 1], pos[idx[t * 3 + k] * 3 + 2]];
      (c.tris ??= []).push([at(0), at(1), at(2)]);
    }
    for (const [r, c] of comps) {
      let ni = -1, best = 0;
      for (const [n, k] of c.votes) if (k > best) { best = k; ni = n; }
      let id, chunk, layer;
      if (ni >= 0 && best >= 0.3 * c.n) {
        id = `n${ni}`; ({ chunk, layer } = refParts[ni]);
      } else {
        const centre = c.lo.map((v, k) => (v + c.hi[k]) / 2);
        const hold = /ACT_GROUND/.test(material) ? -1 : containing(centre);
        id = hold >= 0 ? `n${hold}` : `p${pi}:${r}`;
        chunk = hold >= 0 ? refParts[hold].chunk : /GROUND|TURF|MOAT|TERRAIN/.test(material) ? 'site' : 'building';
        layer = hold >= 0 ? refParts[hold].layer : classify({ name: '', type: '', materials: [material], lo: c.lo, hi: c.hi, ...orientation(c.tris) });
      }
      c.id = id;
      c.tris = null;
      let part = parts.get(id);
      if (!part) parts.set(id, (part = { chunk, layer, lo: [...c.lo], hi: [...c.hi] }));
      for (let k = 0; k < 3; k++) { part.lo[k] = Math.min(part.lo[k], c.lo[k]); part.hi[k] = Math.max(part.hi[k], c.hi[k]); }
    }
    const tp = new Array(nt);
    for (let t = 0; t < nt; t++) {
      const c = comps.get(find(idx[t * 3]));
      tp[t] = c.id;
      if (c.id.startsWith('n') && c.votes.size) matchedTris++;
    }
    triPart[pi] = tp;
  });
  console.log(`R151 building: ${prims.length} primitives, ${totalTris} triangles, ${parts.size} parts, ${(100 * matchedTris / totalTris).toFixed(1)} % of triangles matched to R149 parts by vertex`);

  // --- fragments for the exploded views, as bakePieces does for Çevre 1
  const frags = new Map();
  const partFrag = new Map();
  for (const [id, p] of parts) {
    if (p.chunk !== 'building') continue;
    const c = p.lo.map((v, k) => (v + p.hi[k]) / 2);
    const diag = Math.hypot(p.hi[0] - p.lo[0], p.hi[1] - p.lo[1], p.hi[2] - p.lo[2]);
    const li = LAYERS.indexOf(p.layer);
    const fk = diag > 2 * CELL ? `own:${id}` : `${li}:${Math.floor(c[0] / CELL)}:${Math.floor(c[2] / CELL)}:${storeyOf(c[1])}`;
    const w = Math.max(diag, 0.05);
    let f = frags.get(fk);
    if (!f) frags.set(fk, (f = { li, sum: [0, 0, 0], w: 0, lo: [...p.lo], hi: [...p.hi], n: 0 }));
    for (let k = 0; k < 3; k++) { f.sum[k] += c[k] * w; f.lo[k] = Math.min(f.lo[k], p.lo[k]); f.hi[k] = Math.max(f.hi[k], p.hi[k]); }
    f.w += w; f.n++;
    partFrag.set(id, f);
  }
  for (const f of frags.values()) f.c = f.sum.map((v) => Math.round((v / f.w) * 100) / 100);
  const pieces = [...frags.values()].map((f) => [...f.c, f.li, Math.round(Math.hypot(f.hi[0] - f.lo[0], f.hi[1] - f.lo[1], f.hi[2] - f.lo[2]) * 100) / 100, f.n]);
  fs.writeFileSync(piecesFile, JSON.stringify({ layers: LAYERS, cell: CELL, pieces }));
  const counts = {};
  for (const p of parts.values()) counts[`${p.chunk}/${p.layer}`] = (counts[`${p.chunk}/${p.layer}`] ?? 0) + 1;
  console.log('parts by chunk/layer', counts, 'fragments', pieces.length);

  // --- one file per chunk: triangles regrouped per layer, _PIECE baked in
  const subset = (prim, tris, piece) => {
    const idx = prim.getIndices().getArray();
    const remap = new Map(), order = [];
    const out = new Uint32Array(tris.length * 3);
    tris.forEach((t, k) => {
      for (let c = 0; c < 3; c++) {
        const v = idx[t * 3 + c];
        let n = remap.get(v);
        if (n === undefined) { n = order.length; remap.set(v, n); order.push(v); }
        out[k * 3 + c] = n;
      }
    });
    const q = doc.createPrimitive().setMaterial(prim.getMaterial()).setMode(prim.getMode());
    for (const sem of prim.listSemantics()) {
      const acc = prim.getAttribute(sem), size = acc.getElementSize(), src = acc.getArray();
      const dst = new src.constructor(order.length * size);
      order.forEach((v, i) => { for (let c = 0; c < size; c++) dst[i * size + c] = src[v * size + c]; });
      q.setAttribute(sem, doc.createAccessor().setType(acc.getType()).setArray(dst).setNormalized(acc.getNormalized()).setBuffer(buffer));
    }
    if (piece) {
      const data = new Float32Array(order.length * 4);
      const vertTri = new Int32Array(order.length);
      tris.forEach((t, k) => { for (let c = 0; c < 3; c++) vertTri[out[k * 3 + c]] = t; });
      for (let i = 0; i < order.length; i++) data.set(piece(vertTri[i]), i * 4);
      q.setAttribute('_PIECE', doc.createAccessor().setType('VEC4').setArray(data).setBuffer(buffer));
    }
    q.setIndices(doc.createAccessor().setType('SCALAR').setArray(out).setBuffer(buffer));
    return q;
  };
  const scene = root.getDefaultScene() ?? root.listScenes()[0];
  const groups = {};
  const groupNode = (chunk, layer) => {
    const k = `${chunk}/${layer}`;
    if (groups[k]) return groups[k];
    let top = groups[chunk];
    if (!top) { top = groups[chunk] = doc.createNode(`MUDAM_${chunk.toUpperCase()}`); scene.addChild(top); }
    if (chunk !== 'building') return (groups[k] = top);
    const n = doc.createNode(`LAYER_${layer}`);
    top.addChild(n);
    return (groups[k] = n);
  };
  const meshes = {};
  prims.forEach((prim, pi) => {
    const byGroup = new Map();
    triPart[pi].forEach((id, t) => {
      const p = parts.get(id);
      if (p.chunk === 'none') return;
      const g = `${p.chunk}/${p.layer}`;
      if (!byGroup.has(g)) byGroup.set(g, []);
      byGroup.get(g).push(t);
    });
    for (const [g, tris] of byGroup) {
      const [chunk, layer] = g.split('/');
      const piece = chunk === 'building' ? (t) => { const f = partFrag.get(triPart[pi][t]); return [f.c[0], f.c[1], f.c[2], f.li]; } : null;
      if (!meshes[g]) { meshes[g] = doc.createMesh(g); groupNode(chunk, layer).addChild(doc.createNode(g).setMesh(meshes[g])); }
      meshes[g].addPrimitive(subset(prim, tris, piece));
    }
  });
  for (const node of [...scene.listChildren()]) if (!Object.values(groups).includes(node)) node.dispose();
  for (const n of root.listNodes()) n.setExtras({});
  await doc.transform(prune());

  // write each chunk from a copy of the regrouped document
  const files = {};
  const bytes = await io.writeBinary(doc);
  for (const chunk of ['building', 'site', 'trees']) {
    if (!groups[chunk]) continue;
    const d = await io.readBinary(bytes);
    const s0 = d.getRoot().getDefaultScene() ?? d.getRoot().listScenes()[0];
    for (const n of [...s0.listChildren()]) if (n.getName() !== `MUDAM_${chunk.toUpperCase()}`) n.dispose();
    await d.transform(
      prune(),
      dedup(),
      join({ keepNamed: false, keepMeshes: false }),
      prune(),
      textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 82, resize: chunk === 'site' ? [2048, 2048] : [1024, 1024] }),
      draco({ method: 'edgebreaker', quantizePosition: 16, quantizeNormal: 10, quantizeTexcoord: 12, quantizeGeneric: 14 }),
    );
    for (const m of d.getRoot().listMaterials()) m.setExtras({});
    const out = path.join(outDir, `${chunk}.glb`);
    await io.write(out, d);
    const st = stats(d);
    console.log(`${chunk}: ${st.prims} primitives, ${st.tris} triangles, ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`, JSON.stringify(st.bounds));
    files[chunk] = { file: path.relative(path.join(repo, 'demo'), out), bytes: fs.statSync(out).size, ...st };
  }
  return files;
}

// Ready-made surroundings (Çevre 2, ACT photo meshes): merged draw calls,
// WebP textures and Draco geometry, and a lighter mesh: the near context
// keeps `ratio` of its triangles, the far one, seen only from a distance,
// less. `error` is relative to each tile's own size.
async function buildContext(name, source, { texture, ratio, error, bits }) {
  const doc = await readDoc(source);
  const before = stats(doc);
  const root = doc.getRoot();
  for (const n of root.listNodes()) n.setExtras({});
  for (const m of root.listMaterials()) m.setExtras({});
  await doc.transform(
    dedup(),
    prune(),
    weld(),
    // tile and UV-island borders stay put, or the sky shows through cracks
    simplify({ simplifier: MeshoptSimplifier, ratio, error, lockBorder: true }),
    join({ keepNamed: false, keepMeshes: false }),
    prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 80, resize: [texture, texture] }),
    // 14 bits over the ~430 m (near) or ~900 m (far) extent: 3 to 6 cm
    draco({ method: 'edgebreaker', quantizePosition: bits, quantizeNormal: 10, quantizeTexcoord: 12, quantizeGeneric: 14 }),
  );
  const out = path.join(outDir, `${name}.glb`);
  await io.write(out, doc);
  const st = stats(doc);
  console.log(`${name}: ${(fs.statSync(source).size / 1048576).toFixed(2)} MB, ${before.prims} primitives, ${before.tris} triangles, ${before.textures} textures -> ${st.prims} primitives, ${st.tris} triangles, ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`, JSON.stringify(st.bounds));
  return { file: path.relative(path.join(repo, 'demo'), out), bytes: fs.statSync(out).size, ...st };
}

if (!CEVRE2) {
  const source = path.join(repo, '12_Blender_Model/exports/current.glb.gz');
  for (const chunk of ['building', 'site', 'trees']) await buildChunk(chunk, source, path.join(dataDir, 'pieces.json'));
} else {
  const src = (name) => {
    const f = ['.glb', '.glb.gz'].map((e) => path.join(R151, name + e)).find((f) => fs.existsSync(f));
    if (!f) throw new Error(`Çevre 2: ${name}.glb not found in ${R151}`);
    return f;
  };
  // the museum, taken apart like Çevre 1 (sections, floors, material layers)
  const files = await buildR151Building(src('building'), path.join(dataDir, 'pieces-cevre2.json'));
  files.near = await buildContext('near', src('near_context'), { texture: 1024, ratio: 0.6, error: 0.004, bits: 14 });
  files.far = await buildContext('far', src('far_context'), { texture: 256, ratio: 0.35, error: 0.01, bits: 14 });
  const lod = path.join(repo, '12_Blender_Model/config/r151_web_lod.json');
  const manifest = {
    name: 'Çevre 2',
    source: path.relative(repo, R151).split(path.sep).join('/'),
    revision: fs.existsSync(lod) ? JSON.parse(fs.readFileSync(lod, 'utf8')).revision : path.basename(R151),
    pieces: 'data/pieces-cevre2.json',
    files,
  };
  fs.writeFileSync(path.join(dataDir, 'cevre2.json'), JSON.stringify(manifest, null, 1));
  console.log('wrote demo/data/cevre2.json');
}
