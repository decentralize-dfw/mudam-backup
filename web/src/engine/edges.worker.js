// Feature edges of a triangle mesh, for the line drawing (wire mode): edges
// where the two faces meet at more than the threshold angle, and open edges.
// Vertices are matched by position (and by _piece, so an edge never joins two
// parts that move apart), because decoded meshes split vertices at every
// normal seam. Returns pairs of ORIGINAL vertex indices, so the lines can reuse
// the mesh's own position and _piece attributes. Open-addressing tables on
// typed arrays keep it fast on meshes of a million triangles.
self.onmessage = (e) => {
  const { id, pos, index, piece, cos } = e.data;
  const nv = pos.length / 3;
  const nt = index ? index.length / 3 : nv / 3;
  const vi = (t, k) => (index ? index[t * 3 + k] : t * 3 + k);

  // quantised key per vertex: x, y, z in mm, plus the piece (centre, layer)
  const K = piece ? 6 : 3;
  const key = new Int32Array(nv * K);
  for (let v = 0; v < nv; v++) {
    key[v * K] = Math.round(pos[v * 3] * 1000);
    key[v * K + 1] = Math.round(pos[v * 3 + 1] * 1000);
    key[v * K + 2] = Math.round(pos[v * 3 + 2] * 1000);
    if (piece) {
      key[v * K + 3] = Math.round(piece[v * 4] * 100);
      key[v * K + 4] = Math.round(piece[v * 4 + 2] * 100);
      key[v * K + 5] = Math.round(piece[v * 4 + 3]);
    }
  }
  const same = (a, b) => { for (let k = 0; k < K; k++) if (key[a * K + k] !== key[b * K + k]) return false; return true; };
  let size = 1;
  while (size < nv * 2) size <<= 1;
  const mask = size - 1;
  const table = new Int32Array(size).fill(-1);
  const canon = new Int32Array(nv);
  for (let v = 0; v < nv; v++) {
    let h = 0;
    for (let k = 0; k < K; k++) h = Math.imul(h ^ key[v * K + k], 0x9e3779b1) ^ (h >>> 15);
    let s = (h >>> 0) & mask;
    for (;;) {
      const u = table[s];
      if (u === -1) { table[s] = v; canon[v] = v; break; }
      if (same(u, v)) { canon[v] = u; break; }
      s = (s + 1) & mask;
    }
  }

  // face normals
  const normal = new Float32Array(nt * 3);
  for (let t = 0; t < nt; t++) {
    const a = vi(t, 0) * 3, b = vi(t, 1) * 3, c = vi(t, 2) * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const wx = pos[c] - pos[a], wy = pos[c + 1] - pos[a + 1], wz = pos[c + 2] - pos[a + 2];
    const nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
    const l = Math.hypot(nx, ny, nz) || 1;
    normal[t * 3] = nx / l; normal[t * 3 + 1] = ny / l; normal[t * 3 + 2] = nz / l;
  }

  // undirected edges: canonical ends -> first face, its vertices, second face
  let esize = 1;
  while (esize < nt * 6) esize <<= 1;
  const emask = esize - 1;
  const eslot = new Int32Array(esize).fill(-1);
  const ea = new Int32Array(nt * 3), eb = new Int32Array(nt * 3), ef = new Int32Array(nt * 3), eva = new Int32Array(nt * 3), evb = new Int32Array(nt * 3), eg = new Int32Array(nt * 3);
  let ne = 0;
  for (let t = 0; t < nt; t++) {
    for (let k = 0; k < 3; k++) {
      const va = vi(t, k), vb = vi(t, (k + 1) % 3);
      let a = canon[va], b = canon[vb];
      if (a === b) continue;
      if (a > b) { const x = a; a = b; b = x; }
      let s = ((Math.imul(a, 0x9e3779b1) ^ Math.imul(b, 0x85ebca6b)) >>> 0) & emask;
      for (;;) {
        const r = eslot[s];
        if (r === -1) {
          eslot[s] = ne;
          ea[ne] = a; eb[ne] = b; ef[ne] = t; eg[ne] = -1; eva[ne] = va; evb[ne] = vb;
          ne++;
          break;
        }
        if (ea[r] === a && eb[r] === b) { eg[r] = eg[r] === -1 ? t : -2; break; }
        s = (s + 1) & emask;
      }
    }
  }
  const out = new Uint32Array(ne * 2);
  let n = 0;
  for (let r = 0; r < ne; r++) {
    const t = ef[r], u = eg[r];
    if (u >= 0) {
      const d = normal[t * 3] * normal[u * 3] + normal[t * 3 + 1] * normal[u * 3 + 1] + normal[t * 3 + 2] * normal[u * 3 + 2];
      if (d > cos) continue;
    }
    out[n++] = eva[r]; out[n++] = evb[r];
  }
  const result = out.slice(0, n);
  self.postMessage({ id, edges: result }, [result.buffer]);
};
