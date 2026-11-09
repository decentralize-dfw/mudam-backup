from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for rev,scene in [('026','MUDAM_R169_KAYNAK_SACAK_ADAY_v026.blend'),('027','MUDAM_R169_SACAK_DUVAR_BAG_ADAY_v027.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/scene));m=bpy.data.materials.new('QA_CLAY');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.55,.55,.55,1)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   for i in range(len(o.data.materials)):o.data.materials[i]=m
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/f'renders/qa/R169_row_clay_v{rev}.png');bpy.ops.render.render(write_still=True)
