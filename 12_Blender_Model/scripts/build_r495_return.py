import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R494_PAVYON_DIS_ISTINAT_ADAY_v001.blend'));D=json.loads((R/'reports/R495_RETURN_PROFILE.json').read_text());A=Vector(D['start']);B=Vector(D['end']);t=(B-A).normalized();n=Vector((-t.y,t.x));length=(B-A).length;old=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];oldvs=[v.co.copy() for v in old.data.vertices];vs=[tuple(v) for v in oldvs[-4:]];fs=[];foot=[];back=[]
# Exact inherited end ring prevents cracks at the wall turn.
foot.append(tuple(oldvs[-4][:2]));back.append(tuple(oldvs[-2][:2]))
for s in [1.5,6,12,18,length]:
 p=A+t*s;z=D['coefficients'][0]+D['coefficients'][1]*s+.08;front=p-n*1.1;rear=p;lower=front-n*.35;vs.extend([(lower.x,lower.y,-9),(rear.x,rear.y,-9),(rear.x,rear.y,z),(front.x,front.y,z)]);foot.append(tuple(lower));back.append(tuple(rear))
for i in range(len(vs)//4-1):
 for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
fs.extend([(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]);me=bpy.data.meshes.new('R495_SOUTH_OUTER_WALL_EAST_RETURN');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(check.values()),check;ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';ob['source']='Independent OSM838550868 east return, road-backed crest with20withheld control cells RMS.01774m/max.03315m. Cap offset0.08m, width1.1m, underground closure-9m and modest batter are construction candidates, not surveyed.';me.materials.append(bpy.data.materials['R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE']);uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
for p in me.polygons:
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((Vector((v.x,v.y))-A).dot(t)/4,v.z/3) if abs(p.normal.z)<.8 else(v.x/4,v.y/3)
poly=foot+list(reversed(back));tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else(i.x,i.y) for i in f]for f in tris];records=[]
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
    if ob.type != 'MESH' or ob.hide_render or not (ob.name in ['R152_CLASS2_TERRAIN','R152_FORECOURT_0'] or ob.name.startswith('R152_PATH_')):
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



out=R/'scenes/MUDAM_R495_PAVYON_DIS_SUR_DONUS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));old=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];new=bpy.data.objects['R495_SOUTH_OUTER_WALL_EAST_RETURN'];gap=max((old.data.vertices[len(old.data.vertices)-4+i].co-new.data.vertices[i].co).length for i in range(4));assert gap<1e-6;(R/'reports/R495_BUILD.json').write_text(json.dumps(dict(check=check,cuts=records,reopened=True,sharedEndRingMaxGap=gap,accepted=False,published=False,limits=['Measured road-backed crest is not whole wall source-fidelity proof.','West termination and terrain-to-foot visual acceptance remain pending.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=680;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(90,-105,55));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((28,-36,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.filepath=str(R/'renders/qa/R495_pavilion_candidate.png');bpy.ops.render.render(write_still=True)
