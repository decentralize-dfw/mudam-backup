from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R234_KALE_TOPRAK_YUZEY_ADAY_v001.blend'));rows=json.loads((R/'config/r193_fort_sw_planes.json').read_text());d=json.loads((R/'config/r235_court_grade.json').read_text());edgeCounts={}
for r in rows:
 for p,q in zip(r['xy'],r['xy'][1:]+r['xy'][:1]):
  e=tuple(sorted((tuple(p),tuple(q))));edgeCounts[e]=edgeCounts.get(e,0)+1
edges=[(Vector(p),Vector(q))for (p,q),n in edgeCounts.items()if n==1]
def h(x,y):
 X=(x-d['origin'][0])/25;Y=(y-d['origin'][1])/25;c=d['fit'];return c[0]+c[1]*X+c[2]*Y+c[3]*X*X+c[4]*X*Y+c[5]*Y*Y
def dist(p,a,b):
 v=b-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
changes=[]
for r in rows:
 o=bpy.data.objects['R193_'+r['name']];p=[Vector(v)for v in r['xy']];vs=[];fs=[];ids={};shifts=[];N=24
 for i in range(N+1):
  for j in range(N+1-i):
   q=p[0]+(p[1]-p[0])*(i/N)+(p[2]-p[0])*(j/N);old=r['plane'][0]*(q.x-r['origin'][0])+r['plane'][1]*(q.y-r['origin'][1])+r['plane'][2];w=min(1,min(dist(q,a,b)for a,b in edges)/4);w=w*w*(3-2*w);z=old+w*(h(q.x,q.y)-old);ids[i,j]=len(vs);vs.append((q.x,q.y,z));shifts.append(abs(z-old))
 for i in range(N):
  for j in range(N-i):
   fs.append((ids[i,j],ids[i+1,j],ids[i,j+1]))
   if i+j<N-1:fs.append((ids[i+1,j],ids[i+1,j+1],ids[i,j+1]))
 me=bpy.data.meshes.new(o.name+'_R235');me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R234_DRY_FORT_EARTH']);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o.data=me
 for face in me.polygons:face.use_smooth=True
 changes.append(dict(name=o.name,maxShift=max(shifts),vertices=len(vs)))
path=R/'scenes/MUDAM_R235_KALE_AVLU_KOT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.name.startswith('R193_SOUTHWEST_COURT'))
glb=R/'exports/r152_clean/r235_court_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 checks.append(dict(name=o.name,finite=all(math.isfinite(x)for v in o.data.vertices for x in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)))
assert all(c['finite'] and not c['zero']for c in checks)
(R/'reports/R235_COURT_GRADE.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,changes=changes,reopen=checks,limits=['Whole-fit held-out p90 .724m; not final accuracy acceptance','Outer boundary fixed with4m transition; actual blended surface error not measured','Existing walls/paths/ruin ground contact must be reconciled before production']),indent=2))
