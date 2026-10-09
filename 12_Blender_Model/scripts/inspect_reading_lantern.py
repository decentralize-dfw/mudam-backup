from pathlib import Path
import bpy,json
R=Path.cwd();B=R/'12_Blender_Model';r=json.loads((B/'reports/R46_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));rows=[]
for o in bpy.context.scene.objects:
 if o.name.startswith(('P17_READING_','P06_READING_','P05_MAIN_ROOF_DECK')):
  vs=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else [];rows.append(dict(name=o.name,type=o.type,hide_render=o.hide_render,hide_get=o.hide_get(),dimensions=list(o.dimensions),bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)] if vs else [],material=[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []))
(B/'reports/R47_reading_lantern_inventory.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
