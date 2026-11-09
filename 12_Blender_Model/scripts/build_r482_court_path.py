import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
from collections import Counter
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend'))
D=json.loads((R/'reports/R482_COURT_PATH_DOMAINS.json').read_text());P=json.loads((R/'reports/R481_WEST_PATH_GRADE.json').read_text());G=json.loads((R/'reports/R479_NW_FOUR_GRADE_PLANES.json').read_text());assert P['valid']
vs=[];fs=[]
for name in ['R457_NORTH_LOADING_COURT','R458_WEST_SERVICE_PLAZA']:
 o=bpy.data.objects[name];o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[i+k for i in t.vertices] for t in o.data.loop_triangles])
B=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def edgey(x):
 return 44.557142857+(x+59.971428571)*(.314285714/13.042857143) if x<=-46.928571429 else 44.871428571-(x+46.928571429)*(.314285714/13.828571429)
def court(x):
 h,*_=B.ray_cast(Vector((x,edgey(x)+.002,20)),Vector((0,0,-1)),50)
 assert h is not None,x
 return h.z
pc=P['coefficients']
def rawpath(x,y):return sum(a*b for a,b in zip(pc,[1,x,y,x*x,x*y,y*y]))
def pathgrade(x,y):
 w=max(0,min(1,(y-43.2)/1.01));return rawpath(x,y)*(1-w)+court(max(-58.22,min(-44.43,x)))*w
# Actual traced west verge, and north lawn boundary; bank widths are explicit model parameters.
west=np.array(sorted([(44.21,-58.22),(37,-57.31),(27.9,-56.855),(20.165,-57.415)]))
north=np.array(sorted([(-58.22,44.21),(-44.78,44.0),(-44.43,43.16)]))
def lawn(x,y):
 xe=float(np.interp(y,west[:,0],west[:,1]));yn=float(np.interp(x,north[:,0],north[:,1]));base=G['planes'][0];floor=base[0]+base[1]*(x+51)+base[2]*(y-35)
 w=max(0,1-max(0,x-xe)/3.5);n=max(0,1-max(0,yn-y)/2.5)
 westz=floor+(pathgrade(xe,y)-floor)*w;northz=floor+(court(max(-58.22,min(-44.43,x)))-floor)*n
 e=G['planes'][3];east=e[0]+e[1]*(x+51)+e[2]*(y-35)
 return max(floor,westz,northz,east)
poly=D['cutout'];tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tri];records=[]
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

checks=[];newnames=[]
for key,fn in [('lawn',lawn),('path',pathgrade),('connector',lambda x,y:court(x))]:
 dm=D[key];N=len(dm['vertices']);vs=[(x,y,fn(x,y)+dz) for dz in [0,-.2] for x,y in dm['vertices']];faces=[tuple(f) for f in dm['faces']]+[tuple(i+N for i in reversed(f)) for f in dm['faces']];edges=Counter(tuple(sorted((a,b))) for f in dm['faces'] for a,b in zip(f,f[1:]+f[:1]))
 for (a,b),cnt in edges.items():
  if cnt==1:faces.append((a,b,b+N,a+N))
 name='R482_NW_'+key.upper();me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));checks.append(check);bm.to_mesh(me);bm.free();assert check['nonManifold']==check['zeroArea']==0,check
 ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);newnames.append(name);ob['level_id']='SITE';ob['source']='Independent source-traced lawn, measured path and court connection. No source mesh transferred. Bank width diagnostic.'
 mat=bpy.data.objects['R152_CLASS2_TERRAIN' if key=='lawn' else 'R457_NORTH_LOADING_COURT'].data.materials[0];me.materials.append(mat)
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x*.05,v.y*.05)
out=R/'scenes/MUDAM_R482_AVLU_YOL_SEV_BIRLESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
reopen=[]
for name in newnames:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);reopen.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R482_COURT_PATH_BUILD.json').write_text(json.dumps(dict(scene=out.name,checks=checks,reopened=reopen,cuts=records,pathControls=P['check'],accepted=False,published=False,limits=['Bank widths3.5m/2.5m require visual source reconciliation.','Historic retaining edge and adjacent dark strip still incomplete.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-48,37,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R482_court_path.png');bpy.ops.render.render(write_still=True)
