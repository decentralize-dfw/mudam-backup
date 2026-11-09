import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R495_PAVYON_DIS_SUR_DONUS_ADAY_v001.blend'));records=[]
for name in ['R152_CLASS2_TERRAIN','R485_NW_LAWN']:
 o=bpy.data.objects[name];me=o.data;groups={};keys={}
 for p in me.polygons:
  group=0 if name=='R152_CLASS2_TERRAIN' else (1 if p.normal.z>.3 else -1 if p.normal.z<-.3 else 2)
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;key=(group,round(v.x,6),round(v.y,6),round(v.z,6));keys[li]=key
   if key not in groups:groups[key]=Vector((0,0,0))
   groups[key]+=p.normal*p.area
  p.use_smooth=True
 normals=[groups[keys[i]].normalized() for i in range(len(me.loops))];me.normals_split_custom_set(normals);records.append(dict(name=name,vertices=len(me.vertices),faces=len(me.polygons),change='area-weighted shared-position custom normals only; vertex coordinates, topology and UVs unchanged; lawn top/bottom/side normal groups separated'))
mat=bpy.data.materials['R457_LOADING_COURT_MINERAL'];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92;t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures/R157_ground_micro_normal.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='R497_MINERAL_METRIC';normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.15;links.new(uvnode.outputs['UV'],t.inputs['Vector']);links.new(t.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
for o in bpy.context.scene.objects:
 if o.type!='MESH' or mat not in list(o.data.materials):continue
 me=o.data;uv=me.uv_layers.get('R497_MINERAL_METRIC') or me.uv_layers.new(name='R497_MINERAL_METRIC')
 for p in me.polygons:
  for li in p.loop_indices:
   v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co
   uv.data[li].uv=(v.x/3,v.y/3) if abs(p.normal.z)>.7 else((v.y if abs(p.normal.x)>.7 else v.x)/3,v.z/3)
 if me.uv_layers.get('UVMap'):me.uv_layers.active=me.uv_layers['UVMap'];me.uv_layers['UVMap'].active_render=True
 records.append(dict(name=o.name,change='mineral surface micro-normal coordinates added'))
out=R/'scenes/MUDAM_R497_ARAZI_YUZEY_NORMAL_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R497_SURFACE_BUILD.json').write_text(json.dumps(dict(records=records,reopened=True,accepted=False,published=False),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=680;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(90,-105,55));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((28,-36,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.filepath=str(R/'renders/qa/R497_pavilion_candidate.png');bpy.ops.render.render(write_still=True)
