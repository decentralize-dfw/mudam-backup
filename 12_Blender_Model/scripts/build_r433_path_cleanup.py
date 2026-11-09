import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R431_KALE_KOPRUSU_AHSAP_KORKULUK_ADAY_v001.blend'))
d=json.loads((R/'reports/R430_FRONT_APPROACH_PLANE.json').read_text());assert d['valid'];poly=d['outline'];plane=d['plane']
tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
captris=list(tri);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tri];records=[]
def clip(points, a, b, sign, inside):
    out = []
    for j, P in enumerate(points):
        Q = points[(j + 1) % len(points)]
        f = lambda X: sign * ((b[0] - a[0]) * (X[1] - a[1]) - (b[1] - a[1]) * (X[0] - a[0]))
        dp = f(P)
        dq = f(Q)
        ip = dp >= -1e-08 if inside else dp <= 1e-08
        iq = dq >= -1e-08 if inside else dq <= 1e-08
        if ip:
            out.append(P)
        if ip != iq:
            t = dp / (dp - dq)
            out.append(tuple((p + (q - p) * t for p, q in zip(P, Q))))
    return out
for ob in list(bpy.context.scene.objects):
    if ob.type != 'MESH' or ob.hide_render or not ob.name.startswith('R152_PATH_'):
        continue
    me = ob.data
    me.calc_loop_triangles()
    uvs = list(me.uv_layers)
    verts = []
    faces = []
    mis = []
    attrs = []
    changed = 0
    for tr in me.loop_triangles:
        points = []
        for li in tr.loops:
            q = ob.matrix_world @ me.vertices[me.loops[li].vertex_index].co
            points.append(tuple(q) + tuple((v for layer in uvs for v in layer.data[li].uv)))
        chunks = [points]
        for region in regions:
            sign = 1 if sum((region[i][0] * region[(i + 1) % len(region)][1] - region[(i + 1) % len(region)][0] * region[i][1] for i in range(len(region)))) > 0 else -1
            result = []
            for chunk in chunks:
                if max((p[0] for p in chunk)) < min((p[0] for p in region)) or min((p[0] for p in chunk)) > max((p[0] for p in region)) or max((p[1] for p in chunk)) < min((p[1] for p in region)) or (min((p[1] for p in chunk)) > max((p[1] for p in region))):
                    result.append(chunk)
                    continue
                remaining = chunk
                for i, a in enumerate(region):
                    if len(remaining) < 3:
                        break
                    b = region[(i + 1) % len(region)]
                    outside = clip(remaining, a, b, sign, False)
                    if len(outside) > 2:
                        result.append(outside)
                    remaining = clip(remaining, a, b, sign, True)
                if len(remaining) > 2:
                    changed += 1
            chunks = result
        for chunk in chunks:
            for i in range(1, len(chunk) - 1):
                tri = [chunk[0], chunk[i], chunk[i + 1]]
                if (Vector(tri[1][:3]) - Vector(tri[0][:3])).cross(Vector(tri[2][:3]) - Vector(tri[0][:3])).length < 1e-08:
                    continue
                k = len(verts)
                verts.extend((tuple(ob.matrix_world.inverted() @ Vector(p[:3])) for p in tri))
                attrs.extend((p[3:] for p in tri))
                faces.append((k, k + 1, k + 2))
                mis.append(tr.material_index)
    if changed:
        new = bpy.data.meshes.new(ob.name + '_COURT_CUT')
        new.from_pydata(verts, [], faces)
        new.update()
        for ma in me.materials:
            new.materials.append(ma)
        for i, ma in enumerate(mis):
            new.polygons[i].material_index = ma
        for j, layer in enumerate(uvs):
            dst = new.uv_layers.new(name=layer.name)
            for l in new.loops:
                dst.data[l.index].uv = attrs[l.vertex_index][j * 2:j * 2 + 2]
        ob.data = new
        records.append(dict(name=ob.name, cutTriangles=changed))

out=R/'scenes/MUDAM_R433_ON_YOL_CAKISMA_TEMIZLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R433_PATH_CLEANUP.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,cuts=records,scope='Only legacy path surfaces inside R430 source-traced approach polygon removed; source-defined moat and bridge preserved.'),indent=2));print('R433_SAVED',records,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-120,-112,52));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-72,-59,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=48;s.render.filepath=str(R/'renders/qa/R433_approach_candidate.png');bpy.ops.render.render(write_still=True)

