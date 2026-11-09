import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for label,scene in [('current',R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'),('source',R/'.local_source_cache/r316/museum_ring_reference.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene
 if label=='current':
  rows=[]
  for o in s.objects:
   if o.name.startswith('R158_TREE_'):o.hide_render=True
   if o.type!='MESH' or o.hide_render:continue
   bb=[o.matrix_world@Vector(v)for v in o.bound_box];lo=[min(v[i]for v in bb)for i in range(3)];hi=[max(v[i]for v in bb)for i in range(3)]
   if hi[0]>-53 and lo[0]<-28 and hi[1]>-10 and lo[1]<23 and hi[2]<4:rows.append(dict(name=o.name,lo=lo,hi=hi))
  (R/'reports/R586_WEST_OBJECTS.json').write_text(json.dumps(rows,indent=2))
 s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100
 bpy.ops.object.camera_add(location=(-40,8,65));s.camera=bpy.context.object;s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=38;s.render.filepath=str(R/f'renders/qa/R586_west_top_{label}.png');bpy.ops.render.render(write_still=True)
