from pathlib import Path
import bpy,json,math,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R239_KALE_IC_KALINTI_DUVARLARI_ADAY_v001.blend'))
d=json.loads((R/'config/r240_ruin_buffered_grade.json').read_text());assert d['p90']<.35 and d['support']>.85
poly=[Vector((*p,0)) for p in d['polygon']];tri=tessellate_polygon([poly]);vs=[];fs=[]
old=json.loads((R/'config/r193_fort_sw_planes.json').read_text())[0]
def distance(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
for ids in tri:
 t=[poly[k] for k in ids] if isinstance(ids[0],int) else ids;indices={};N=24
 for i in range(N+1):
  for j in range(N+1-i):
   q=t[0]+(t[1]-t[0])*i/N+(t[2]-t[0])*j/N;c=d['plane'];z=c[0]*(q.x-d['origin'][0])+c[1]*(q.y-d['origin'][1])+c[2]
   # Three inherited court edges have fixed old-plane elevations; the fourth borders the unmodelled uphill apron.
   edge=min(distance(q,poly[k],poly[k+1]) for k in range(3));w=min(1,edge/1.5);w=w*w*(3-2*w)
   prior=old['plane'][0]*(q.x-old['origin'][0])+old['plane'][1]*(q.y-old['origin'][1])+old['plane'][2];z=prior*(1-w)+z*w
   indices[i,j]=len(vs);vs.append((q.x,q.y,z))
 for i in range(N):
  for j in range(N-i):
   fs.append((indices[i,j],indices[i+1,j],indices[i,j+1]))
   if i+j<N-1:fs.append((indices[i+1,j],indices[i+1,j+1],indices[i,j+1]))
me=bpy.data.meshes.new('R240_RUIN_SURROUND');me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R234_DRY_FORT_EARTH']);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
xy=json.loads((R/'reports/R198_RUIN_MEASUREMENTS.json').read_text())['xy']
if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
records=[]
def split(poly,a,b):
 ins=[];out=[]
 def dt(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dt(p),dt(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not (o.name=='R240_RUIN_SURROUND' ):continue
 old=o.data;old.calc_loop_triangles();before=sum(p.area for p in old.polygons);uv=old.uv_layers.active;vs=[];fs=[];tex=[]
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):v=o.matrix_world@old.vertices[vi].co;poly.append([*v,*(uv.data[li].uv if uv else (0,0))])
  parts=[];remain=poly
  for a,b in zip(xy,xy[1:]+xy[:1]):
   if len(remain)<3:break
   remain,out=split(remain,a,b)
   if len(out)>=3:parts.append(out)
  for p in parts:
   k=len(vs);vs.extend(v[:3] for v in p);tex.extend(v[3:] for v in p);fs.extend((k,k+j,k+j+1) for j in range(1,len(p)-1))
 me=bpy.data.meshes.new(o.name+'_RUIN_CUT');me.from_pydata([o.matrix_world.inverted()@Vector(v) for v in vs],[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 o.data=me
 records.append(dict(name=o.name,beforeArea=before,afterArea=sum(p.area for p in me.polygons)))


xy=d['polygon']
if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not (o.name=='R154_FAR_GROUND' ):continue
 old=o.data;old.calc_loop_triangles();before=sum(p.area for p in old.polygons);uv=old.uv_layers.active;vs=[];fs=[];tex=[]
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):v=o.matrix_world@old.vertices[vi].co;poly.append([*v,*(uv.data[li].uv if uv else (0,0))])
  parts=[];remain=poly
  for a,b in zip(xy,xy[1:]+xy[:1]):
   if len(remain)<3:break
   remain,out=split(remain,a,b)
   if len(out)>=3:parts.append(out)
  for p in parts:
   k=len(vs);vs.extend(v[:3] for v in p);tex.extend(v[3:] for v in p);fs.extend((k,k+j,k+j+1) for j in range(1,len(p)-1))
 me=bpy.data.meshes.new(o.name+'_RUIN_CUT');me.from_pydata([o.matrix_world.inverted()@Vector(v) for v in vs],[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 o.data=me
 records.append(dict(name=o.name,beforeArea=before,afterArea=sum(p.area for p in me.polygons)))


o=bpy.data.objects['R240_RUIN_SURROUND'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-9],context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
path=R/'scenes/MUDAM_R240_KALE_KALINTI_CEVRE_ZEMIN_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R240_ruin_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name=='R240_RUIN_SURROUND')
g=R/'exports/r152_clean/r240_ruin_surround_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(g),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(g));checks=[dict(name=o.name,finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'];assert all(c['finite'] and not c['zero'] for c in checks)
(R/'reports/R240_RUIN_SURROUND.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,cut=records,reopen=checks,limits=['1.5m exclusion removes stone-wall contamination from measurements','Boundary blend and ruin contact require visual acceptance','Uphill apron and whole fort remain incomplete']),indent=2));print('R240_READY')


