import bpy,json,re,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R552_BATI_EGIMLI_TAS_SUR_GOVDESI_ADAY_v001.blend'));m=bpy.data.materials.new('R554_WEATHERED_COURSED_STONE_CC0');m.use_nodes=True;nd=m.node_tree.nodes;lk=m.node_tree.links;p=nd.get('Principled BSDF');p.inputs['Metallic'].default_value=0;uvnode=nd.new('ShaderNodeUVMap');uvnode.uv_map='R554_STONE_METRIC_2_5M'
for suf,fmt,socket,space in [('diff','jpg','Base Color','sRGB'),('nor_gl','png','Normal','Non-Color'),('rough','jpg','Roughness','Non-Color')]:
 t=nd.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/f'textures/polyhaven_castle_wall_slates/castle_wall_slates_{suf}_2k.{fmt}'),check_existing=True);t.image.colorspace_settings.name=space;lk.new(uvnode.outputs[0],t.inputs[0])
 if socket=='Normal':n=nd.new('ShaderNodeNormalMap');n.uv_map=uvnode.uv_map;n.inputs['Strength'].default_value=.55;lk.new(t.outputs[0],n.inputs['Color']);lk.new(n.outputs[0],p.inputs['Normal'])
 else:lk.new(t.outputs[0],p.inputs[socket])
rows=[]
for o in bpy.context.scene.objects:
 num=re.match(r'R(\d+)_',o.name);num=int(num[1])if num else 0
 if o.type!='MESH' or o.hide_render or not(num in (152,154)or 317<=num<=552):continue
 slots=[i for i,ma in enumerate(o.data.materials)if ma and ma.name=='R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE']
 if not slots:continue
 for i in slots:o.data.materials[i]=m
 uv=o.data.uv_layers.get('R554_STONE_METRIC_2_5M')or o.data.uv_layers.new(name='R554_STONE_METRIC_2_5M')
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(f.normal.z)>.6:co=(v.x/2.5,v.y/2.5)
   elif abs(f.normal.x)>.7:co=(v.y/2.5,v.z/2.5)
   else:co=(v.x/2.5,v.z/2.5)
   uv.data[li].uv=co
 rows.append(dict(name=o.name,slots=slots))
m['source']='Rob Tuytel / Poly Haven castle_wall_slates, CC0, nominal2.5m width. Actual museum photo063 informs material class only; not exact stone-joint replication.'
out=R/'scenes/MUDAM_R554_SUR_ASINMIS_TAS_PBR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R554_BUILD.json').write_text(json.dumps(dict(objects=rows,reopened=True,geometryChanged=False,accepted=False,source='R554_MATERIAL_SOURCE.json',rejectedMaterial='R553 defense_wall: dark irregular basalt-like appearance inconsistent with local photo063'),indent=2));print('MATERIALS',len(rows),flush=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=500;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-20,-2,-5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-20,1,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=18;s.render.filepath=str(R/'renders/qa/R554_stone_candidate.png');bpy.ops.render.render(write_still=True)
