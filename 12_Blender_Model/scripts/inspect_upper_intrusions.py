from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def xy(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];return [((M[1][1]*a-M[0][1]*b)/det-ox)/k,((-M[1][0]*a+M[0][0]*b)/det-oy)/k,p.z]
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R95_BES_ISARET_KABUK_DUZELTME_v001.blend'))
r=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 ps=[xy(o.matrix_world@Vector(p)) for p in o.bound_box];lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 if hi[2]<4.3 or lo[2]>6:continue
 if not ((hi[0]>780 and lo[0]<920 and hi[1]>280 and lo[1]<400) or (hi[0]>400 and lo[0]<750 and hi[1]>470 and lo[1]<800)):continue
 if any(w in o.name for w in ['TREE','FRAME','GLASS','PROFILE','RAIL','TREAD','ROD','BAR','PANEL','TILE']):continue
 r.append(dict(name=o.name,lo=lo,hi=hi,level=o.get('level_id'),kind=o.get('element_type')))
(B/'reports/R96_inspection.json').write_text(json.dumps(r,indent=2));print('INSPECT',len(r))
