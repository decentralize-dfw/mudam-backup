"""R16 separate source-visible coated roof framing from exposed interior metal."""
from pathlib import Path
import bpy,json,sys,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';base='MUDAM_R14_BATI_CAM_MERDIVEN_v003.blend';out=B/'scenes'/f'MUDAM_R16_DIS_PROFIL_MALZEME_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
params=dict(base_color_linear=[.008,.011,.014,1],roughness=.48,metallic=0.0,source_ids=['089','090','092','093','094','097','099'],confidence='Photographs support dark coated appearance; exact alloy, coating chemistry, colorimetric values and weathering are unverified.')
mat=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'].copy();mat.name='R16_EXTERIOR_DARK_COATING_CANDIDATE';mat.diffuse_color=params['base_color_linear'];node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=params['base_color_linear'];node.inputs['Metallic'].default_value=params['metallic'];node.inputs['Roughness'].default_value=params['roughness'];node.inputs['Specular IOR Level'].default_value=.3;mat['source_ids']=','.join(params['source_ids']);mat['confidence_material']=params['confidence'];changed=[]
for ob in bpy.context.scene.objects:
 kind=ob.get('element_type','');selected=(ob.name.startswith('P10_') and kind in ['surface_mullion','perimeter_frame']) or (ob.name.startswith('P11_') and kind=='surface_frame') or ob.name.startswith(('R13_FRAME_','R11_END_FRAME_'))
 if not selected:continue
 assert ob.type=='MESH' and len(ob.data.materials)==1,ob.name
 old=ob.data.materials[0].name;ob.data.materials[0]=mat;ob['confidence_material']=params['confidence'];ob['material_source_ids']=','.join(params['source_ids']);changed.append(dict(name=ob.name,old_material=old,new_material=mat.name))
assert len(changed)>500,len(changed)
bpy.context.scene['stage']='R16 source-visible exterior frame finish';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R16_MATERIAL_SOURCE_LIMITS').write(json.dumps(params,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'config/exterior_frame_finish.json').write_text(json.dumps(params,indent=2),encoding='utf8');(B/'reports/R16_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,assignments=changed,changed_inherited_objects=[q['name'] for q in changed],geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8');print('R16 assigned',len(changed))
