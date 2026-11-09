from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('TOP');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2
bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(38,-273,0);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=29;s.render.filepath=str(R/'renders/qa/R169_33_roof_source.png');bpy.ops.render.render(write_still=True)
