// Walking surface for the walk mode: where a visitor can stand inside the
// building, as a height field on a 0.25 m grid. Built from the web model
// itself (demo/model/building.glb, after `npm run model`), so it matches what
// is drawn:
//
//   node scripts/build-walk.mjs  ->  demo/data/walk.json
//
// A cell is walkable at height h when a part of the floors layer (slabs,
// finishes, stairs, landings, ramps; _PIECE.w = 0) has an upward face there at
// h, and nothing at all (walls, glass, rails, the stair above, a low beam)
// passes through the body from knee to head, h + STEP .. h + HEAD. One cell
// can hold several heights: the storeys above each other, a stair under a
// landing. Blocked cells grow by one cell, the visitor's shoulders. Rows are
// run-length coded per layer: [first column, count, height in mm].
//
// Stairs are walked as one ramp each: from the floor at the foot to the floor
// at the head, one even slope along the way up, landings included, so the
// eye glides instead of hopping from tread to tread. The stairs are found by
// name in the source model (treads, nosings, aisles, corner landings of
// 12_Blender_Model/exports/current.glb.gz); each connected flight of them is
// one ramp, its height set by how far along the way up a cell lies.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
import { MeshoptDecoder } from 'meshoptimizer';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const source = path.join(repo, 'demo/model/building.glb');
const stairSource = path.join(repo, '12_Blender_Model/exports/current.glb.gz');
const out = path.join(repo, 'demo/data/walk.json');

const STEP = 0.25;      // grid cell, m
const EYE = 1.6;        // eye above the floor
const MAX_STEP = 0.38;  // highest step taken in one move (one or two risers)
const KNEE = 0.4;       // obstacles from here ...
const HEAD = 1.95;      // ... to here above the floor block the cell
const MERGE = 0.3;      // walkable faces closer than this in one cell are one floor
const UP = 0.7;         // walkable faces: normal.y above this (up to ~45°)
const FLOORS = 0;       // layer index of the floors layer (scripts/build-model.mjs LAYERS)
// stair parts in the source model, by name or element type
const STAIR_NAME = /TREAD|NOSING|AISLE|CORNER_LANDING/;
const STAIR_TYPE = /tread|quarter_turn_flat_landing|radial_step/;
const STAIR_LINK = 0.45; // treads this close in height, side by side, are one flight
const RAMP_KNEE = 0.8;   // on a ramp, the stair's own treads and landings may rise this far above it

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'draco3d.decoder': await draco3d.createDecoderModule(), 'meshopt.decoder': MeshoptDecoder });
const doc = await io.read(source);

// World-space triangles of a document's meshes: [ax, ay, az, bx, by, bz, cx,
// cy, cz, layer]; `keep(node)` picks the nodes.
function triangles(document, keep = () => true) {
  const list = [];
  for (const node of document.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh || !keep(node)) continue;
    const M = node.getWorldMatrix();
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION');
      const piece = prim.getAttribute('_PIECE');
      const idx = prim.getIndices()?.getArray();
      const n = idx ? idx.length : pos.getCount();
      const v = [], p = [];
      const world = (i) => {
        pos.getElement(i, v);
        return [M[0] * v[0] + M[4] * v[1] + M[8] * v[2] + M[12], M[1] * v[0] + M[5] * v[1] + M[9] * v[2] + M[13], M[2] * v[0] + M[6] * v[1] + M[10] * v[2] + M[14]];
      };
      for (let t = 0; t + 2 < n; t += 3) {
        const i0 = idx ? idx[t] : t;
        const layer = piece ? Math.round(piece.getElement(i0, p)[3]) : -1;
        list.push([...world(i0), ...world(idx ? idx[t + 1] : t + 1), ...world(idx ? idx[t + 2] : t + 2), layer]);
      }
    }
  }
  return list;
}

// --- world-space triangles of the web model, with their layer
const tris = triangles(doc);
// --- the stairs' walked faces, from the source model
const stairNames = new Set();
const stairTris = triangles(await io.readBinary(new Uint8Array(zlib.gunzipSync(fs.readFileSync(stairSource)))), (node) => {
  const yes = STAIR_NAME.test(node.getName()) || STAIR_TYPE.test(node.getExtras()?.element_type ?? '');
  if (yes) stairNames.add(node.getName().replace(/_\d+(_\d+)*$/, ''));
  return yes;
});

