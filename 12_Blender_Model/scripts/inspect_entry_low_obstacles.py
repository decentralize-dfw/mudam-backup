from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';q=json.loads((B/'reports/R63_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/q['file']));r=json.loads((B/'reports/R57_build_report.json').read_text());O,U,N=map(Vector,[r['origin'],r['axis'],r['outward']]);dep=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(dep);me=eo.to_mesh();w=eo.matrix_world.copy();pts=[w@v.co-O for v in me.vertices];eo.to_mesh_clear()
 if not pts:continue
 x=[p.dot(U) for p in pts];d=[p.dot(N) for p in pts];z=[p.z for p in pts]
 if min(x)<.8 and max(x)>-.8 and min(d)<2.3 and max(d)>-.25 and max(z)>.025 and min(z)<.4:rows.append(dict(name=ob.name,x=[min(x),max(x)],d=[min(d),max(d)],z=[min(z),max(z)],type=ob.get('element_type',''),source=ob.get('source_ids','')))
(B/'reports/R64_entry_low_obstacle_probe.json').write_text(json.dumps(dict(file=q['file'],objects=rows),indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
