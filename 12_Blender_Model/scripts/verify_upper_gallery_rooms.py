from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R23_build_report.json').read_text());P=json.loads((B/'config/upper_gallery_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];
output_name='R23_verification.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];assert len(args)==2;r['file']=args[0];output_name=args[1]
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(p,q):
 d=(q-p).normalized();hits=[]
 for ob in visible:
  iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@d,distance=(q-p).length)
  if ok:hits.append(ob.name)
 return hits
UP=r['upper_z'];passages=[];support=[]
for door in r['portals']:
 a=Vector(door['start']);b=Vector(door['end']);n=Vector(door['outward'])
 for f in [.2,.5,.8]:
  p=a+(b-a)*f
  for h in [.2,1.5,2.2]:
   hits=ray(p-n*.5+Vector((0,0,UP+h)),p+n*.9+Vector((0,0,UP+h)));row=dict(portal=door['id'],fraction=f,h=h,hits=hits);passages.append(row)
   if hits:fail.append(row)
  for d in [-.2,.4,.75,1.1]:
   q=p+n*d+Vector((0,0,UP+.04));hits=ray(q,q-Vector((0,0,.08)));head=ray(q,q+Vector((0,0,2.05)));row=dict(portal=door['id'],fraction=f,offset=d,support=hits,head=head);support.append(row)
   if not hits or head:fail.append(row)
def uv(u,v,z):return point((u+v)/2,(u-v)/2,z)
route=[(1263,470),(1263,440),(1235,440),(1210,440),(1188,440),(1188,418)]
for i,(u,v) in enumerate(route):
 p=uv(u,v,UP+.04);hits=ray(p,p-Vector((0,0,.08)));head=ray(p,p+Vector((0,0,2.05)));row=dict(route_index=i,uv=[u,v],support=hits,head=head);support.append(row)
 if not hits or head:fail.append(row)
for a,b in zip(route,route[1:]):
 hits=ray(uv(*a,UP+1.4),uv(*b,UP+1.4));row=dict(route_segment=[a,b],hits=hits);passages.append(row)
 if hits:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,portal_and_route_rays=passages,support_head_samples=support,old_west_straight_route_superseded=True,roof_study_unresolved=True,construction_acceptance=False);(B/'reports'/output_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
