from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R296_DOGU_GUNEY_CATI_ISIKLIKLAR_ADAY_v001.blend'))
o=bpy.data.objects['R295_ROOF_SLAB_0'];uv=o.data.uv_layers.new(name='R297_UNIQUE_ROOF_150M')
for l in o.data.loops:
 p=o.matrix_world@o.data.vertices[l.vertex_index].co;uv.data[l.index].uv=((p.x-175)/150,(p.y-2)/150)
o.data.uv_layers.active=uv
ma=bpy.data.materials.new('R297_AUTHORED_MINERAL_ROOF');ma.use_nodes=True;ns=ma.node_tree.nodes;links=ma.node_tree.links;bs=ns['Principled BSDF'];bs.inputs['Roughness'].default_value=.87
for name,socket in [('base','Base Color'),('roughness','Roughness'),('normal',None)]:
 im=bpy.data.images.load(str(R/f'textures/r297/mineral_{name}.png'));im.pack();tex=ns.new('ShaderNodeTexImage');tex.image=im
 if name!='base':im.colorspace_settings.name='Non-Color'
 if socket:links.new(tex.outputs['Color'],bs.inputs[socket])
 else:
  normal=ns.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35;links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
o.data.materials.clear();o.data.materials.append(ma)
path=R/'scenes/MUDAM_R297_DOGU_GUNEY_CATI_MALZEME_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.filepath=str(R/'renders/qa/R297_south_roof_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R295_'))
glb=R/'exports/r152_clean/r297_south_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
(R/'reports/R297_MATERIAL.json').write_text(json.dumps(dict(scene=str(path),accepted=False,published=False,sourcePixelsUsed=False,material='Authored mineral/gravel basecolor, normal and roughness; unique 150m UV domain without tiling',geometry='R296 unchanged',limits=['Weathering patches are visual interpretation, not surveyed','Inherited lower podium facades and ground interface still unresolved']),indent=2));print('R297_READY',flush=True)
