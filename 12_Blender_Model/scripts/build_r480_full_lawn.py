import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend'));d=json.loads((R/'reports/R480_NW_LAWN_MODEL.json').read_text());domain=json.loads((R/'reports/R474_FULL_LAWN_DOMAIN.json').read_text());poly=domain['outline'];vs=[];fs=[]
for name in ['R152_CLASS2_TERRAIN','R152_FORECOURT_0']:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();k=len(vs);vs.extend(ob.matrix_world@v.co for v in me.vertices);fs.extend([[k+i for i in f.vertices] for f in me.loop_triangles])
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
zs=[];contacts=[]
for x,y in domain['vertices']:
 z=max(c[0]+c[1]*(x+51)+c[2]*(y-35) for c in d['planes']); cap=d['westCrestCap']; z=min(z,cap[0]+cap[1]*(y-35));zs.append(z)
# Fit the inherited planar UV map to preserve the surrounding grass texture scale.
o=bpy.data.objects['R152_CLASS2_TERRAIN'];me=o.data;U=[];X=[]
if me.uv_layers:
 for li in range(0,len(me.loops),max(1,len(me.loops)//1000)):
  v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;X.append([v.x,v.y,1]);U.append(list(me.uv_layers.active.data[li].uv))
uvcoef=np.linalg.lstsq(np.array(X),np.array(U),rcond=None)[0] if X else np.array([[.1,0],[0,.1],[0,0]])
uvrms=float(np.sqrt(np.mean((np.array(X)@uvcoef-np.array(U))**2))) if X else None
tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tri];records=[]
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
    if ob.type != 'MESH' or ob.hide_render or ob.name not in ['R152_CLASS2_TERRAIN','R152_FORECOURT_0']:
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

n=len(zs);vs=[(x,y,z+dz) for dz in [0,-.2] for (x,y),z in zip(domain['vertices'],zs)];faces=[tuple(f) for f in domain['faces']]+[tuple(i+n for i in reversed(f)) for f in domain['faces']];edges=Counter(tuple(sorted((a,b))) for f in domain['faces'] for a,b in zip(f,f[1:]+f[:1]))
for (a,b),count in edges.items():
 if count==1:faces.append((a,b,b+n,a+n))
me=bpy.data.meshes.new('R480_NW_GRADED_LAWN');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(check.values()),check
uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=np.array([v.x,v.y,1])@uvcoef
ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0]);ob['level_id']='SITE';ob['source']='Four independent grade planes across full source-traced lawn. Bank fit requires further validation; no arbitrary core blend.'
out=R/'scenes/MUDAM_R480_TAM_AVLU_SEVLERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R480_GROUND_CONTACT.json').write_text(json.dumps(dict(scene=out.name,topology=check,boundaryContacts=len(contacts),maxBoundaryGap=None,uvFitRms=uvrms,cuts=records,source=d['check'],accepted=False,published=False,limits=['Full traced lawn replaces interior patch; grade model diagnostic RMS .086m, max .307m; west crest cap separately fitted, not accepted.','Adjacent narrow glazing and retaining faces still pending.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-48,37,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R480_ground_contacts.png');bpy.ops.render.render(write_still=True)
