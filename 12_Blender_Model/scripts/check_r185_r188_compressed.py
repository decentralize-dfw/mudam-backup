from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r185_r188_district_draco_webp_REVIEW.glb'))
total=bad=0;names=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();total+=len(o.data.loop_triangles);bad+=sum(t.area<1e-10 for t in o.data.loop_triangles)
 if o.name.startswith('R188_BACKGROUND_'):names.append(o.name)
assert total==233650,total
assert len(names)==7,names
assert not bad,bad
(R/'reports/R185_R188_COMPRESSED_REOPEN.json').write_text(json.dumps(dict(reopened=True,triangles=total,degenerate=bad,background_buildings=names,full11regions_complete=False),indent=2))
print('COMPRESSED_REOPEN',total,bad,flush=True)
