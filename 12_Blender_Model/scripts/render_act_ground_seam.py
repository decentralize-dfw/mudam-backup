"""Local museum-base view; do not modify the saved hybrid."""
from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v005.blend'))
scene=bpy.context.scene;cam=scene.camera
cam.location=(45,-44,4);cam.rotation_euler=(Vector((29,-43,-7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=28
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.cycles.samples=12
scene.render.filepath=str(root/'renders/qa/R151_v005_ground_seam.png')
bpy.ops.render.render(write_still=True)
print('LOCAL_SEAM_RENDER_DONE',flush=True)
