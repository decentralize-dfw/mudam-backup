"""R129 changes only existing historic-wall/turf material slots."""
from pathlib import Path
import bpy,json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parent
base='MUDAM_R128_OKUMA_DOGU_ODA_ORTU_BIRLESIM_v001.blend';out=B/'scenes/MUDAM_R129_TARIHI_TAS_VE_HENDEK_MALZEME_v002.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
replacements={};textures=[]
for label in ['historic_masonry','moat_turf']:
 old=bpy.data.materials['R55_'+label.upper()+'_APPEARANCE_CANDIDATE'];mat=old.copy();mat.name='R129_'+label.upper()+'_APPEARANCE_CANDIDATE';nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');uv=next(n for n in nt.nodes if n.type=='UVMAP')
 for n in nt.nodes:
  if n.type=='TEX_IMAGE':
   suffix='normal' if 'normal' in n.image.name else 'basecolor';im=bpy.data.images.load(str(B/'textures'/f'R129_{label}_{suffix}.png'));im.colorspace_settings.name='Non-Color' if suffix=='normal' else 'sRGB';im.pack();n.image=im;textures.append(im.name)
 rough=nt.nodes.new('ShaderNodeTexImage');im=bpy.data.images.load(str(B/'textures'/f'R129_{label}_roughness.png'));im.colorspace_settings.name='Non-Color';im.pack();rough.image=im;rough.extension='REPEAT';nt.links.new(uv.outputs['UV'],rough.inputs['Vector']);nt.links.new(rough.outputs['Color'],bs.inputs['Roughness']);textures.append(im.name)
 mat['source_ids']='063,065,116';mat['status']='source_guided_procedural_appearance_candidate';mat['limits']='Not a scan; exact stones, species, colour and physical material parameters unmeasured. Existing R55 4x3m metric UV preserved.';replacements[old.name]=mat
changed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 if any(s.material and s.material.name in replacements for s in o.material_slots):
  o.data=o.data.copy()
  for s in o.material_slots:
   if s.material and s.material.name in replacements:s.material=replacements[s.material.name]
  o['surface_appearance_revision']='R129';o['surface_source_ids']='063,065,116';changed.append(o.name)
assert len(changed)>=21,changed
bpy.context.scene['stage']='R129 historic masonry and moat surface refinement';bpy.context.scene['current_file']=out.name
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R129_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=[],changed_inherited_objects=changed,materials=[m.name for m in replacements.values()],textures=textures,geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
print('R129 material objects',len(changed))
