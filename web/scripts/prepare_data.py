"""Mudam web data: section caps, rooms, hanging walls, artwork layout, site context.

Reads the same source as build-model.mjs (12_Blender_Model/exports/current.glb.gz)
and writes demo/data/*.json. Everything here is derived from the model and the
OSM extract already in the repository; nothing is measured on site.

    python3 -I web/scripts/prepare_data.py
"""
import gzip, io, json, math, os, random, re, sys
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union, polylabel
import mapbox_earcut as earcut

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(REPO, '12_Blender_Model/exports/current.glb.gz')
OSM = [os.path.join(REPO, '10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri', f) for f in ('mudam_osm.osm', 'mudam_osm_dogu.osm')]
OUT = os.path.join(REPO, 'demo/data')
os.makedirs(OUT, exist_ok=True)

# Model frame: x = easting - 293425, z = -(northing - 5499960), y up (glTF).
ORIGIN_E, ORIGIN_N = 293425.0, 5499960.0

# Registered floor tops in the model and the heights the web view cuts at.
FLOORS = {
    'LM1': {'floor': -5.33, 'cut': -2.35},
    'L00': {'floor': 0.0, 'cut': 3.0},
    'LP1': {'floor': 4.86, 'cut': 7.95},
}
# Explode bands: what each floor keeps when the building is taken apart.
BANDS = [
    {'id': 'LM1', 'lo': None, 'hi': -2.35},
    {'id': 'L00', 'lo': -0.15, 'hi': 3.0},
    {'id': 'LP1', 'lo': 4.55, 'hi': 7.95},
    {'id': 'ROOF', 'lo': 7.95, 'hi': None},
]


def load_nodes():
    raw = gzip.decompress(open(SRC, 'rb').read())
    scene = trimesh.load(io.BytesIO(raw), file_type='glb', force='scene', process=False)
    # node extras are not carried by trimesh; read them from the glTF JSON
    import struct
    clen = struct.unpack('<I', raw[12:16])[0]
    gj = json.loads(raw[20:20 + clen])
    extras = {n.get('name'): n.get('extras', {}) for n in gj['nodes']}
    recs = []
    for node in scene.graph.nodes_geometry:
        T, gname = scene.graph[node]
        g = scene.geometry[gname]
        if not hasattr(g, 'faces') or len(g.faces) == 0:
            continue
        base = re.sub(r'_[0-9a-f]{6}$', '', node)
        e = extras.get(node) or extras.get(base) or {}
        mat = getattr(getattr(g.visual, 'material', None), 'name', '') or ''
        recs.append(dict(name=base, level=e.get('level_id', '?'), zone=e.get('zone_id', '?'), mat=mat,
                         mesh=trimesh.Trimesh(trimesh.transform_points(g.vertices, T), g.faces, process=False)))
    # A node with several materials arrives as one primitive per material; a
    # wall box split that way has no closed loop to cut. Rejoin per node.
    merged = {}
    for r in recs:
        merged.setdefault(r['name'], []).append(r)
    out = []
    for name, parts in merged.items():
        r = dict(parts[0])
        if len(parts) > 1:
            m = trimesh.util.concatenate([p['mesh'] for p in parts])
            m.merge_vertices(digits_vertex=5)
            r['mesh'] = m
        out.append(r)
    return out


def is_context(r):
    return r['level'] in ('SITE', 'L00_APPROACH') or r['name'].startswith(('R56_TREE', 'R38_TREE'))


TO2D = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float)


def section_polygons(recs, h, include=lambda r: True, with_lines=False):
    """Closed section loops of every solid the plane y=h passes through.

    Some envelope parts are still single surfaces in the source model; their
    cut is an open line rather than a loop. Those come back separately so the
    drawing can show them as lines and the hanging logic can treat them as walls.
    """
    polys, lines = [], []
    for r in recs:
        if not include(r):
            continue
        m = r['mesh']
        lo, hi = m.bounds[0][1], m.bounds[1][1]
        if not (lo < h < hi):
            continue
        try:
            path = m.section(plane_origin=[0, h, 0], plane_normal=[0, 1, 0])
        except Exception:
            continue
        if path is None:
            continue
        p2, _ = path.to_2D(to_2D=TO2D)
        closed = [poly for poly in p2.polygons_full if poly is not None and poly.is_valid and poly.area > 1e-4]
        polys += closed
        if with_lines and not closed:
            for d in p2.discrete:
                if len(d) >= 2 and LineString(d).length > 0.3:
                    lines.append(LineString(d))
    u = unary_union(polys).buffer(0.004, join_style=2).buffer(-0.004, join_style=2) if polys else MultiPolygon()
    u = u.simplify(0.003, preserve_topology=True)
    if with_lines:
        return u, lines
    return u


