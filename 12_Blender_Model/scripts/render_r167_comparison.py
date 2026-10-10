from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,file in [('candidate',R/'scenes/MUDAM_R167_GUNEY_CATILAR_ADAY_v002.blend'),('source',R/'.local_source_cache/r167/source.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('QA');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.4,-.5,-.3);bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100
 for name,target,eye in [('south_row',(-24,-289,-66),(15,-365,0)),('malterie',(105,-155,-64),(150,-205,-5))]:
  s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R167_{label}_{name}.png');bpy.ops.render.render(write_still=True)

