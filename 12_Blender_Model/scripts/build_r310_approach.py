from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R309_ECCL_UC_CEPHE_BIRLESIM_ADAY_v001.blend'));d=json.loads((R/'config/r310_north_approach.json').read_text());path=np.array(d['path']);stations=np.array(d['stations']);grade=d['grade'];changes=[]
for ob in list(bpy.context.scene.objects):
 if ob.name.startswith("R305_NORTH_"):bpy.data.objects.remove(ob,do_unlink=True)
def deck(s):return grade[0]*s+grade[1]
def point(s,off,z):
 i=min(len(path)-2,max(0,int(np.searchsorted(stations,s,side="right")-1)));t=(s-stations[i])/(stations[i+1]-stations[i]);p=path[i]*(1-t)+path[i+1]*t;u=path[i+1]-path[i];u/=np.linalg.norm(u);p+=np.array([u[1],-u[0]])*off;return (float(p[0]),float(p[1]),float(z))
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/4,v.z/4)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o

def ribbon(name,ds,hs,mat):
 vs=[];fs=[]
 for s in stations:vs.extend(point(s,dd,deck(s)+zz) for dd,zz in [(ds[0],hs[0]),(ds[1],hs[0]),(ds[1],hs[1]),(ds[0],hs[1])])
 for i in range(len(stations)-1):
  k=i*4
  for j in range(4):fs.append((k+j,k+(j+1)%4,k+(j+1)%4+4,k+j+4))
 fs.extend([(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]);return mesh(name,vs,fs,mat)
ribbon('R310_NORTH_BALLAST',[-5,5],[-.3,.02],bpy.data.materials['R175_BALLAST'])
for ti,track in enumerate([-1.82,1.82]):
 for ri,delta in enumerate([-.7175,.7175]):ribbon(f'R310_NORTH_RAIL_{ti}_{ri}',[track+delta-.035,track+delta+.035],[.15,.28],bpy.data.materials['R175_RAIL_STEEL'])
 vs=[];fs=[]
 for s in np.arange(stations[0]+.3,-.3,.75):
  k=len(vs);vs.extend(point(st,dd,deck(st)+zz) for zz in [.02,.14] for st,dd in [(s-.11,track-1.2),(s+.11,track-1.2),(s+.11,track+1.2),(s-.11,track+1.2)])
  fs.extend(tuple(k+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 mesh('R310_NORTH_SLEEPERS_'+str(ti),vs,fs,bpy.data.materials['R175_SLEEPERS'])
a=path[:-1];ab=path[1:]-a;den=np.sum(ab*ab,axis=1)
def project(p):
 t=np.clip(np.sum((p-a)*ab,axis=1)/den,0,1);q=a+ab*t[:,None];dist=np.linalg.norm(q-p,axis=1);i=np.argmin(dist);return float(dist[i]),float(stations[i]+t[i]*(stations[i+1]-stations[i]))
lo=path.min(0)-7;hi=path.max(0)+7
for name in ['R154_FAR_GROUND','R182_EXTENSION_GROUND']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);M=o.matrix_world;inv=M.inverted()
 for _ in range(2):
  edges=set()
  for f in bm.faces:
   ps=[M@v.co for v in f.verts]
   if max(p.x for p in ps)<lo[0] or min(p.x for p in ps)>hi[0] or max(p.y for p in ps)<lo[1] or min(p.y for p in ps)>hi[1]:continue
   edges.update(e for e in f.edges if (M@e.verts[0].co-M@e.verts[1].co).length>1.5)
  if edges:bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=2,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 count=0;maxshift=0
 for v in bm.verts:
  p=M@v.co
  if not(lo[0]<=p.x<=hi[0] and lo[1]<=p.y<=hi[1]):continue
  dist,s=project(np.array(p[:2]))
  if dist>=7:continue
  # Reject points beyond either endpoint, so the existing bridge is untouched.
  if s<=stations[0]+.001 and np.dot(np.array(p[:2])-path[0],ab[0])<0:continue
  if s>=-.001 and np.dot(np.array(p[:2])-path[-1],ab[-1])>0:continue
  w=max(0,min(1,(7-dist)/2));z=p.z*(1-w)+(deck(s)-.12)*w;maxshift=max(maxshift,abs(z-p.z));p.z=z;v.co=inv@p;count+=1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES');bm.to_mesh(o.data);bm.free();changes.append(dict(name=name,vertices=count,maxShift=maxshift))
removed=[]
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('R158_TREE_'):continue
 corners=[o.matrix_world@Vector(v) for v in o.bound_box];p=sum(corners,Vector())/8;dist,s=project(np.array(p[:2]))
 if dist<6.2 and stations[0]+.1<s<-.1:removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
pathout=R/'scenes/MUDAM_R310_KUZEY_RAY_TAM_HARITA_HATTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(pathout),compress=True);bpy.ops.wm.open_mainfile(filepath=str(pathout));s=bpy.context.scene;t=Vector((-290,-265,-48));s.camera.location=t+Vector((-100,-140,120));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=190;s.render.resolution_x=1300;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R310_north_approach.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R310_'))
glb=R/'exports/r152_clean/r310_north_rail_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R310_NORTH_APPROACH.json').write_text(json.dumps(dict(accepted=False,published=False,changes=changes,removedTrees=removed,checks=checks,reference=d,scope='Full166m mapped north approach; north adjacent viaduct and south continuation not yet complete'),indent=2));print('R310_READY')

