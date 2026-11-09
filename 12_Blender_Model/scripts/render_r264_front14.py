import bpy,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'))
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]
 if max(p.x for p in pts)<185 or min(p.x for p in pts)>225 or max(p.y for p in pts)<435 or min(p.y for p in pts)>483:
  o.hide_render=True;continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=[v for v in bm.verts if not (185<(o.matrix_world@v.co).x<225 and 435<(o.matrix_world@v.co).y<483 and (o.matrix_world@v.co).z<22)];bmesh.ops.delete(bm,geom=bad,context='VERTS');bm.to_mesh(o.data);bm.free()
s=bpy.context.scene;t=Vector((204,458,5));s.camera.location=t+Vector((.6542447*35,-.7562829*35,8));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=28;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R264_front14_source.png');bpy.ops.render.render(write_still=True)
