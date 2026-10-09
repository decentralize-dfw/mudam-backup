from pathlib import Path
import bpy,json
b=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(b/'scenes/MUDAM_R98_UST_KOPRU_DUVAR_SINIRI_v001.blend'));c=json.loads((b/'config/foundation.json').read_text())['calibration'];m=c['pdf_to_utm_matrix'];det=m[0][0]*m[1][1]-m[0][1]*m[1][0]
def xy(p):
 a=p.x+293425-m[0][2];v=p.y+5499960-m[1][2];return [((m[1][1]*a-m[0][1]*v)/det-c['canonical_to_pdf_offset'][0])/c['canonical_to_pdf_scale'],((-m[1][0]*a+m[0][0]*v)/det-c['canonical_to_pdf_offset'][1])/c['canonical_to_pdf_scale'],p.z]
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(s in o.name for s in ['R28_','GALLERY_HALL','R95_E_GROUND','R83_CAFE','R04_RECESS_HEAD']):continue
 ps=[xy(o.matrix_world@v.co) for v in o.data.vertices];rows.append(dict(name=o.name,hidden=o.hide_render or not o.visible_get(),lo=[min(p[i] for p in ps) for i in range(3)],hi=[max(p[i] for p in ps) for i in range(3)],status=o.get('status'),note=o.get('assumption_note')))
(b/'reports/R99_inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
