// Mudam web model: 12_Blender_Model/exports/current.glb.gz -> demo/model/*.glb
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
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, join, weld, weldPrimitive, draco, textureCompress, simplifyPrimitive } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import draco3d from 'draco3dgltf';
import sharp from 'sharp';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const source = path.join(repo, '12_Blender_Model/exports/current.glb.gz');
const outDir = path.join(repo, 'demo/model');
fs.mkdirSync(outDir, { recursive: true });

const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({
    'draco3d.decoder': await draco3d.createDecoderModule(),
    'draco3d.encoder': await draco3d.createEncoderModule(),
  });

await MeshoptSimplifier.ready;

// Which chunk a source node belongs to. Site context (moat, park, approach)
// and the trees are separate files so the building can appear first.
function chunkOf(name, extras) {
  const level = extras?.level_id ?? '';
  // leaf meshes: replaced at runtime by light canopies (demo/data/context.json)
  if (/^R56_TREE.*LEAVES/.test(name)) return 'none';
  if (/^R56_TREE|^R38_TREE/.test(name)) return 'trees';
  if (level === 'SITE' || level === 'L00_APPROACH') return 'site';
  return 'building';
}

// Decorative parts that are far denser than the web view needs.
// ratio = target share of the source triangles; error = allowed deviation
// relative to the primitive's own extent.
function simplifyRule(name) {
  if (/^R56_TREE.*LEAVES/.test(name)) return { ratio: 0.06, error: 0.1, lockBorder: false };
  if (/^R56_TREE.*BRANCHES/.test(name)) return { ratio: 0.25, error: 0.02, lockBorder: false };
  if (/^R20_SEAT/.test(name)) return { ratio: 0.18, error: 0.02, lockBorder: false };
  if (/^R21_/.test(name)) return { ratio: 0.2, error: 0.01, lockBorder: false };
  if (/^R51_|^R42_|^R50_/.test(name)) return { ratio: 0.5, error: 0.004, lockBorder: true };
  return null;
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

async function buildChunk(chunk) {
  const buffer = zlib.gunzipSync(fs.readFileSync(source));
  const doc = await io.readBinary(new Uint8Array(buffer));
  // Simplification needs indexed, welded vertices.
  await doc.transform(weld());
  const root = doc.getRoot();
  const scene = root.getDefaultScene() ?? root.listScenes()[0];
  const group = doc.createNode(`MUDAM_${chunk.toUpperCase()}`);
  const done = new Set();
  let kept = 0;

  for (const node of [...scene.listChildren()]) {
    const extras = node.getExtras();
    if (chunkOf(node.getName(), extras) !== chunk) { node.dispose(); continue; }
    node.setExtras({});
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
  scene.addChild(group);
  // Materials and meshes only referenced by the other chunks go away here.
  await doc.transform(
    prune(),
    dedup(),
    weld(),
    join({ keepNamed: false, keepMeshes: false }),
    prune(),
    textureCompress({ encoder: sharp, targetFormat: 'webp', quality: 82, resize: chunk === 'site' ? [2048, 2048] : [1024, 1024] }),
    draco({ method: 'edgebreaker', quantizePosition: 16, quantizeNormal: 10, quantizeTexcoord: 12 }),
  );
  for (const material of root.listMaterials()) material.setExtras({});
  const out = path.join(outDir, `${chunk}.glb`);
  await io.write(out, doc);
  const prims = root.listMeshes().reduce((n, m) => n + m.listPrimitives().length, 0);
  let tris = 0;
  for (const m of root.listMeshes()) for (const p of m.listPrimitives()) tris += (p.getIndices()?.getCount() ?? p.getAttribute('POSITION').getCount()) / 3;
  console.log(`${chunk}: ${kept} source nodes -> ${prims} primitives, ${Math.round(tris)} triangles, ${(fs.statSync(out).size / 1048576).toFixed(2)} MB`);
}

for (const chunk of ['building', 'site', 'trees']) await buildChunk(chunk);
