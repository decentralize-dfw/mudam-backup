from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R/'.local_source_cache/act_context/local_glb';bpy.ops.wm.read_factory_settings(use_empty=True)
for row in json.loads((src/'manifest.json').read_text())['tiles']:
 b=np.array(row['bounds_local']);lo=b.min(0);hi=b.max(0)
 if hi[0]<-250 or lo[0]>400 or hi[1]<240 or lo[1]>650:continue
 bpy.ops.import_scene.gltf(filepath=str(src/row['file']))
for m in bpy.data.materials:
 if not m.use_nodes:continue
 tex=next((n for n in m.node_tree.nodes if n.type=='TEX_IMAGE'),None)
 if tex:
  em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],m.node_tree.nodes.get('Material Output').inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.resolution_x=1800;s.render.resolution_y=1800;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.world=bpy.data.worlds.new('Reference');s.world.color=(0,0,0)
bpy.ops.object.camera_add(location=(75,445,400));s.camera=bpy.context.object;s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=650
s.render.filepath=str(R/'renders/qa/R176_north_source_top.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'),compress=True)
print('FORT_REFERENCE_READY')

