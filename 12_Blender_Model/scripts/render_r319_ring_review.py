import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,file in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('revised','scenes/MUDAM_R319_SUR_ZEMIN_TEMAS_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/file));s=bpy.context.scene;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('Review');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 for name,eye,target,scale in [('east',(100,-10,35),(48,-7,-2),80),('fort',(-140,-140,75),(-45,-40,-2),120)]:
  s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.filepath=str(R/f'renders/qa/R319_{name}_{label}.png');bpy.ops.render.render(write_still=True)
