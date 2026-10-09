from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];r=json.loads((B/'reports/R116_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def c(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];return [((M[1][1]*a-M[0][1]*b)/det-ox)/k,((-M[1][0]*a+M[0][0]*b)/det-oy)/k,p.z]
rows=[];deps=bpy.context.evaluated_depsgraph_get();r54=json.loads((B/'reports/R54_build_report.json').read_text());from mathutils import Vector
origin=Vector(r54['origin']);axis=Vector(r54['axis']);normal=Vector(r54['inside'])
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not (o.name.startswith(('R27_','R54_WINDOW_01','R116_LOWER','R35_WALL_51946353','P05_FLOOR_LP1_'))):continue
 e=o.evaluated_get(deps);me=e.to_mesh();p=[e.matrix_world@q.co for q in me.vertices];v=[c(q) for q in p]
 if p:rows.append(dict(name=o.name,hidden=o.hide_render,local_min=[min((q-origin).dot(axis) for q in p),min((q-origin).dot(normal) for q in p),min(q.z for q in p)],local_max=[max((q-origin).dot(axis) for q in p),max((q-origin).dot(normal) for q in p),max(q.z for q in p)],canonical=v if len(v)<40 else [],modifiers=[dict(name=m.name,type=m.type,object=m.object.name if m.type=='BOOLEAN' and m.object else None) for m in o.modifiers]))
 e.to_mesh_clear()
(B/'reports/R117_target_inventory.json').write_text(json.dumps(rows,indent=2))
