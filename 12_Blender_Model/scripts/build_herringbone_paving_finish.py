from pathlib import Path
import bpy,json,sys,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R61_SACAK_GOMME_ISIK_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R62_BALIKSIRTI_DOSEME_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));prior=json.loads((B/'reports/R59_build_report.json').read_text());UV=prior['uv_map'];ob=bpy.data.objects[prior['surface_object']];ob.data=ob.data.copy();old=bpy.data.materials['R59_DARK_STONE_PAVING_CANDIDATE'];mat=old.copy();mat.name='R62_HERRINGBONE_STONE_CANDIDATE'
for node in mat.node_tree.nodes:
 if node.type=='TEX_IMAGE':
  suffix='normal' if 'normal' in node.image.name else 'basecolor';im=bpy.data.images.load(str(B/'textures'/f'R62_herringbone_candidate_{suffix}.png'));im.colorspace_settings.name='Non-Color' if suffix=='normal' else 'sRGB';im.pack();node.image=im
mat['source_ids']='013,014';mat['status']='herringbone_bond_supported_module_unmeasured';mat['limits']='013 corrects R59 bond. 200x50mm, joints, colour and relief are appearance candidates.'
for i,m in enumerate(ob.data.materials):
 if m==old:ob.data.materials[i]=mat
rows=[]
for f in prior['faces']:
 if f['material']==old.name:rows.append(dict(face=f['index'],u=f['u'],v=f['v'],repeat_m=f['repeat'],material=mat.name))
ob['surface_appearance_revision']='R62';ob['surface_source_ids']='013,014';ob['surface_appearance_status']='Herringbone corrected from013; module and orientation candidate';bpy.context.scene['stage']='R62 herringbone approach paving correction';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R62_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=[ob.name],surface_objects=[dict(name=ob.name,faces=rows)],uv_map=UV,materials=[mat.name],evaluated_geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['013','014']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R62_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['Herringbone visible in013 foreground;014 provides approach family only.','R59 staggered bond superseded. No geometric, level or outline alteration.','200x50mm module and4mm joints remain editable unmeasured candidates.']),indent=2),encoding='utf8');print('R62',len(rows),'faces')