def triangulate(geom):
    pos, idx = [], []
    geoms = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for g in geoms:
        if g.is_empty or g.area < 1e-4:
            continue
        rings = [np.asarray(g.exterior.coords)[:-1]] + [np.asarray(i.coords)[:-1] for i in g.interiors]
        verts = np.concatenate(rings)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        tri = earcut.triangulate_float64(verts, ends)
        base = len(pos) // 2
        pos.extend(np.round(verts, 3).ravel().tolist())
        idx.extend((np.asarray(tri) + base).tolist())
    return pos, idx


def outlines(geom):
    lines = []
    geoms = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for g in geoms:
        if g.is_empty:
            continue
        for ring in [g.exterior, *g.interiors]:
            lines.append(np.round(np.asarray(ring.coords), 3).ravel().tolist())
    return lines


# ---------------------------------------------------------------- rooms
ROOMS = [
    # id, floor, label (plan name), source floor meshes, kind
    ('grand-hall', 'L00', 'Grand Hall', ['P05_FLOOR_L00_GH'], 'hall'),
    ('galerie-est-0', 'L00', 'Galerie Est', ['P05_FLOOR_L00_E0', 'R28_E_CIRCULATION_FLOOR'], 'gallery'),
    ('galerie-ouest-0', 'L00', 'Galerie Ouest', ['P05_FLOOR_L00_W0', 'R28_W_CIRCULATION_FLOOR'], 'gallery'),
    ('jardin-sculptures', 'L00', 'Jardin des Sculptures', ['P05_FLOOR_L00_EAST_GARDEN'], 'glasshall'),
    ('cafe', 'L00', 'Mudam Café', ['P05_FLOOR_L00_WEST_CAFE'], 'cafe'),
    ('entree', 'L00', 'Entrée', ['P05_FLOOR_L00_ENT', 'R33_FLOOR_CLOAK'], 'service'),
    ('pavillon', 'L00', 'Pavillon', ['R17_GROUND_FLOOR'], 'pavilion'),
    ('passage', 'L00', 'Passage', ['P05_LINK_FLOOR'], 'link'),
    ('galerie-est-1', 'LP1', 'Galerie Est', ['P05_FLOOR_LP1_E0'], 'gallery'),
    ('galerie-ouest-1', 'LP1', 'Galerie Ouest', ['P05_FLOOR_LP1_W0'], 'gallery'),
    ('petite-galerie-ouest', 'LP1', 'Petite Galerie Ouest', ['R87_UPPER_FLOOR'], 'gallery'),
    ('studio', 'LP1', 'Studio', ['P05_FLOOR_LP1_STUDIO'], 'service'),
    ('documentation', 'LP1', 'Espace de documentation', ['P17_READING_FLOOR', 'R96_DOCUMENTATION_EAST_FLOOR'], 'service'),
    ('pont', 'LP1', 'Passerelle', ['P05_FLOOR_LP1_BRIDGE'], 'link'),
    ('galerie-est-m1', 'LM1', 'Galerie Est', ['R29_E_FLOOR'], 'gallery'),
    ('foyer', 'LM1', 'Foyer', ['R29_FOYER_FLOOR'], 'gallery'),
    ('galerie-ouest-m1', 'LM1', 'Galerie Ouest', ['R29_W_FLOOR'], 'gallery'),
    ('auditorium', 'LM1', 'Auditorium', ['R19_ROOM_FLOOR'], 'service'),
    ('pavillon-m1', 'LM1', 'Pavillon −1', ['R25_LOWER_PAVILION_FLOOR'], 'pavilion'),
]


def floor_polygon(recs, names):
    parts = []
    for r in recs:
        if r['name'] not in names:
            continue
        m = r['mesh']
        tri = m.vertices[m.faces]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nl = np.linalg.norm(n, axis=1) + 1e-12
        up = (n[:, 1] / nl) > 0.9
        ps = [Polygon(t[:, [0, 2]]) for t in tri[up]]
        parts += [p for p in ps if p.area > 1e-6]
    u = unary_union(parts).buffer(0.02, join_style=2).buffer(-0.02, join_style=2)
    if hasattr(u, 'geoms'):
        u = max(u.geoms, key=lambda g: g.area) if len(u.geoms) else u
    return u.simplify(0.02, preserve_topology=True)


