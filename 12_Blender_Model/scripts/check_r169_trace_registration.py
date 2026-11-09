from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';a=json.loads((D/'upper_roof_trace_33.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));dg=bpy.context.evaluated_depsgraph_get()
for v in a['vertices']:
 hit,q,*_=bpy.context.scene.ray_cast(dg,Vector((v[0],v[1],0)),Vector((0,0,-1)),distance=150);print(v,'direct',tuple(q) if hit else None)
bpy.ops.object.camera_add();bpy.context.object.data.type='ORTHO';bpy.context.object.data.ortho_scale=29;s=bpy.context.scene;s.render.resolution_x=1400;s.render.resolution_y=1100;print('FRAME',[tuple(p) for p in bpy.context.object.data.view_frame(scene=s)])
