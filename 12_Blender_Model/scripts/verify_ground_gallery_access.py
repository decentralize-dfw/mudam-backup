from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R28_build_report.json').read_text());P=json.loads((B/'config/ground_gallery_access.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
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
for name,ends in P['routes'].items():
 a,b=[point(*p) for p in ends];normal=(b-a).normalized().cross(Vector((0,0,1)))
 for offset in [-.35,0,.35]:
  for h in [.3,1.5,2.1]:
   hits=ray(a+normal*offset+Vector((0,0,h)),b+normal*offset+Vector((0,0,h)));row=dict(route=name,offset=offset,height=h,hits=hits);passages.append(row)
   if hits:fail.append(row)
  for f in [0,.2,.4,.6,.8,1]:
   p=a+(b-a)*f+normal*offset+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(route=name,offset=offset,fraction=f,support=hits,head=head);support.append(row)
   if not hits or head:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,passage_rays=passages,support_head_samples=support,construction_acceptance=False);(B/'reports/R28_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
