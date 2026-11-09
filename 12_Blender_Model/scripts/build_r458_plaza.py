import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R457_KUZEY_SERVIS_AVLUSU_ADAY_v001.blend'))
d=json.loads((R/'reports/R458_WEST_PLAZA_GRADE.json').read_text());assert d['valid'];poly=d['outline'];coef=d['coefficients']
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
    if ob.type != 'MESH' or ob.hide_render or ob.name not in ['R152_CLASS2_TERRAIN','R152_PATH_759551377','R152_PATH_51768376','R152_FORECOURT_0']:
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

n=len(poly);vs=[(x,y,dz) for dz in [0,-.16] for x,y in poly];faces=[]
for f in captris:
 ids=[i if isinstance(i,int) else min(range(n),key=lambda j:(Vector((*poly[j],0))-i).length) for i in f];faces.append(tuple(ids));faces.append(tuple(i+n for i in reversed(ids)))
for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
me=bpy.data.meshes.new('R458_WEST_SERVICE_PLAZA');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=12,use_grid_fill=True)
for v in bm.verts:
 x,y,z=v.co;v.co.z=z+coef[0]+coef[1]*x+coef[2]*y+coef[3]*x*x+coef[4]*x*y+coef[5]*y*y
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);o['level_id']='SITE';o['source']='R457 analytical grade, source outline, 28 held-out cells RMS .0194m; no scan geometry'
m=bpy.data.materials.new('R458_WEST_PLAZA_MINERAL');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.38,.36,.31,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9;me.materials.append(m)
# Superseded approximate forecourt and straight strip: the source shows one mineral court.
retired=[]
for name in ['R152_FORECOURT_0','R152_PATH_51768376']:
 ob=bpy.data.objects.get(name)
 if ob:
  bounds=[ob.matrix_world@Vector(c) for c in ob.bound_box]
  if name.startswith('R152_PATH_'):
   assert min(v.x for v in bounds)>-75 and max(v.x for v in bounds)<25,(name,[tuple(v) for v in bounds])
  ob.hide_render=True;ob.hide_viewport=True;retired.append(name)
out=R/'scenes/MUDAM_R458_BATI_SERVIS_AVLU_KOTU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));o=bpy.data.objects['R458_WEST_SERVICE_PLAZA'];bm=bmesh.new();bm.from_mesh(o.data);check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert not any(check.values());(R/'reports/R458_PLAZA_BUILD.json').write_text(json.dumps(dict(scene=out.name,check=check,cuts=records,retired=retired,source=d['check'],accepted=False,published=False,limits=['Perimeter terrain transitions and west entry path need visual verification; source boundary not cadastral survey.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-28,48,95));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-28,48,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.filepath=str(R/'renders/qa/R458_service_plaza.png');bpy.ops.render.render(write_still=True)
