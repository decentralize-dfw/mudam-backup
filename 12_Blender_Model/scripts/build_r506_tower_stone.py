import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R505_KULE_CATISI_FOTOGRAF_MALZEME_ADAY_v001.blend'));m=bpy.data.materials.new('R506_TOWER_SANDSTONE_CC0');m.use_nodes=True;nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=0;uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='R506_STONE_3M'
for suffix,fmt,socket,space in [('diff','jpg','Base Color','sRGB'),('nor_gl','png','Normal','Non-Color'),('rough','jpg','Roughness','Non-Color')]:
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/f'textures/polyhaven_sandstone_blocks_04/sandstone_blocks_04_{suffix}_2k.{fmt}'),check_existing=True);t.image.colorspace_settings.name=space;links.new(uvnode.outputs['UV'],t.inputs['Vector'])
 if socket=='Normal':n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.65;links.new(t.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bs.inputs[socket])
 else:links.new(t.outputs['Color'],bs.inputs[socket])
m['source']='Generic compatible CC0 sandstone, Rob Tuytel / Poly Haven sandstone_blocks_04. Refer reports/R506_MATERIAL_SOURCE.json. Not a reproduction of actual facade joint layout.';rows=[]
for label,cx,cy in [('WEST',-71.5,-47.6),('CENTRE',-61.6,-53.15),('SOUTH',-57.076460370468,-63.11257545086857)]:
 o=bpy.data.objects['R424_'+label+'_TOWER_BODY'];me=o.data;old=[ma.name for ma in me.materials];me.materials.clear();me.materials.append(m);uv=me.uv_layers.new(name='R506_STONE_3M')
 for f in me.polygons:
  q=o.matrix_world@f.center;rad=Vector((q.x-cx,q.y-cy,0));radius=rad.length;theta=math.atan2(rad.y,rad.x);useCylinder=radius>0 and abs(f.normal.dot(rad.normalized()))>.55 and abs(f.normal.z)<.7
  for li in f.loop_indices:
   v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co
   if useCylinder:
    ang=math.atan2(v.y-cy,v.x-cx);ang=theta+math.atan2(math.sin(ang-theta),math.cos(ang-theta));u=ang*radius/3;vv=v.z/3
   elif abs(f.normal.z)>.7:u,vv=v.x/3,v.y/3
   else:u,vv=(v.y if abs(f.normal.x)>.6 else v.x)/3,v.z/3
   uv.data[li].uv=(u,vv)
 me.uv_layers.active=uv;uv.active_render=True;rows.append(dict(name=o.name,oldMaterials=old,newMaterial=m.name))
out=R/'scenes/MUDAM_R506_KULE_TASI_PBR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R506_BUILD.json').write_text(json.dumps(dict(rows=rows,reopened=True,accepted=False,published=False,geometryChanged=False,source='R506_MATERIAL_SOURCE.json'),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=750;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-46,-37,5.4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.filepath=str(R/'renders/qa/R506_roof_court_candidate.png');bpy.ops.render.render(write_still=True)
