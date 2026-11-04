import bpy,bmesh,json,hashlib,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
CACHE=R/'.local_source_cache/r588_ground'
CACHE.mkdir(parents=True,exist_ok=True)
D=json.loads((CACHE/'R588_GROUND_TRANSITION_DATA.json').read_text());INPUT=json.loads((CACHE/'R588_GROUND_FULL_INPUT.json').read_text())
base=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v009.blend'
out=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v010.blend'
bpy.ops.wm.open_mainfile(filepath=str(base))
def sig(o):
 m=o.data;a=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',a);b=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',b)
 return hashlib.sha256(a.tobytes()+b.tobytes()+str((o.matrix_world,o.hide_render)).encode()).hexdigest()
before={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'}
old=INPUT['R152_CLASS2_TERRAIN'];ov=[Vector(v)for v in old['vertices']];ot=[t['vertices']for t in old['triangles']]
bv=BVHTree.FromPolygons(ov,ot,all_triangles=True)
def inherited_normal(p):
 loc,n,i,dist=bv.find_nearest(Vector(p))
 if loc is None:return Vector((0,0,1))
 t=old['triangles'][i];a=np.array([old['vertices'][k]for k in t['vertices']]);M=np.c_[a[:,:2],np.ones(3)].T
 try:w=np.linalg.solve(M,np.array([loc.x,loc.y,1]))
 except np.linalg.LinAlgError:return n
 q=w@np.array([old['normals'][k]for k in t['loops']]);return Vector(q).normalized()
def planar_uv(o):
 o.data.calc_loop_triangles();ls=list(o.data.loops);xyz=np.array([list(o.matrix_world@o.data.vertices[l.vertex_index].co)for l in ls]);A=np.c_[xyz[:,:2],np.ones(len(xyz))]
 result={}
 for l in o.data.uv_layers:
  uv=np.array([list(q.uv)for q in l.data]);co=np.linalg.lstsq(A,uv,rcond=None)[0];err=float(np.max(abs(A@co-uv)));assert err<2e-4,(o.name,l.name,err);result[l.name]=co
 return result
def inside(p):return -33.00001<=p.x<=-23.99999 and -9.55001<=p.y<=3.80001
reports={}
for name,rows in D['objects'].items():
 removed_slivers=[];valid_rows=[]
 for row in rows:
  q=np.array(row['v'],dtype=np.float32);area=float(np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))*.5)
  if area<1e-10:removed_slivers.append(area)
  else:valid_rows.append(row)
 rows=valid_rows
 o=bpy.data.objects[name];oldmesh=o.data;materials=list(oldmesh.materials);solid=name!='R152_CLASS2_TERRAIN';uvcoef=planar_uv(o)
 verts=[v for t in rows for v in t['v']];faces=[(3*i,3*i+1,3*i+2)for i in range(len(rows))]
 m=bpy.data.meshes.new(name+'_v010');m.from_pydata(verts,[],faces);m.update()
 if not solid:
  test=bmesh.new();test.from_mesh(m);test.faces.ensure_lookup_table();bad={f.index for f in test.faces if f.calc_area()<1e-10};test.free()
  if bad:
   removed_slivers.extend([0]*len(bad));rows=[r for i,r in enumerate(rows)if i not in bad];verts=[v for t in rows for v in t['v']];faces=[(3*i,3*i+1,3*i+2)for i in range(len(rows))];m.clear_geometry();m.from_pydata(verts,[],faces);m.update()
 if solid:
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
  # Polygon differences create T junctions where clipped and unchanged source
  # triangles meet. Node every existing collinear vertex before extrusion.
  candidates=[v.co.copy()for v in bm.verts]
  for iteration in range(64):
   splits=0
   for e in list(bm.edges):
    a=e.verts[0].co.copy();ab=e.verts[1].co-a;ll=ab.length_squared
    if ll<1e-12:continue
    hits=[]
    for p in candidates:
     t=(p-a).dot(ab)/ll
     if 1e-5<t<1-1e-5 and (a+t*ab-p).length<1e-5:hits.append((t,p))
    if hits:
     t,p=min(hits,key=lambda q:q[0]);ne,nv=bmesh.utils.edge_split(e,e.verts[0],t);nv.co=p;splits+=1
   if not splits:break
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
  bmesh.ops.triangulate(bm,faces=list(bm.faces))
  tiny=[f for f in bm.faces if f.calc_area()<1e-11]
  if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  for f in bm.faces:
   if f.normal.z<0:f.normal_flip()
  bm.to_mesh(m);bm.free();m.update()
  tv=[tuple(v.co)for v in m.vertices];tf=[list(f.vertices)for f in m.polygons];n=len(tv);edges=defaultdict(list)
  for f in tf:
   for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))].append((a,b))
  assert all(len(x)<=2 for x in edges.values()),name
  boundary=[e[0]for e in edges.values()if len(e)==1]
  allv=tv+[(x,y,z-.2)for x,y,z in tv];allf=tf+[[q+n for q in reversed(f)]for f in tf]+[[a+n,b+n,b,a]for a,b in boundary]
  m.clear_geometry();m.from_pydata(allv,[],allf);m.update();topcount=len(tf)
 else:topcount=len(rows)
 for mat in materials:m.materials.append(mat)
 for lname,coef in uvcoef.items():
  l=m.uv_layers.new(name=lname)
  for i,loop in enumerate(m.loops):p=m.vertices[loop.vertex_index].co;l.data[i].uv=np.array([p.x,p.y,1])@coef
 # Physical normals share only similar-facing surfaces. Connector/bottom edges
 # retain their actual crease; inherited terrain normals remain outside edits.
 incident=defaultdict(list)
 for f in m.polygons[:topcount]:
  if f.area<1e-10:continue
  for vi in f.vertices:incident[tuple(round(q,5)for q in m.vertices[vi].co)].append((f.normal.copy(),f.area))
 norms=[]
 for fi,f in enumerate(m.polygons):
  f.use_smooth=fi<topcount
  for li in f.loop_indices:
   p=m.vertices[m.loops[li].vertex_index].co
   if fi>=topcount:norm=f.normal
   elif name=='R588_WEST_CLASS2_GROUND_RESTORATION' and not inside(p):norm=inherited_normal(p)
   elif name=='R152_CLASS2_TERRAIN' and not rows[fi]['inside']:norm=Vector(rows[fi]['normals'][li-f.loop_start])
   else:
    candidates=incident[tuple(round(q,5)for q in p)];norm=sum((nn*aa for nn,aa in candidates if nn.dot(f.normal)>.55),Vector((0,0,0))).normalized()
   norms.append(tuple(norm))
 m.normals_split_custom_set(norms);o.data=m
 o['R588_ground_method']=D['method'];o['R588_source_audit']=D['source'];o['R588_source_limit']='Diagonal break candidate +/- source resolution, not measured survey; class2 grade controls with heldout checks. Southern building footprint protected.'
 bm=bmesh.new();bm.from_mesh(m);report=dict(vertices=len(m.vertices),faces=len(m.polygons),nonManifold=sum(not e.is_manifold for e in bm.edges),badEdges=[dict(v=[list(v.co)for v in e.verts],faces=len(e.link_faces))for e in bm.edges if not e.is_manifold][:12],zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),customNormals=m.has_custom_normals,uvLayers=list(uvcoef),volume=bm.calc_volume(signed=False)if solid else None);bm.free()
 if solid:assert report['nonManifold']==report['zeroArea']==0,(name,report)
 report['removedFloat32DegenerateSlivers']=len(removed_slivers);reports[name]=report
changed=[n for n,h in before.items()if h!=sig(bpy.data.objects[n])];assert set(changed)==set(D['objects']),(changed,list(D['objects']))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
afterchanged=[n for n,h in before.items()if h!=sig(bpy.data.objects[n])];assert set(afterchanged)==set(changed)
report=dict(scene=str(out),base=str(base),reopened=True,changed=changed,unchangedOtherMeshes=len(before)-len(changed),objects=reports,gradeChanges=D['reports'],source=D['source'],limitations=D['limits'],sourceSurfaceCopied=False,accepted=False,published=False)
(W/'R588_GROUND_V010_BUILD.json').write_text(json.dumps(report,indent=2));print('R588_GROUND_V010_READY',report,flush=True)
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R588_west_v010.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-40,8,65);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=38;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R588_west_top_v010.png');bpy.ops.render.render(write_still=True)
