from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R30_build_report.json').read_text());P=json.loads((B/'config/upper_lift_landing.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];
output_name='R30_verification.json'
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
passages=[];support=[];UP=r['upper_z']
for x in [650,665,680]:
 for y in [537,544,552,559]:
  p=point(x,y,UP+.04);hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(x=x,y=y,support=hits,head=head);support.append(row)
  if not hits or head:fail.append(row)
for x in [650,665,680]:
 for h in [.3,1.5,2.1]:
  hits=ray(point(x,579,UP+h),point(x,536,UP+h));row=dict(x=x,h=h,hits=hits);passages.append(row)
  if hits:fail.append(row)
leaf_checks=[]
x0,x1=P['door_span_canonical']
for i in range(4):
 x=x0+(x1-x0)*(i+.5)/4;hits=ray(point(x,538,UP+1.2),point(x,531,UP+1.2));expected='R30_DOOR_LEAF_'+str(i+1);row=dict(leaf=expected,hits=hits);leaf_checks.append(row)
 if expected not in hits or any(n not in [expected,'R30_DOOR_BACKING'] for n in hits):fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,passage_rays=passages,support_head_samples=support,closed_leaf_checks=leaf_checks,full_shaft_continuity_verified=False,construction_acceptance=False);(B/'reports'/output_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
