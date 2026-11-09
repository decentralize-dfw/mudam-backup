import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,file in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('current','scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/file));s=bpy.context.scene
 bpy.ops.object.camera_add(location=(0,46,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,61,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100
 s.world=bpy.data.worlds.new('R317_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 s.render.filepath=str(R/f'renders/qa/R317_north_wall_{label}.png');bpy.ops.render.render(write_still=True)

