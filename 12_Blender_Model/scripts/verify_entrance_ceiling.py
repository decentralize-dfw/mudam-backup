from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R39_build_report.json').read_text());P=json.loads((B/'config/ground_service_rooms.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];
output_name='R39_verification.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];assert len(args) in [2,3];r['file']=args[0];output_name=args[1]
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
passages=[];support=[]
for name,(start,end) in P['routes'].items():
 a,b=point(*start),point(*end)
 for h in [.3,1.5,2.05]:
  hits=ray(a+Vector((0,0,h)),b+Vector((0,0,h)));row=dict(route=name,h=h,hits=hits);passages.append(row)
  if hits:fail.append(row)
 for i in range(13):
  p=a.lerp(b,i/12)+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(route=name,t=i/12,support=hits,head=head);support.append(row)
  if not hits or head:fail.append(row)
import sys
sys.path.insert(0,str(Path(__file__).parent));from plan_union import inside
Q=json.loads((B/'config/entrance_ceiling.json').read_text());coverage=[];reserve=[]
if '--' in sys.argv and len(args)==3:
 contract=json.loads((B/'reports'/args[2]).read_text());assert contract['file']==r['file'];reserve=contract['stair_ceiling_reserve_canonical']
ceilings=[o for o in visible if o.name.startswith('R39_PUBLIC_CEILING_') or o.name.startswith('R33_CEILING_')]
for x in range(470,686,13):
 for y in range(558,708,11):
  if not inside((x,y),Q['public_outer']):continue
  p=point(x,y,Q['ceiling_z']-.04);hits=[]
  for ob in ceilings:
   iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@Vector((0,0,1)),distance=.08)
   if ok:hits.append(ob.name)
  stair_reserve=bool(reserve and inside((x,y),reserve));row=dict(canonical=[x,y],hits=hits,expected_stair_reserve=stair_reserve);coverage.append(row)
  if (not hits and not stair_reserve) or (hits and stair_reserve):fail.append(row)
result=dict(ceiling_coverage_samples=coverage,file=r['file'],failures=fail,evaluated_solids=solids,passage_rays=passages,support_head_samples=support,construction_acceptance=False);(B/'reports'/output_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
