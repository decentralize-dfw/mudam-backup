import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R554_SUR_ASINMIS_TAS_PBR_ADAY_v001.blend'));m=bpy.data.materials['R554_WEATHERED_COURSED_STONE_CC0'];nd=m.node_tree.nodes;lk=m.node_tree.links;tex=next(n for n in nd if n.type=='TEX_IMAGE'and '_diff_'in n.image.name);tex.image=bpy.data.images.load(str(R/'textures/R556_weathered_stone_albedo_atlas.png'),check_existing=True);uvnode=nd.new('ShaderNodeUVMap');uvnode.uv_map='R556_STONE_ATLAS_20x10';lk.new(uvnode.outputs[0],tex.inputs[0]);rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or m not in list(o.data.materials):continue
 o.data.uv_layers.new(name=uvnode.uv_map);src=o.data.uv_layers['R554_STONE_METRIC_2_5M'];dst=o.data.uv_layers[uvnode.uv_map]
 for l in o.data.loops:dst.data[l.index].uv=(src.data[l.index].uv.x/8,src.data[l.index].uv.y/4)
 rows.append(o.name)
out=R/'scenes/MUDAM_R556_SUR_TAS_DOKUSU_TEKRAR_AZALTMA_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R556_BUILD.json').write_text(json.dumps(dict(objects=rows,reopened=True,geometryChanged=False,accepted=False,source='R556_TEXTURE_PROCESS.json'),indent=2));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=500;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-20,-2,-5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-20,1,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=18;s.render.filepath=str(R/'renders/qa/R556_stone_candidate.png');bpy.ops.render.render(write_still=True)
