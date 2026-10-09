"""R80 extend the existing north glazed closure to the ground datum."""
from pathlib import Path
import bpy,bmesh,json,sys,re
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R79_CATIDA_EKSIK_KOSELER_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R80_KUZEY_CAM_ALT_KAPANIS_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));changed=[];made=[];before={}
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 glass=bool(re.fullmatch(r'P11_GH_SLOT_\d{2}_00',ob.name));vertical=bool(re.fullmatch(r'P11_GH_SLOT_\d{2}_00_FRAME_[13]',ob.name))
 if glass or vertical:
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];zmin=min(v.z for v in vs);target=.0225 if glass else 0.;before[ob.name]=[list(v) for v in vs];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
  for v,w in zip(ob.data.vertices,vs):
   if abs(w.z-zmin)<2e-5:w.z=target;v.co=inv@w
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob['envelope_closure_revision']='R80 087/119 north strip continues to ground; existing column divisions retained, lower module detail unverified';changed.append(ob.name)
 if re.fullmatch(r'P11_GH_SLOT_\d{2}_00_FRAME_0',ob.name):
  new=ob.copy();new.data=ob.data.copy();new.name='R80_NORTH_SILL_'+ob.name.split('_')[3];ob.users_collection[0].objects.link(new);new.location.z-=2.9155502319335938;new['element_id']=new.name;new['source_ids']='087,119,102';new['assumption_note']='Ground closure member reuses current frame profile. Profile and module divisions remain unmeasured.';made.append(new.name)
assert len(changed)==7 and len(made)==3,(changed,made)
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=changed+made,changed_inherited_objects=changed,new_objects=made,before_world_vertices=before,source_ids=['087','119','102'],construction_acceptance=False,limits=['North glass strip visible down to ground in087/119; previous panes incorrectly began at2.938m.','Existing upper glazing and transverse bar retained; three lowest panes and four vertical members extended, three ground closure bars added.','No detailed lower panel subdivision or product specification inferred. Existing glass/profile dimensions remain candidates.'])
bpy.context.scene['stage']='R80 north lower glazed enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R80_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R80_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R80',len(changed),'extended',len(made),'sill members')
