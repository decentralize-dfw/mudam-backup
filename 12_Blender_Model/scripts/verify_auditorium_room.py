from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R19_build_report.json').read_text());P=json.loads((B/'config/auditorium_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
s,dx,dy=C['basement_registration']['source_to_canonical'];LOW=r['lower_z']
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy
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
support=[]
for i in range(8):
 for x in [490,522,555]:
  y=441+(i+.5)*8;z=LOW+(i+1)*P['row_rise_m'];p=point(x,y,z+.05);hits=ray(p,p-Vector((0,0,.1)));head=ray(p+Vector((0,0,.01)),p+Vector((0,0,2.05)));row=dict(x=x,y=y,z=z,hits=hits,head_obstructions=head);support.append(row)
  if f'R19_TIER_{i+1:02d}' not in hits or head:fail.append(row)
for x in [475,570]:
 for i in range(16):
  y=441+(i+.5)*4;z=LOW+(i+1)*P['row_rise_m']/2;p=point(x,y,z+.04);hits=ray(p,p-Vector((0,0,.08)));head=ray(p,p+Vector((0,0,2.05)));row=dict(x=x,y=y,z=z,hits=hits,head_obstructions=head);support.append(row)
  if not any(n.startswith('R19_AISLE_') for n in hits) or head:fail.append(row)
passages=[]
for x in [472,474.5,477,568,570.5,573]:
 for h in [.2,1.5,2.1]:
  hits=ray(point(x,412,LOW+h),point(x,429,LOW+h));row=dict(x=x,h=h,hits=hits);passages.append(row)
  if hits:fail.append(row)
for x,y in [(474,416),(570,416),(475,434),(570,434),(522,434),(480,515),(522,515),(570,515)]:
 z=LOW+(1.92 if y>505 else 0);p=point(x,y,z+.04);hits=ray(p,p-Vector((0,0,.08)));row=dict(x=x,y=y,hits=hits);support.append(row)
 if not hits:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,support_and_head_samples=support,front_entry_rays=passages,physical_seats_complete=False,construction_acceptance=False);(B/'reports/R19_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
