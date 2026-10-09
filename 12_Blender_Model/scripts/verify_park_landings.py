from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R38_build_report.json').read_text());P=json.loads((B/'config/park_landings.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
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
bridge_samples=[];Q=json.loads((B/'reports/R34_build_report.json').read_text())
for route,(a,b) in Q['routes'].items():
 a,b=Vector((*a,0)),Vector((*b,0))
 for i in range(61):
  p=a.lerp(b,i/60)+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(route=route,t=i/60,support=hits,head=head);bridge_samples.append(row)
  if Q['deck'] not in hits or head:fail.append(row)
tree_checks=[]
for t in r['trees']:
 trunk=bpy.data.objects[t['trunk']];vs=[trunk.matrix_world@v.co for v in trunk.data.vertices];center=sum(vs,Vector())/len(vs);xyerr=((center.x-t['xy'][0])**2+(center.y-t['xy'][1])**2)**.5;p=Vector((*t['xy'],.04));hits=ray(p,p-Vector((0,0,.09)));row=dict(id=t['id'],xy_error_m=xyerr,support=hits);tree_checks.append(row)
 if xyerr>1e-4 or 'R38_PARK_APPROACH_GROUND' not in hits:fail.append(row)
for route,(a,b) in r['routes'].items():
 a,b=Vector((*a,0)),Vector((*b,0))
 for i in range(41):
  p=a.lerp(b,i/40)+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(route=route,t=i/40,support=hits,head=head);bridge_samples.append(row)
  if not any(n in hits for n in [Q['deck'],'R38_PARK_APPROACH_GROUND']) or head:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,bridge_and_extension_samples=bridge_samples,tree_checks=tree_checks,terrain_height_surveyed=False,construction_acceptance=False);(B/'reports/R38_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),trees=len(tree_checks),routes=len(bridge_samples),failures=fail),indent=2));assert not fail,fail
