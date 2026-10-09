"""R43 top-face UV finish only; retain floor openings and all evaluated geometry."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/stone_floor_finish.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R43_TAS_DOSEME_YUZEYI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));UV='R43_METRIC_FLOOR_UV';M=C['pdf_to_utm_matrix'];u=Vector((M[0][0],M[1][0],0)).normalized();v=Vector((M[0][1],M[1][1],0)).normalized();mat=bpy.data.materials.new('R43_STONE_FLOOR_APPEARANCE_CANDIDATE');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=P['roughness'];uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R43_stone_floor_candidate_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';nt.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  nn=nt.nodes.new('ShaderNodeNormalMap');nn.uv_map=UV;nn.inputs['Strength'].default_value=P['normal_strength'];nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
mat['source_ids']=','.join(P['source_ids']);mat['status']='procedural_floor_candidate_not_measured';changed=[];rows=[]
for name in P['objects']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy();me=ob.data;slot=len(me.materials);me.materials.append(mat);uv=me.uv_layers.new(name=UV);me.uv_layers.active=uv;faces=[];normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
 for face in me.polygons:
  if (normal_matrix@face.normal).normalized().z<.99:continue
  face.material_index=slot;faces.append(face.index)
  for li in face.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/P['repeat_m'],q.dot(v)/P['repeat_m'])
 assert faces,name
 ob['floor_appearance_revision']='R43';ob['floor_appearance_limits']='0.9m grid and direction are appearance candidates, not surveyed joints';changed.append(name);rows.append(dict(name=name,faces=faces))
bpy.context.scene['stage']='R43 stone floor finish candidate';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R43_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R43_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],changed_inherited_objects=changed,surface_objects=rows,uv_map=UV,basis_u=list(u),basis_v=list(v),material=mat.name,geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