// --- grid over the building
const lo = [Infinity, Infinity], hi = [-Infinity, -Infinity];
for (const t of tris) for (const k of [0, 3, 6]) {
  lo[0] = Math.min(lo[0], t[k]); hi[0] = Math.max(hi[0], t[k]);
  lo[1] = Math.min(lo[1], t[k + 2]); hi[1] = Math.max(hi[1], t[k + 2]);
}
const gx = Math.floor(lo[0] / STEP) * STEP - STEP, gz = Math.floor(lo[1] / STEP) * STEP - STEP;
const W = Math.ceil((hi[0] - gx) / STEP) + 2, H = Math.ceil((hi[1] - gz) / STEP) + 2;
const count = W * H;

// Clip a polygon (flat [x, y, z, ...]) to axis k in [a, b].
function clip(poly, k, a, b) {
  for (const [s, bound] of [[1, a], [-1, b]]) {
    const outp = [];
    const n = poly.length / 3;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      const pi = poly[i * 3 + k] * s - bound * s, pj = poly[j * 3 + k] * s - bound * s;
      if (pi >= 0) outp.push(poly[i * 3], poly[i * 3 + 1], poly[i * 3 + 2]);
      if ((pi >= 0) !== (pj >= 0)) {
        const t = pi / (pi - pj);
        outp.push(poly[i * 3] + (poly[j * 3] - poly[i * 3]) * t, poly[i * 3 + 1] + (poly[j * 3 + 1] - poly[i * 3 + 1]) * t, poly[i * 3 + 2] + (poly[j * 3 + 2] - poly[i * 3 + 2]) * t);
      }
    }
    poly = outp;
    if (!poly.length) return poly;
  }
  return poly;
}

// Every (cell, y range) a triangle passes through.
function cover(t, visit) {
  const tri = t.slice(0, 9);
  let z0 = Infinity, z1 = -Infinity;
  for (const k of [2, 5, 8]) { z0 = Math.min(z0, tri[k]); z1 = Math.max(z1, tri[k]); }
  const r0 = Math.max(0, Math.floor((z0 - gz) / STEP)), r1 = Math.min(H - 1, Math.floor((z1 - gz) / STEP));
  for (let row = r0; row <= r1; row++) {
    const band = clip(tri, 2, gz + row * STEP, gz + (row + 1) * STEP);
    if (!band.length) continue;
    let x0 = Infinity, x1 = -Infinity;
    for (let i = 0; i < band.length; i += 3) { x0 = Math.min(x0, band[i]); x1 = Math.max(x1, band[i]); }
    const c0 = Math.max(0, Math.floor((x0 - gx) / STEP)), c1 = Math.min(W - 1, Math.floor((x1 - gx) / STEP));
    for (let col = c0; col <= c1; col++) {
      const cell = clip(band, 0, gx + col * STEP, gx + (col + 1) * STEP);
      if (!cell.length) continue;
      let y0 = Infinity, y1 = -Infinity;
      for (let i = 1; i < cell.length; i += 3) { y0 = Math.min(y0, cell[i]); y1 = Math.max(y1, cell[i]); }
      visit(row * W + col, y0, y1);
    }
  }
}

const normalY = (t) => {
  const ux = t[3] - t[0], uy = t[4] - t[1], uz = t[5] - t[2], vx = t[6] - t[0], vy = t[7] - t[1], vz = t[8] - t[2];
  const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
  return ny / (Math.hypot(nx, ny, nz) || 1);
};

// --- pass 1: walkable heights per cell (top of each floors-layer face).
// Faces closer than MERGE are one floor at the highest of them (a slab and
// the tread on it, two treads in one cell).
const MAX_LAYERS = 8;
const faces = Array.from({ length: count }, () => null);
let walkTris = 0;
for (const t of tris) {
  if (t[9] !== FLOORS || normalY(t) < UP) continue;
  walkTris++;
  cover(t, (i, y0, y1) => { (faces[i] ??= []).push(y1); });
}
const tops = faces.map((list) => {
  if (!list) return null;
  list.sort((a, b) => b - a);
  const out = [];
  let low = Infinity;
  for (const h of list) {
    if (h > low - MERGE) { low = h; continue; }
    out.push(h);
    low = h;
  }
  return out.reverse().slice(-MAX_LAYERS);
});

