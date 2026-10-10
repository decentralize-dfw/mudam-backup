// Mudam web model, two sets:
//
//   node scripts/build-model.mjs
//     Çevre 1: 12_Blender_Model/exports/current.glb.gz -> demo/model/{building,site,trees}.glb
//   node scripts/build-model.mjs --cevre2 [dir]
//     Çevre 2: 12_Blender_Model/exports/r151_web_v002/{building,near_context,far_context}.glb
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
import { dedup, prune, join, weld, weldPrimitive, draco, textureCompress, simplifyPrimitive, flatten } from '@gltf-transform/functions';
import { MeshoptSimplifier, MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';
import draco3d from 'draco3dgltf';
import sharp from 'sharp';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const args = process.argv.slice(2);
const CEVRE2 = args.includes('--cevre2');
const R151 = path.resolve(args.find((a) => !a.startsWith('--')) ?? path.join(repo, '12_Blender_Model/exports/r151_web_v002'));
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

// Material layers for the exploded views (Malzemelere ayır). Element types
// were classified once (scripts/layers.json, element_type -> layer); new
// element types fall back to the keyword rules below.
export const LAYERS = ['floors', 'walls', 'ceilings', 'frames', 'glass', 'fittings'];
const layerMap = JSON.parse(fs.readFileSync(path.join(here, 'layers.json'), 'utf8')).map;
function layerOf(name, extras, materials) {
  const known = layerMap[extras?.element_type];
  if (known && LAYERS.includes(known)) return known;
  const s = `${name} ${extras?.element_type ?? ''} ${materials.join(' ')}`.toUpperCase();
  if (/GLASS|GLAZING|PANE\b/.test(s) && !/FRAME|SEAL|BEAD|FIXING|RAIL/.test(s)) return 'glass';
  if (/TREAD|NOSING|RISER|STAIR|RAIL|SEAT|LIGHT|LENS|LAMP|FIXTURE|DOOR|HINGE|PANEL_BODY|SIGN|CONTROL|SPEAKER|TRACK/.test(s)) return 'fittings';
  if (/FRAME|MULLION|TRANSOM|ROD|STRUT|SHADE|SHADING|SEAL|BEAD|CHANNEL|POST|FIXING|METAL|STEEL/.test(s)) return 'frames';
  if (/CEILING|SOFFIT|ROOF|APRON|CANOPY_SLAB|FASCIA/.test(s)) return 'ceilings';
  if (/FLOOR|SLAB|LANDING|THRESHOLD|STAGE|DECK|ZONE_/.test(s)) return 'floors';
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
    const layer = layerOf(node.getName(), node.getExtras(), materials);
    const { lo, hi } = nodeBox(node);
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

// Ready-made surroundings (Çevre 2): kept as delivered apart from merging
// draw calls, WebP textures and Draco geometry.
async function buildContext(name, source, texture) {
  const doc = await readDoc(source);
  const before = stats(doc);
  const root = doc.getRoot();
  for (const n of root.listNodes()) n.setExtras({});
  for (const m of root.listMaterials()) m.setExtras({});
  await doc.transform(
    dedup(),
    prune(),
    join({ keepNamed: false, keepMeshes: false }),
    prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 80, resize: [texture, texture] }),
    draco({ method: 'edgebreaker', quantizePosition: 16, quantizeNormal: 10, quantizeTexcoord: 12, quantizeGeneric: 14 }),
  );
  const out = path.join(outDir, `${name}.glb`);
  await io.write(out, doc);
  const st = stats(doc);
  console.log(`${name}: ${(fs.statSync(source).size / 1048576).toFixed(2)} MB, ${before.prims} primitives, ${before.tris} triangles, ${before.textures} textures -> ${st.prims} primitives, ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`, JSON.stringify(st.bounds));
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
  const files = {};
  // the museum, taken apart like Çevre 1 (sections, floors, material layers)
  for (const chunk of ['building', 'site', 'trees']) {
    const r = await buildChunk(chunk, src('building'), path.join(dataDir, 'pieces-cevre2.json'));
    if (r) files[chunk] = r;
  }
  files.near = await buildContext('near', src('near_context'), 2048);
  files.far = await buildContext('far', src('far_context'), 1024);
  const manifest = {
    name: 'Çevre 2',
    source: path.relative(repo, R151).split(path.sep).join('/'),
    revision: path.basename(R151),
    pieces: 'data/pieces-cevre2.json',
    files,
  };
  fs.writeFileSync(path.join(dataDir, 'cevre2.json'), JSON.stringify(manifest, null, 1));
  console.log('wrote demo/data/cevre2.json');
}
