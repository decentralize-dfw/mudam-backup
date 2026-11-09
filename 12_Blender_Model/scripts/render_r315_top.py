import bpy
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
for label,path in [('source',R/'.local_source_cache/r166/source.blend'),('candidate',R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(190,30,150);s.camera.rotation_euler=(0,0,0);s.camera.rotation_euler=(Vector((190,30,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.engine='CYCLES';s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=4
 s.world=bpy.data.worlds.new('Study');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/f'renders/qa/R315_tip_top_{label}.png');bpy.ops.render.render(write_still=True)
