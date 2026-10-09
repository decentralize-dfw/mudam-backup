from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R114_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));C=json.loads((B/'config/foundation.json').read_text())['calibration'];s,dx,dy=C['basement_registration']['source_to_canonical'];LOW=json.loads((B/'reports/R19_build_report.json').read_text())['lower_z']
def pt(x,y,z):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
dep=bpy.context.evaluated_depsgraph_get();objects=[o.evaluated_get(dep) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render];rows=[]
for x in [514,518,522,526,530,532]:
 for z in [LOW+2.85,LOW+3.15,LOW+3.5]:
  p=pt(x,503,z);q=pt(x,508,z);d=(q-p).normalized();hits=[]
  for o in objects:
   iv=o.matrix_world.inverted();ok,loc,_,_=o.ray_cast(iv@p,iv.to_3x3()@d,distance=(q-p).length)
   if ok:hits.append(dict(name=o.name,distance=(o.matrix_world@loc-p).length,materials=[m.name if m else None for m in o.data.materials]))
  rows.append(dict(x=x,z=z,hits=sorted(hits,key=lambda a:a['distance'])))
q=dict(file=r['file'],window_front_probes=rows);(B/'reports/R114_auditorium_window_probe.json').write_text(json.dumps(q,indent=2),encoding='utf8');print(json.dumps(q,indent=2))
