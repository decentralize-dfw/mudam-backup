from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R14_build_report.json').read_text());P=json.loads((B/'config/west_glazed_stair.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();up=Vector((0,0,1));fail=[];solids=[]
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(p,d,length):
 hits=[]
 for ob in visible:
  iv=ob.matrix_world.inverted();ok,loc,_,_=ob.ray_cast(iv@p,iv.to_3x3()@d,distance=length)
  if ok:hits.append(dict(name=ob.name,distance=(ob.matrix_world@loc-p).length))
 return sorted(hits,key=lambda h:h['distance'])
walk=[];eyes=[]
for t in r['steps']:
 for f in [-.3,0,.3]:
  p=Vector(t['center'])+Vector(t['side'])*t['width']*f+up*.025;support=ray(p,-up,.06);head=ray(p,up,2.1);row=dict(tread=t['name'],fraction=f,support=support[:2],head=head);walk.append(row)
  if not support or support[0]['name']!=t['name'] or head:fail.append(row)
  if f==0:eyes.append(p+up*1.4)
landings=[]
for label,uv,z in [('entry_inside',(1170,590),0),('entry_seam',(1115,590),0),('entry_previous',(1110,590),0),('corner',(1263.5,591),r['mid_z'])]+[(f'upper_{v}',(1263,v),r['upper_z']) for v in [495,470,460,450,430,410,400]]:
 p=point(*uv,z)+up*.025;support=ray(p,-up,.08);head=ray(p,up,2.1);row=dict(label=label,support=support[:2],head=head);landings.append(row)
 if not support or head:fail.append(row)
paths=[]
for a,b in zip(eyes,eyes[1:]):
 hits=ray(a,(b-a).normalized(),(b-a).length);paths.append(hits)
 if hits:fail.append(dict(test='eye_path',hits=hits))
for u in [1257,1263,1270]:
 a=point(u,495,r['upper_z']+1.4);b=point(u,400,r['upper_z']+1.4);hits=ray(a,(b-a).normalized(),(b-a).length);paths.append(hits)
 if hits:fail.append(dict(test='upper_gallery_entry_path',u=u,hits=hits))
glass=[]
for name in r['panels']:
 ob=bpy.data.objects[name];vs=np.array([list(v.co) for v in ob.data.vertices]);ps=vs[:4];n=np.cross(ps[1]-ps[0],ps[2]-ps[0]);n/=np.linalg.norm(n);err=float(max(abs((ps-ps[0])@n)));glass.append(dict(name=name,plane_error=err))
 if err>2e-5:fail.append(glass[-1])
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,tread_support_headroom=walk,landings=landings,eye_paths=paths,glass_planes=glass,construction_acceptance=False);(B/'reports/R14_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
