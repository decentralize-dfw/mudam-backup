from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R26_build_report.json').read_text());P=json.loads((B/'config/upper_gallery_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
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
glass_checks=[]
for panel in r['panels']:
 c=Vector(panel['center']);hits=ray(c+Vector((0,0,.1)),c-Vector((0,0,.1)));ob=bpy.data.objects[panel['name']];zs=[(ob.matrix_world@v.co).z for v in ob.data.vertices];th=max(zs)-min(zs);row=dict(name=ob.name,hits=hits,thickness_m=th);glass_checks.append(row)
 if panel['name'] not in hits or abs(th-.018)>1e-4:fail.append(row)
roof=bpy.data.objects['P06_EAST_GLAZED_ROOF'];corners=[roof.matrix_world@v.co for v in roof.data.vertices];joins=[]
for x,y in [(289.5,266.5),(462.4,441.1)]:
 p=point(x,y,r['z']);err=min((c-p).length for c in corners);row=dict(canonical=[x,y],error_m=err);joins.append(row)
 if err>1e-4:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,glass_checks=glass_checks,roof_corner_joins=joins,construction_acceptance=False);(B/'reports/R26_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
