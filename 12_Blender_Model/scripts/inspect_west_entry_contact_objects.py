from pathlib import Path
import bpy,json,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def coord(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];u=(M[1][1]*a-M[0][1]*b)/det;v=(-M[1][0]*a+M[0][0]*b)/det
 return [(u-C['canonical_to_pdf_offset'][0])/C['canonical_to_pdf_scale'],(v-C['canonical_to_pdf_offset'][1])/C['canonical_to_pdf_scale'],p.z]
rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 ps=[coord(ob.matrix_world@v.co) for v in ob.data.vertices]
 if not ps:continue
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if lo[0]>693 or hi[0]<676 or lo[1]>555 or hi[1]<470 or lo[2]>4.4 or hi[2]<-.1:continue
 rows.append(dict(name=ob.name,lo=lo,hi=hi,vertices=ps if len(ps)<25 else None,note=ob.get('assumption_note'),source=ob.get('source_ids')))
(B/'reports/R104_west_entry_contact_objects.json').write_text(json.dumps(rows,indent=2));print([(x['name'],x['lo'],x['hi']) for x in rows])
