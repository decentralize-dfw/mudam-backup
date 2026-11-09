from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R242_KALE_ISTINAT_ZEMIN_BAGLANTI_ADAY_v001.blend'))
d=json.loads((R/'config/r243_uphill_apron.json').read_text());assert d['gradeHeldoutP90']<.35
names=[o.name for o in bpy.context.scene.objects if o.type=='MESH' and (o.name in ('R154_FAR_GROUND','R241_RUIN_SURROUND') or o.name.startswith('R193_SOUTHWEST_COURT'))]
vs=[];fs=[]
for name in names:
 o=bpy.data.objects[name];o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);poly=[Vector((p[0],p[1],0)) for p in d['points']]
def dist(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
vs=[];fs=[]
for ids3 in d['triangles']:
 a,b,c=[poly[k] for k in ids3];ix={};N=20
 for i in range(N+1):
  for j in range(N+1-i):
   p=a+(b-a)*i/N+(c-a)*j/N;x=(p.x-d['gradeOrigin'][0])/20;y=(p.y-d['gradeOrigin'][1])/20;coef=d['gradeCoefficients'];z=sum(q*r for q,r in zip(coef,[1,x,y,x*x,x*y,y*y]));edge=min(dist(p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]));h=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)[0]
   if h is not None:
    w=min(1,edge/1.5);w=w*w*(3-2*w);z=h.z*(1-w)+z*w
   ix[i,j]=len(vs);vs.append((p.x,p.y,z))
 for i in range(N):
  for j in range(N-i):
   fs.append((ix[i,j],ix[i+1,j],ix[i,j+1]))
   if i+j<N-1:fs.append((ix[i+1,j],ix[i+1,j+1],ix[i,j+1]))
me=bpy.data.meshes.new('R243_UPHILL_APRON');me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R234_DRY_FORT_EARTH']);obj=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(obj)
def split(poly,a,b):
 ins=[];out=[]
 def dt(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dt(p),dt(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out

changes=[]
for name in names:
 o=bpy.data.objects[name];old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;polys=[]
 for t in old.loop_triangles:
  polys.append(([[*(o.matrix_world@old.vertices[vi].co),*(uv.data[li].uv if uv else (0,0))] for vi,li in zip(t.vertices,t.loops)],t.material_index))
 for ids3 in d['triangles']:
  xy=[d['points'][k][:2] for k in ids3]
  if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
  nextpolys=[]
  for poly,mat in polys:
   remain=poly
   for a,b in zip(xy,xy[1:]+xy[:1]):
    if len(remain)<3:break
    remain,out=split(remain,a,b)
    if len(out)>=3:nextpolys.append((out,mat))
  polys=nextpolys
 vs=[];fs=[];tex=[];mats=[]
 for p,mat in polys:
  k=len(vs);vs.extend(o.matrix_world.inverted()@Vector(v[:3]) for v in p);tex.extend(v[3:] for v in p)
  for j in range(1,len(p)-1):fs.append((k,k+j,k+j+1));mats.append(mat)
 me=bpy.data.meshes.new(name+'_R243');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 for f,m in zip(me.polygons,mats):f.material_index=m
 o.data=me;changes.append(name)
for name in names+['R243_UPHILL_APRON']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES');bm.to_mesh(o.data);bm.free()
p=R/'scenes/MUDAM_R243_KALE_UST_AVLU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R243_apron_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in names+['R243_UPHILL_APRON'])
glb=R/'exports/r152_clean/r243_apron_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[dict(name=o.name,finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'];assert all(c['finite'] and not c['zero'] for c in checks)
(R/'reports/R243_UPHILL_APRON.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,changed=changes,reopen=checks,limits=['Boundary1.5m transition uses existing authored terrain','Final blended surface fidelity not yet measured','Whole fort remains incomplete']),indent=2));print('R243_READY')
