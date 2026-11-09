from pathlib import Path
import bpy,bmesh,json,numpy as np
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));sv=[];sf=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(sv);sv.extend(o.matrix_world@v.co for v in o.data.vertices);sf.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
source=BVHTree.FromPolygons(sv,sf,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v073.blend'));body=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];me=body.data;verts=[];faces=[];uvs=[];ids={};mat=me.materials[me.polygons[0].material_index]
for face in me.polygons[:35200]:
 f=[];uv=[]
 for li in face.loop_indices:
  p=me.vertices[me.loops[li].vertex_index].co;key=tuple(round(x,7) for x in p)
  if key not in ids:ids[key]=len(verts);verts.append(np.array(p))
  f.append(ids[key]);uv.append(np.array(me.uv_layers.active.data[li].uv))
 faces.append(f);uvs.append(uv)
rejected=[];history=[]
def sample(p):
 h,*_=source.ray_cast(Vector((float(p[0]),float(p[1]),50)),Vector((0,0,-1)),200)
 if not h:return p.copy(),False
 # A multi-metre downward jump into source layers is not proof of a real roof opening.
 if h.z<p[2]-3:rejected.append([*map(float,p),float(h.z)]);return p.copy(),False
 return np.array(h),True
for iteration in range(3):
 counts=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]));split={};centres={};flagged=0
 for fi,f in enumerate(faces):
  p=sum((verts[i] for i in f))/3;c,ok=sample(p);bad=ok and abs(c[2]-p[2])>.08
  for a,b in zip(f,f[1:]+f[:1]):
   key=tuple(sorted((a,b)))
   if counts[key]!=2:continue
   mid=(verts[a]+verts[b])/2;h,valid=sample(mid)
   if valid and abs(h[2]-mid[2])>.08:split[key]=h;bad=True
  if bad:centres[fi]=c;flagged+=1
 if not flagged:break
 edgeids={}
 for key,p in split.items():edgeids[key]=len(verts);verts.append(p)
 nf=[];nu=[]
 for fi,(f,uv) in enumerate(zip(faces,uvs)):
  poly=[];pu=[]
  for j,(a,b) in enumerate(zip(f,f[1:]+f[:1])):
   poly.append(a);pu.append(uv[j]);key=tuple(sorted((a,b)))
   if key in edgeids:poly.append(edgeids[key]);pu.append((uv[j]+uv[(j+1)%3])/2)
  if fi not in centres and len(poly)==3:nf.append(f);nu.append(uv);continue
  c=centres.get(fi)
  if c is None:c,_=sample(sum((verts[i] for i in f))/3)
  ci=len(verts);verts.append(c);cu=sum(uv)/3
  for j,a in enumerate(poly):nf.append([a,poly[(j+1)%len(poly)],ci]);nu.append([pu[j],pu[(j+1)%len(poly)],cu])
 history.append(dict(iteration=iteration,flagged=flagged,split_edges=len(split),triangles=len(nf)));faces,uvs=nf,nu;print(history[-1],flush=True)
# Remove only the previous main-roof faces; all exterior facade geometry stays unchanged.
bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=list(bm.faces)[:35200],context='FACES');loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(me);bm.free();body.name='R169_FACADES'
mesh=bpy.data.meshes.new('R169_ADAPTIVE_MAIN_ROOF');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat);layer=mesh.uv_layers.new(name='UVMap')
for face,uv in zip(mesh.polygons,uvs):
 for li,p in zip(face.loop_indices,uv):layer.data[li].uv=p
 face.use_smooth=True
roof=bpy.data.objects.new('R169_WHOLE_SOURCE_ROOF',mesh);bpy.context.collection.objects.link(roof);bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
path=R/'scenes/MUDAM_R169_ADAPTIF_BUTUN_CATI_ADAY_v074.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);(R/'reports/R169_ADAPTIVE_ROOF_v074.json').write_text(json.dumps(dict(history=history,rejected_large_source_drops=rejected[:30],rejected_count=len(rejected),accepted=False,published=False),indent=2));print('ADAPTIVE_COMPLETE',len(verts),len(faces))