// --- stairs as ramps
// Tread heights per cell (one per flight above another), linked to the
// neighbouring cells' treads within STAIR_LINK: each connected set is a stair.
const treadFaces = new Map();
for (const t of stairTris) {
  if (normalY(t) < UP) continue;
  cover(t, (i, y0, y1) => { if (!treadFaces.has(i)) treadFaces.set(i, []); treadFaces.get(i).push(y1); });
}
const nodes = []; // { i, h }
const nodesAt = new Map(); // cell -> node ids
for (const [i, list] of treadFaces) {
  list.sort((a, b) => b - a);
  let low = Infinity;
  for (const h of list) {
    if (h > low - MERGE) { low = h; continue; }
    low = h;
    if (!nodesAt.has(i)) nodesAt.set(i, []);
    nodesAt.get(i).push(nodes.length);
    nodes.push({ i, h });
  }
}
const NEAR8 = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, Math.SQRT2], [1, -1, Math.SQRT2], [-1, 1, Math.SQRT2], [-1, -1, Math.SQRT2]];
const around = (i, fn) => {
  const col = i % W, row = (i - col) / W;
  for (const [dc, dr, w] of NEAR8) {
    const c = col + dc, r = row + dr;
    if (c >= 0 && r >= 0 && c < W && r < H) fn(r * W + c, w);
  }
};
const links = (n, fn) => around(nodes[n].i, (j, w) => {
  for (const m of nodesAt.get(j) ?? []) if (Math.abs(nodes[m].h - nodes[n].h) <= STAIR_LINK) fn(m, w);
});
// shortest way along the stair from a set of start nodes
function along(starts, inStair) {
  const d = new Map(starts.map((n) => [n, 0]));
  const queue = [...starts];
  // few hundred nodes per stair: a plain relaxation queue is enough
  while (queue.length) {
    const n = queue.shift();
    links(n, (m, w) => {
      if (!inStair.has(m)) return;
      const v = d.get(n) + w;
      if (v < (d.get(m) ?? Infinity) - 1e-9) { d.set(m, v); queue.push(m); }
    });
  }
  return d;
}
const ramp = new Map(); // cell -> [[tread height, ramp height], ...]
const stairs = [];
const seen = []; // nodes already in a stair (absorbed edge cells join later)
for (let n0 = 0, count0 = nodes.length; n0 < count0; n0++) {
  if (seen[n0]) continue;
  const stair = [n0];
  seen[n0] = 1;
  for (let q = 0; q < stair.length; q++) links(stair[q], (m) => { if (!seen[m]) { seen[m] = 1; stair.push(m); } });
  const inStair = new Set(stair);
  // the floors it meets: standing heights next to a tread, within a link,
  // that are not this stair's own treads
  const contacts = [];
  for (const n of stair) {
    const { i, h } = nodes[n];
    const meet = (j) => {
      for (const t of tops[j] ?? []) {
        if (Math.abs(t - h) > STAIR_LINK) continue;
        if ((nodesAt.get(j) ?? []).some((m) => inStair.has(m) && Math.abs(nodes[m].h - t) < MERGE)) continue;
        contacts.push([n, t]);
      }
    };
    meet(i);
    around(i, meet);
  }
  // foot and head: the lowest and highest floors it meets along more than a
  // couple of cells (not a stray face)
  const byLevel = new Map();
  for (const [n, t] of contacts) { const k = Math.round(t * 50); if (!byLevel.has(k)) byLevel.set(k, new Set()); byLevel.get(k).add(n); }
  const levels = [...byLevel].filter(([, ns]) => ns.size >= 3).map(([k]) => k / 50);
  if (levels.length < 2) continue;
  const foot = Math.min(...levels), head = Math.max(...levels);
  if (head - foot < 2 * MAX_STEP) continue; // a step or two: walked as it is
  // The cells along the stair's edge that the source treads only graze keep
  // the web model's tread heights: they join the ramp, so its edge is not a
  // row of little steps. A floor or a seating tier beside the stair (flat
  // over several cells) stays as it is.
  const flat = (j, t) => {
    let same = 0;
    around(j, (k) => { if ((tops[k] ?? []).some((u) => Math.abs(u - t) < 0.03)) same++; });
    return same >= 4;
  };
  for (const n of [...stair]) {
    around(nodes[n].i, (j) => {
      for (const t of tops[j] ?? []) {
        if (t <= foot + 0.1 || t >= head - 0.1 || Math.abs(t - nodes[n].h) > STAIR_LINK) continue;
        if ((nodesAt.get(j) ?? []).some((m) => Math.abs(nodes[m].h - t) < MERGE)) continue;
        if (flat(j, t)) continue;
        if (!nodesAt.has(j)) nodesAt.set(j, []);
        nodesAt.get(j).push(nodes.length);
        inStair.add(nodes.length);
        stair.push(nodes.length);
        nodes.push({ i: j, h: t });
      }
    });
  }
  const d0 = along([...new Set(contacts.filter((c) => c[1] - foot < 0.2).map((c) => c[0]))], inStair);
  const d1 = along([...new Set(contacts.filter((c) => head - c[1] < 0.2).map((c) => c[0]))], inStair);
  let set = 0;
  for (const n of stair) {
    const a = d0.get(n), b = d1.get(n);
    if (a === undefined || b === undefined) continue;
    const h = a + b > 0 ? foot + ((head - foot) * a) / (a + b) : foot;
    const { i } = nodes[n];
    if (!ramp.has(i)) ramp.set(i, []);
    ramp.get(i).push([nodes[n].h, h]);
    set++;
  }
  const c = stair.reduce((acc, n) => [acc[0] + (nodes[n].i % W), acc[1] + Math.floor(nodes[n].i / W)], [0, 0]);
  stairs.push({ at: [gx + (c[0] / stair.length + 0.5) * STEP, gz + (c[1] / stair.length + 0.5) * STEP].map((v) => Math.round(v * 10) / 10), foot: Math.round(foot * 100) / 100, head: Math.round(head * 100) / 100, cells: set, of: stair.length, run: Math.round(Math.max(...[...d0.values()].filter(Number.isFinite)) * STEP * 10) / 10 });
}
// the ramp takes the treads' place in the standing heights
const rampAt = new Map(); // cell -> ramp heights (mm)
for (const [i, list] of ramp) {
  let row = tops[i] ?? [];
  for (const [tread, h] of list) {
    row = row.filter((t) => Math.abs(t - tread) >= MERGE && Math.abs(t - h) >= MERGE);
    row.push(h);
  }
  tops[i] = row.sort((a, b) => a - b).slice(-MAX_LAYERS);
  rampAt.set(i, new Set(list.map(([, h]) => Math.round(h * 1000))));
}
const onRamp = (i, h) => rampAt.get(i)?.has(Math.round(h * 1000)) ?? false;

