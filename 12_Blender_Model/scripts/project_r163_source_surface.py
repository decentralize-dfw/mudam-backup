from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_ACT2020_DOKUNULMAMIS.blend'))
s=bpy.context.scene
for o in s.objects:
 if o.type!='MESH':o.hide_render=True
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image),None)
 if tex:
  em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
  if out:nt.links.new(em.outputs[0],out.inputs['Surface'])
bpy.ops.object.camera_add(location=(75,100,500));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=1150;s.camera.data.clip_end=2000
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=4096;s.render.resolution_y=4096;s.render.resolution_percentage=100;s.render.film_transparent=True;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'textures/R163_ACT_registered_surface.png');bpy.ops.render.render(write_still=True)
(R/'reports/R163_ORTHO_PROJECTION.json').write_text(json.dumps(dict(source='MUDAM_ACT2020_DOKUNULMAMIS.blend',bounds=[-500,-475,650,675],resolution=[4096,4096],source_scene_modified=False,limits=['Vertical projection of ACT surface; canopy and roofs occlude ground.','Reference color projection, not independent ground survey.']),indent=2));print('R163_PROJECTION_READY',flush=True)

