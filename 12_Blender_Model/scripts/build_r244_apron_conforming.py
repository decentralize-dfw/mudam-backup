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
apronVerts=[];apronFaces=[]
outline=list(poly)
def split(poly,a,b):
 ins=[];out=[]
 def dt(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dt(p),dt(q)
  if dp>=-1e-8:ins.append(p)
  if dp<=1e-8:out.append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out

changes=[]
for name in names:
 o=bpy.data.objects[name];old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;polys=[];insidePolys=[]
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
   if len(remain)>=3:insidePolys.append(remain)
  polys=nextpolys
 for ring in insidePolys:
  for j in range(1,len(ring)-1):
   a,b,c=[Vector(q[:3]) for q in (ring[0],ring[j],ring[j+1])];ix={};N=max(1,min(12,math.ceil(max((a-b).length,(b-c).length,(c-a).length)/.75)))
   for ii in range(N+1):
    for jj in range(N+1-ii):
     q=a+(b-a)*ii/N+(c-a)*jj/N;flat=Vector((q.x,q.y,0));edge=min(dist(flat,u,v) for u,v in zip(outline,outline[1:]+outline[:1]));x=(q.x-d['gradeOrigin'][0])/20;y=(q.y-d['gradeOrigin'][1])/20;z=sum(u*v for u,v in zip(d['gradeCoefficients'],[1,x,y,x*x,x*y,y*y]));w=min(1,edge/1.5);w=w*w*(3-2*w);z=q.z*(1-w)+z*w;ix[ii,jj]=len(apronVerts);apronVerts.append((q.x,q.y,z))
   for ii in range(N):
    for jj in range(N-ii):
     apronFaces.append((ix[ii,jj],ix[ii+1,jj],ix[ii,jj+1]))
     if ii+jj<N-1:apronFaces.append((ix[ii+1,jj],ix[ii+1,jj+1],ix[ii,jj+1]))
 vs=[];fs=[];tex=[];mats=[]
 for p,mat in polys:
  k=len(vs);vs.extend(o.matrix_world.inverted()@Vector(v[:3]) for v in p);tex.extend(v[3:] for v in p)
  for j in range(1,len(p)-1):fs.append((k,k+j,k+j+1));mats.append(mat)
 me=bpy.data.meshes.new(name+'_R244');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 for f,m in zip(me.polygons,mats):f.material_index=m
 o.data=me;changes.append(name)
me=bpy.data.meshes.new('R244_UPHILL_APRON');me.from_pydata(apronVerts,[],apronFaces);me.update();me.materials.append(bpy.data.materials['R234_DRY_FORT_EARTH']);obj=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(obj)
for name in names+['R244_UPHILL_APRON']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-8],context='FACES');bm.to_mesh(o.data);bm.free()
p=R/'scenes/MUDAM_R244_KALE_UST_AVLU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R244_apron_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in names+['R244_UPHILL_APRON'])
glb=R/'exports/r152_clean/r244_apron_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[dict(name=o.name,finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'];print('CHECKS',checks);assert all(c['finite'] and not c['zero'] for c in checks)
(R/'reports/R244_UPHILL_APRON.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,changed=changes,reopen=checks,limits=['Boundary1.5m transition uses existing authored terrain','Final blended surface fidelity not yet measured','Whole fort remains incomplete']),indent=2));print('R244_READY')
