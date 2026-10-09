from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R44_global_audit_before.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
def pt(x,y):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
origin=pt(0,0);u=pt(1,0)-origin;v=pt(0,1)-origin;rows=[]
for row in r['open_or_nonmanifold_objects']:
 o=bpy.data.objects[row['name']];world=[o.matrix_world@x.co for x in o.data.vertices];canonical=[[(p-origin).dot(u)/u.length_squared,(p-origin).dot(v)/v.length_squared,p.z] for p in world];normal=(o.matrix_world.to_3x3().inverted().transposed()@o.data.polygons[0].normal).normalized();rows.append(dict(name=o.name,canonical_vertices=canonical,world_vertices=[list(p) for p in world],normal=list(normal),material_names=[m.name for m in o.data.materials],source_ids=o.get('source_ids','')))
(B/'reports/R44_open_surface_geometry.json').write_text(json.dumps(dict(file=r['file'],surfaces=rows),indent=2),encoding='utf8')
for row in rows:print(row['name'],[[round(x,2) for x in p] for p in row['canonical_vertices']])