def hanging_walls(room_poly, solids, min_len):
    """Wall faces bounding a room at hanging height: free floor edges backed by solid."""
    reach = room_poly.buffer(1.6, join_style=2).intersection(room_poly.convex_hull.buffer(1.6, join_style=2))
    free = reach.difference(solids)
    if hasattr(free, 'geoms'):
        free = max(free.geoms, key=lambda g: g.intersection(room_poly).area)
    from shapely.geometry.polygon import orient as orient_poly
    free = orient_poly(free.simplify(0.04, preserve_topology=True), 1.0)
    walls = []
    # exterior ring ccw, holes cw: the free floor is always on the left
    edges = []
    for ring in [free.exterior, *free.interiors]:
        c = list(ring.coords)
        edges += list(zip(c[:-1], c[1:]))
    for (x0, z0), (x1, z1) in edges:
        L = math.hypot(x1 - x0, z1 - z0)
        if L < min_len:
            continue
        tx, tz = (x1 - x0) / L, (z1 - z0) / L
        nx, nz = -tz, tx
        # the wall must face into this room, not the next one through a doorway
        hits = 0
        for f in (0.2, 0.35, 0.5, 0.65, 0.8):
            px, pz = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
            behind = solids.contains(Point(px - nx * 0.12, pz - nz * 0.12))
            # the face must look into this room: probing inward along the
            # normal has to reach the room's own floor (a wall's outer face,
            # or a face seen through a doorway, never does)
            inside = any(room_poly.contains(Point(px + nx * d, pz + nz * d)) for d in (0.5, 1.0, 1.6, 2.2))
            if behind and inside:
                hits += 1
        if hits >= 4:
            walls.append(dict(a=[round(x0, 3), round(z0, 3)], b=[round(x1, 3), round(z1, 3)], n=[round(nx, 4), round(nz, 4)], length=round(L, 3)))
    return walls, free


# ------------------------------------------------------- artwork layout
# How each exhibition dresses a wall: (min width, max width, aspect choices, gap).
STYLE = {
    'kaiho': dict(w=(0.7, 2.1), aspects=[0.75, 1.0, 1.33, 0.8, 1.5, 0.66], gap=(1.0, 1.7), centre=1.55, floor_items=3),
    'vktrs': dict(w=(0.8, 2.4), aspects=[1.33, 1.5, 0.75, 1.0, 1.78], gap=(0.9, 1.5), centre=1.6, floor_items=3),
    'forever': dict(w=(2.6, 3.0), aspects=[0.8], gap=(0.6, 0.6), centre=1.85, floor_items=0, per_wall=1),
}


def layout_wall(wall, style, rng, floor_y):
    L = wall['length']
    usable = L - 1.0
    items = []
    if usable < 0.8:
        return items
    # pick works until the wall is full, then centre the run
    picks, total = [], 0
    while True:
        w = rng.uniform(*style['w'])
        a = rng.choice(style['aspects'])
        h = min(w / a, 2.6)
        w = h * a
        g = rng.uniform(*style['gap'])
        if total + w + (g if picks else 0) > usable:
            break
        total += w + (g if picks else 0)
        picks.append((w, h, g))
        if len(picks) >= style.get('per_wall', 10):
            break
    if not picks:
        w = min(usable, style['w'][1])
        a = style['aspects'][0]
        picks = [(w, min(w / a, 2.6), 0)]
        total = w
    s = 0.5 + (usable - total) / 2
    ax, az = wall['a']; bx, bz = wall['b']
    tx, tz = (bx - ax) / L, (bz - az) / L
    for i, (w, h, g) in enumerate(picks):
        if i:
            s += g
        c = s + w / 2
        s += w
        cy = floor_y + max(style['centre'], h / 2 + 0.35)
        items.append(dict(pos=[round(ax + tx * c + wall['n'][0] * 0.03, 3), round(cy, 3), round(az + tz * c + wall['n'][1] * 0.03, 3)],
                          normal=[wall['n'][0], 0, wall['n'][1]], w=round(w, 3), h=round(h, 3), kind='wall'))
    return items


