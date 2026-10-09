from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];r=json.loads((B/'reports/R115_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def c(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];return [((M[1][1]*a-M[0][1]*b)/det-ox)/k,((-M[1][0]*a+M[0][0]*b)/det-oy)/k,p.z]
rows=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 if not any(t in o.name for t in ['FLOOR','WALL','FRONT','RECESS','LINER','PETITE','ROOM_','BOUNDARY','PORTAL','P05_PAV','R29_','R19_ENTRY','R19_STAGE_BACK','R87_','R30_LANDING']):continue
 e=o.evaluated_get(deps);me=e.to_mesh();v=[c(e.matrix_world@q.co) for q in me.vertices]
 if v:rows.append(dict(name=o.name,min=[min(q[i] for q in v) for i in range(3)],max=[max(q[i] for q in v) for i in range(3)],verts=v if len(v)<70 else [],materials=[m.name for m in o.data.materials]))
 e.to_mesh_clear()
(B/'reports/R116_geometry_inventory.json').write_text(json.dumps(rows,indent=2))
