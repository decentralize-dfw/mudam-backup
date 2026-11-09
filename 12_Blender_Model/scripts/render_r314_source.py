import bpy
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'));s=bpy.context.scene;bpy.ops.object.camera_add();s.camera=bpy.context.object;t=Vector((187,25,12));s.camera.location=t+Vector((55,-80,30));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.engine='CYCLES';s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=8
s.world=bpy.data.worlds.new('Reference');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
s.render.filepath=str(R/'renders/qa/R314_south_corner_source.png');bpy.ops.render.render(write_still=True)
