from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v062.blend'))
roof=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];bpy.ops.object.select_all(action='DESELECT');roof.select_set(True);bpy.context.view_layer.objects.active=roof
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
# Preserve existing surface shading across the extracted roof and body.
# Angle split preserves sharp roof feature boundaries while smoothing sampling facets.
mod=roof.modifiers.new('Measured feature creases','EDGE_SPLIT');mod.split_angle=math.radians(35);mod.use_edge_angle=True;bpy.ops.object.modifier_apply(modifier=mod.name)
img=bpy.data.images.new('R169_WHOLE_ROOF_SOURCE_COLOR',width=4096,height=4096,alpha=False)
mat=bpy.data.materials.new('R169_WHOLE_ROOF_BAKED');mat.use_nodes=True;nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=img;nodes.active=tex;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
roof.data.materials.clear();roof.data.materials.append(mat)
with bpy.data.libraries.load(str(D/'source.blend'),link=False) as (src,dst):dst.objects=src.objects
sources=[]
for ob in dst.objects:
 if ob is not None and ob.type=='MESH':bpy.context.collection.objects.link(ob);sources.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in sources:ob.select_set(True)
bpy.context.view_layer.objects.active=sources[0];bpy.ops.object.join();sources=[bpy.context.object]
for sm in sources[0].data.materials:
 if not sm or not sm.use_nodes:continue
 nt=sm.node_tree;st=next((n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image),None)
 if st:
  em=nt.nodes.new('ShaderNodeEmission');nt.links.new(st.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES' ;s.cycles.samples=1;s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=1.5;s.render.bake.max_ray_distance=3.0;s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=False;s.render.bake.use_pass_color=True;s.render.bake.margin=16
bpy.ops.object.select_all(action='DESELECT')
for ob in sources:ob.select_set(True)
roof.select_set(True);bpy.context.view_layer.objects.active=roof;bpy.ops.object.bake(type='EMIT')
img.filepath_raw=str(R/'textures/R169_whole_roof_source_v062.png');img.file_format='PNG';img.save();mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for ob in sources:bpy.data.objects.remove(ob,do_unlink=True)
path=R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v062.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
s=bpy.context.scene;s.render.bake.use_selected_to_active=False;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48
for tag,pos in [('rear',(-100,-270,-36)),('front',(-55,-335,-35)),('top',(-80,-301,-15))]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector((-80,-301,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('renders/qa/R169_whole_v062_'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('WHOLE_ROOF_BAKED',path)