// --- pass 2: anything through the body, from knee to head, in the cell or
// next to it (the visitor's shoulders), blocks that height. On a ramp the
// handrails mark the edge (no shoulder room), and the stair's own treads and
// landings, which the ramp cuts through, only block well above it.
const blocked = new Uint8Array(count); // bit k: tops[i][k] blocked
const AROUND = [0, 1, -1, W, -W];
for (const t of tris) {
  const walked = t[9] === FLOORS;
  cover(t, (j, y0, y1) => {
    for (const d of AROUND) {
      const i = j + d, list = tops[i];
      if (!list) continue;
      for (let k = 0; k < list.length; k++) {
        const h = list[k], r = onRamp(i, h);
        if (r && d) continue;
        if (y1 > h + (r && walked ? RAMP_KNEE : KNEE) && y0 < h + HEAD) blocked[i] |= 1 << k;
      }
    }
  });
}
const stand = [];
for (let i = 0; i < count; i++) tops[i]?.forEach((h, k) => { if (!(blocked[i] & (1 << k))) stand.push([i, Math.round(h * 1000)]); });

// --- layers: heights of one cell, lowest first
const cells = Array.from({ length: count }, () => null);
for (const [i, mm] of stand) (cells[i] ??= []).push(mm);
let layersUsed = 0;
for (const list of cells) if (list) layersUsed = Math.max(layersUsed, Math.min(MAX_LAYERS, list.length));
const layers = Array.from({ length: layersUsed }, () => ({ rows: Array.from({ length: H }, () => []) }));
for (let row = 0; row < H; row++) {
  for (let k = 0; k < layersUsed; k++) {
    const runs = layers[k].rows[row];
    for (let col = 0; col < W; col++) {
      const h = cells[row * W + col]?.[k];
      if (h === undefined) continue;
      const last = runs[runs.length - 1];
      if (last && last[0] + last[1] === col && last[2] === h) last[1]++;
      else runs.push([col, 1, h]);
    }
  }
}

const data = {
  grid: { x: Math.round(gx * 1000) / 1000, z: Math.round(gz * 1000) / 1000, step: STEP, width: W, height: H },
  eye_height_m: EYE,
  maximum_step_m: MAX_STEP,
  layers,
};
fs.writeFileSync(out, JSON.stringify(data));
const n = stand.length;
const byStorey = { '-1': 0, '0': 0, '+1': 0, other: 0 };
for (const [, mm] of stand) {
  const h = mm / 1000;
  if (h > -6 && h < -3) byStorey['-1']++; else if (h > -0.6 && h < 1) byStorey['0']++; else if (h > 4.3 && h < 5.5) byStorey['+1']++; else byStorey.other++;
}
for (const st of stairs) console.log('ramp', JSON.stringify(st));
console.log('stair parts', [...stairNames].sort().join(' '));
console.log(`walk: ${tris.length} triangles (${walkTris} walkable faces), grid ${W} x ${H} at ${STEP} m, ${n} standing cells (${(n * STEP * STEP).toFixed(0)} m²), ${layersUsed} layers`, byStorey, `${(fs.statSync(out).size / 1024).toFixed(0)} kB`);