def floor_spots(free, room_poly, count, rng, clearance=2.2):
    region = free.intersection(room_poly).buffer(-clearance)
    if region.is_empty:
        return []
    spots, tries = [], 0
    minx, minz, maxx, maxz = region.bounds
    while len(spots) < count and tries < 4000:
        tries += 1
        p = Point(rng.uniform(minx, maxx), rng.uniform(minz, maxz))
        if region.contains(p) and all(p.distance(q) > 4.2 for q in spots):
            spots.append(p)
    return spots


def main():
    recs = load_nodes()
    building = [r for r in recs if not is_context(r)]
    print('nodes', len(recs), 'building', len(building))

    # ---------------- section caps at the three floor cuts
    sections = []
    for fid, f in FLOORS.items():
        g, open_lines = section_polygons(building, f['cut'], with_lines=True)
        pos, idx = triangulate(g)
        segs = [np.round(np.asarray(l.coords), 3).ravel().tolist() for l in open_lines]
        sections.append(dict(id=fid, y=f['cut'], p=pos, i=idx, lines=outlines(g) + segs))
        print('section', fid, f['cut'], 'area', round(g.area, 1), 'tris', len(idx) // 3)
    json.dump(dict(coordinate_system='model x,z (y up)', floors=FLOORS, bands=BANDS, cuts=sections),
              open(os.path.join(OUT, 'sections.json'), 'w'), separators=(',', ':'))

    # ---------------- rooms + hanging walls
    solids_at = {}
    def wall_solids(h):
        g, open_lines = section_polygons(building, h, with_lines=True)
        return unary_union([g] + [l.buffer(0.09, cap_style=2) for l in open_lines])
    for fid, f in FLOORS.items():
        solids_at[fid] = wall_solids(f['floor'] + 1.5)
    # the pavilion's lower floor and the ground pavilion sit on their own datum
    rooms = []
    for rid, fid, label, names, kind in ROOMS:
        poly = floor_polygon(building, set(names))
        fy = FLOORS[fid]['floor']
        if rid == 'pavillon-m1':
            fy = -3.83
        anchor = polylabel(poly, 0.05)
        room = dict(id=rid, floor=fid, label=label, kind=kind, y=fy,
                    polygon=np.round(np.asarray(poly.exterior.coords)[:-1], 3).tolist(),
                    anchor=[round(anchor.x, 3), round(anchor.y, 3)])
        if kind in ('gallery', 'pavilion', 'hall', 'glasshall'):
            solids = solids_at[fid] if rid != 'pavillon-m1' else wall_solids(fy + 1.5)
            walls, free = hanging_walls(poly, solids, 2.2)
            room['walls'] = walls
            room['_free'] = free
        rooms.append(room)
        print('room', rid, kind, round(poly.area, 1), len(room.get('walls', [])))

    # ---------------- artwork layout per exhibition room
    EXHIBITION_ROOMS = {
        'kaiho': ['galerie-est-0', 'galerie-ouest-0', 'grand-hall', 'jardin-sculptures', 'galerie-est-1', 'galerie-ouest-1', 'petite-galerie-ouest'],
        'vktrs': ['galerie-est-m1', 'foyer', 'galerie-ouest-m1'],
        'forever': ['pavillon'],
    }
    by_id = {r['id']: r for r in rooms}
    artworks = []
    for ex, room_ids in EXHIBITION_ROOMS.items():
        style = STYLE[ex]
        n = 0
        for rid in room_ids:
            room = by_id[rid]
            rng = random.Random(f'{ex}:{rid}')
            poly = Polygon(room['polygon'])
            placed = []
            if room['kind'] in ('gallery', 'pavilion'):
                walls = sorted(room['walls'], key=lambda w: -w['length'])
                if ex == 'forever':
                    # four walls of sculptural canvases: every other face of
                    # the octagon, starting from the one opposite the passage
                    cx, cz = poly.centroid.x, poly.centroid.y
                    ang = lambda w: math.atan2((w['a'][1] + w['b'][1]) / 2 - cz, (w['a'][0] + w['b'][0]) / 2 - cx)
                    faces = sorted([w for w in walls if w['length'] > 3.0], key=ang)
                    walls = faces[0::2][:4] if len(faces) >= 7 else faces[:4]
                for w in walls:
                    placed += layout_wall(w, style, rng, room['y'])
                spots = floor_spots(room['_free'], poly, style['floor_items'] if poly.area > 150 else 1 if poly.area > 60 else 0, rng)
            else:
                # Grand Hall and the glazed garden carry floor pieces only
                spots = floor_spots(room['_free'], poly, 4 if room['kind'] == 'glasshall' else 2, rng, clearance=3.0)
            for p in spots:
                s = rng.uniform(1.0, 1.8)
                h = rng.uniform(1.1, 2.4)
                placed.append(dict(pos=[round(p.x, 3), round(room['y'] + h / 2 + 0.25, 3), round(p.y, 3)], normal=None,
                                   w=round(s, 3), h=round(h, 3), kind=rng.choice(['plinth', 'vitrine', 'standing'])))
            # order works as a visitor meets them: along the walls in turn
            for a in placed:
                n += 1
                a.update(id=f'{ex}-{n:03d}', exhibition=ex, room=rid, index=n, seed=rng.randrange(1 << 30))
                artworks.append(a)
        print('exhibition', ex, n)
    for r in rooms:
        r.pop('_free', None)
    json.dump(dict(floors=FLOORS, rooms=rooms), open(os.path.join(OUT, 'rooms.json'), 'w'), separators=(',', ':'))
    json.dump(dict(artworks=artworks), open(os.path.join(OUT, 'artworks.json'), 'w'), separators=(',', ':'))

    # ---------------- site context from OSM
    context(recs)


# ------------------------------------------------------------------ OSM

def utm32(lat, lon):
    a = 6378137.0; f = 1 / 298.257223563; k0 = 0.9996; e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    lon0 = math.radians(9); phi = math.radians(lat); lam = math.radians(lon)
    N = a / math.sqrt(1 - e2 * math.sin(phi) ** 2); T = math.tan(phi) ** 2; C = ep2 * math.cos(phi) ** 2; A = math.cos(phi) * (lam - lon0)
    e4 = e2 * e2; e6 = e4 * e2
    M = a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * phi - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * phi)
             + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * phi) - (35 * e6 / 3072) * math.sin(6 * phi))
    x = k0 * N * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5 / 120) + 500000
    y = k0 * (M + N * math.tan(phi) * (A * A / 2 + (5 - T + 9 * C + 4 * C * C) * A ** 4 / 24 + (61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6 / 720))
    return x - ORIGIN_E, -(y - ORIGIN_N)


# Buildings on the Kirchberg plateau around the museum. The valley quarters
# (Pfaffenthal, Clausen, the old town) lie 40-60 m lower; drawing them on the
# plateau's level would be wrong, so the massing stops at the plateau edge.
def on_plateau(x, z):
    return math.hypot(x, z) < 430 and x > -150 and not (z > 140 and x < 60) and z < 260


def context(recs):
    ways, nodes = {}, {}
    for fn in OSM:
        root = ET.parse(fn).getroot()
        for n in root.iter('node'):
            nodes[n.get('id')] = (float(n.get('lat')), float(n.get('lon')))
        for w in root.iter('way'):
            ways[w.get('id')] = w
    buildings, lines = [], []
    for wid, w in ways.items():
        tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
        pts = [nodes[nd.get('ref')] for nd in w.findall('nd') if nd.get('ref') in nodes]
        if len(pts) < 2:
            continue
        xz = [utm32(*p) for p in pts]
        cx = sum(p[0] for p in xz) / len(xz); cz = sum(p[1] for p in xz) / len(xz)
        if 'building' in tags and len(xz) >= 4:
            if tags.get('name') == 'MUDAM' or not on_plateau(cx, cz):
                continue
            # the museum itself and its pavilion come from the model
            if abs(cx) < 50 and abs(cz) < 60:
                continue
            if 'height' in tags:
                try:
                    h = float(re.sub('[^0-9.]', '', tags['height']))
                except ValueError:
                    h = 12.0
            elif 'building:levels' in tags:
                h = float(re.sub('[^0-9.]', '', tags['building:levels']) or 3) * 3.3
            else:
                h = 9.0 if tags.get('building') not in ('ruins', 'roof') else 3.0
            poly = Polygon(xz)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if poly.is_empty or poly.area < 6:
                continue
            if hasattr(poly, 'geoms'):
                poly = max(poly.geoms, key=lambda g: g.area)
            buildings.append(dict(id=wid, name=tags.get('name'), h=round(h, 1), kind=tags.get('building'),
                                  p=np.round(np.asarray(poly.exterior.coords)[:-1], 2).ravel().tolist()))
        else:
            kind = None
            if 'highway' in tags:
                kind = 'road' if tags['highway'] in ('primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'service', 'living_street', 'trunk') else 'path'
            elif tags.get('railway') in ('tram', 'rail', 'funicular'):
                kind = 'rail'
            elif tags.get('barrier') in ('city_wall', 'retaining_wall', 'wall') or tags.get('historic') == 'citywalls':
                kind = 'wall'
            elif tags.get('leisure') == 'park' or tags.get('landuse') in ('grass', 'village_green', 'forest') or tags.get('natural') in ('wood', 'scrub'):
                kind = 'green'
            if kind and math.hypot(cx, cz) < 700:
                lines.append(dict(kind=kind, name=tags.get('name'), p=np.round(np.asarray(xz), 1).ravel().tolist()))
    # trees: canopy volumes of the source foliage (the leaf meshes themselves
    # are too dense for the web and are replaced by light canopies)
    trees = {}
    for r in recs:
        m = re.match(r'R56_TREE_(\d+)_LEAVES', r['name'])
        if not m:
            continue
        lo, hi = r['mesh'].bounds
        t = trees.setdefault(m.group(1), [lo.copy(), hi.copy()])
        t[0] = np.minimum(t[0], lo); t[1] = np.maximum(t[1], hi)
    tree_list = [dict(c=np.round((lo + hi) / 2, 2).tolist(), s=np.round((hi - lo) / 2, 2).tolist()) for lo, hi in trees.values()]
    json.dump(dict(buildings=buildings, trees=tree_list), open(os.path.join(OUT, 'context.json'), 'w'), separators=(',', ':'))
    print('context buildings', len(buildings), 'lines', len(lines), 'trees', len(tree_list))
    # holes in the ground drawing: the museum footprint and the two moats,
    # which lie several metres below the plateau
    holes = []
    mudam = None
    for wid, w in ways.items():
        tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
        if tags.get('name') == 'MUDAM':
            pts = [utm32(*nodes[nd.get('ref')]) for nd in w.findall('nd') if nd.get('ref') in nodes]
            mudam = Polygon(pts).buffer(0.6, join_style=2)
    parts = [mudam] if mudam else []
    parts.append(floor_polygon(recs, {'R35_MOAT_GROUND', 'R68_MOAT_GROUND'}).buffer(0.3, join_style=2))
    u = unary_union(parts).simplify(0.05)
    for g in (u.geoms if hasattr(u, 'geoms') else [u]):
        holes.append(np.round(np.asarray(g.exterior.coords)[:-1], 2).tolist())
    ground_texture(lines, holes)


def ground_texture(lines, holes):
    """A quiet site-plan drawing for the ground disc: parks, roads, paths, walls."""
    from PIL import Image, ImageDraw, ImageFilter
    R = 600.0  # metres from the museum to the texture edge
    S = 4096
    k = S / (2 * R)
    im = Image.new('RGB', (S, S), (226, 224, 216))
    d = ImageDraw.Draw(im)

    def px(x, z):
        return ((x + R) * k, (z + R) * k)
    for l in lines:
        if l['kind'] == 'green' and len(l['p']) >= 6:
            pts = [px(l['p'][i], l['p'][i + 1]) for i in range(0, len(l['p']), 2)]
            d.polygon(pts, fill=(205, 212, 192))
    widths = {'road': 7.5, 'path': 2.2, 'rail': 2.0, 'wall': 1.1}
    colours = {'road': (240, 239, 234), 'path': (236, 233, 224), 'rail': (178, 176, 170), 'wall': (150, 140, 124)}
    for kind in ('path', 'road', 'rail', 'wall'):
        for l in lines:
            if l['kind'] != kind:
                continue
            pts = [px(l['p'][i], l['p'][i + 1]) for i in range(0, len(l['p']), 2)]
            d.line(pts, fill=colours[kind], width=max(1, int(widths[kind] * k)), joint='curve')
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    os.makedirs(os.path.join(REPO, 'demo/context'), exist_ok=True)
    im.save(os.path.join(REPO, 'demo/context/ground.webp'), quality=82, method=6)
    json.dump(dict(radius=R, holes=holes), open(os.path.join(OUT, 'ground.json'), 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
