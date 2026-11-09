import bpy
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r165/source.blend'));s=bpy.context.scene
if not s.camera:
 bpy.ops.object.camera_add();s.camera=bpy.context.object
s.camera.location=(390,180,65);t=Vector((240,370,48));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100
if not s.world:s.world=bpy.data.worlds.new('World')
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
s.render.filepath=str(R/'renders/qa/R255_towers_source.png');bpy.ops.render.render(write_still=True)
