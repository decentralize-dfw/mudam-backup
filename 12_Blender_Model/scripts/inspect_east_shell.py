from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R10_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];A=Matrix([[M[0][0]*k,M[0][1]*k],[M[1][0]*k,M[1][1]*k]]);off=Vector((M[0][0]*ox+M[0][1]*oy+M[0][2]-293425,M[1][0]*ox+M[1][1]*oy+M[1][2]-5499960))
def point(p,z):
 q=A@Vector(p)+off;return Vector((q.x,q.y,z))
deps=bpy.context.evaluated_depsgraph_get();hits=[]
for height in [1,3,5]:
 a=point([429,378],1.65);b=point([309,329],height);d=(b-a).normalized()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  ev=ob.evaluated_get(deps);iv=ev.matrix_world.inverted();ok,loc,no,ix=ev.ray_cast(iv@a,iv.to_3x3()@d,distance=(b-a).length)
  if ok:hits.append(dict(name=ob.name,height=height,distance=(ev.matrix_world@loc-a).length))
walls=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or len(ob.data.vertices)>20:continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices];coords=[list(A.inverted()@(Vector((p.x,p.y))-off))+[p.z] for p in ps]
 if coords and any(280<p[0]<465 and 155<p[1]<450 for p in coords):walls.append(dict(name=ob.name,vertices=coords))
(B/'reports/R10_context_obstructions.json').write_text(json.dumps(dict(hits=sorted(hits,key=lambda h:(h['height'],h['distance'])),nearby_surfaces=walls),indent=2),encoding='utf8');print(json.dumps(hits,indent=2))
