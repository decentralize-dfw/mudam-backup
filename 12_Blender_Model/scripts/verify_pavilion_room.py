from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R17_build_report.json').read_text());P=json.loads((B/'config/pavilion_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
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
passage=[]
for y in [268,279,290]:
 for z in [.2,1.5,2.1]:
  hits=ray(point(165,y,z),point(177,y,z));row=dict(y=y,z=z,hits=hits);passage.append(row)
  if hits:fail.append(row)
support=[]
for x,y in [(107,279),(110,230),(150,270),(150,310),(106,330),(64,300),(95,290),(171,279),(175,279)]:
 hits=ray(point(x,y,.1),point(x,y,-.4));row=dict(x=x,y=y,hits=hits);support.append(row)
 if not any(n in ['R17_GROUND_FLOOR','P05_LINK_FLOOR'] for n in hits):fail.append(row)
c=Vector(r['stair_center']);voidhits=ray(c+Vector((0,0,.15)),c-Vector((0,0,.6)))
if voidhits:fail.append(dict(stair_reserve_hits=voidhits))
window=[]
for y in [269,279,289]:
 for z in [1.3,2.3,3.3]:
  hits=ray(point(40,y,z),point(47,y,z));row=dict(y=y,z=z,hits=hits);window.append(row)
  if hits!=['R17_WINDOW_GLASS']:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,bridge_portal=passage,floor_support=support,window_view=window,stair_reserve_open=not voidhits,stair_and_guard_complete=False,construction_acceptance=False);(B/'reports/R17_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
