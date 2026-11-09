from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r157';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R156_SCHUMAN_CEVRE_v002.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND','R154_FAR_ROADS') or o.name.startswith(('R152_PATH_','R152_FORECOURT_'))):rows.append(dict(name=o.name,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons]))
(D/'terrain_input.json').write_text(json.dumps(rows));print('TERRAIN_EXPORTED',len(rows),flush=True)
