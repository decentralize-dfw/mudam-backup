import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R504_GUNEY_KULE_CATISI_OTURUM_ADAY_v001.blend'));m=bpy.data.materials.new('R505_WEATHERED_ROOF_APPEARANCE');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.395,.34,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.87
m['source']='Visible matte warm-grey roof appearance in rooftop_view_1/2_Zinneke_CC_BY_SA_3.jpg; finish appearance only, precise substrate not established. No photograph transferred.'
t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures/R157_ground_micro_normal.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color';u=m.node_tree.nodes.new('ShaderNodeUVMap');u.uv_map='R505_ROOF_METRIC';n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.055;m.node_tree.links.new(u.outputs['UV'],t.inputs['Vector']);m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],bs.inputs['Normal']);rows=[]
for label in ['WEST','CENTRE','SOUTH']:
 o=bpy.data.objects['R418_TOWER_CONICAL_ROOF_'+label];me=o.data;N=128;cx=sum(v.co.x for v in me.vertices[:N])/N;cy=sum(v.co.y for v in me.vertices[:N])/N;outer=math.hypot(me.vertices[0].co.x-cx,me.vertices[0].co.y-cy);inner=math.hypot(me.vertices[N].co.x-cx,me.vertices[N].co.y-cy);slope=(me.vertices[0].co.z-me.vertices[N].co.z)/(outer-inner);me.materials.append(m);idx=len(me.materials)-1;uv=me.uv_layers.new(name='R505_ROOF_METRIC');normals=[None]*len(me.loops)
 for p in me.polygons:
  if abs(p.normal.z)>.5:p.material_index=idx
  for li in p.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x/2,q.y/2);rad=Vector((q.x-cx,q.y-cy,0)).normalized();normals[li]=Vector((-slope*rad.x,-slope*rad.y,1)).normalized()*(1 if p.normal.z>0 else -1) if abs(p.normal.z)>.5 else rad*(1 if p.normal.dot(rad)>0 else -1)
  p.use_smooth=True
 me.normals_split_custom_set(normals);rows.append(dict(name=o.name,slope=slope,vertices=len(me.vertices),faces=len(me.polygons),geometryChanged=False))
out=R/'scenes/MUDAM_R505_KULE_CATISI_FOTOGRAF_MALZEME_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R505_BUILD.json').write_text(json.dumps(dict(rows=rows,reopened=True,accepted=False,published=False,source='references/fort_inpa/rooftop_view_1_Zinneke_CC_BY_SA_3.jpg'),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-46,-37,5.4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.filepath=str(R/'renders/qa/R505_roof_court_candidate.png');bpy.ops.render.render(write_still=True)
