"""R84 restore fixed entry glazing contact with floor, visible in013/014."""
from pathlib import Path
import bpy,bmesh,json,re
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R83_CATI_KENAR_KAPANISLARI_v001.blend';out=B/'scenes/MUDAM_R84_GIRIS_ALT_CAM_KAPANISI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));changed=[];before={}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or not re.match(r'ENT-0[123]-L00_(FRAME_(LEFT|RIGHT|SILL)|GLASS($|_LEFT_SIDE$|_RIGHT_SIDE$))',ob.name):continue
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];lo=min(v.z for v in vs);assert .17<lo<.26,(ob.name,lo);before[ob.name]=[list(v) for v in vs];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
 for v,w in zip(ob.data.vertices,vs):
  if ob.name.endswith('FRAME_SILL'):w.z-=.18
  elif abs(w.z-lo)<1e-5:w.z=(0. if 'FRAME_' in ob.name or 'SIDE' in ob.name else .07)
  v.co=inv@w
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob['floor_closure_revision']='R84 fixed glazing base to013/014 floor contact; operable leaves unchanged';changed.append(ob.name)
assert len(changed)==12,changed
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=changed,changed_inherited_objects=changed,before_world_vertices=before,source_ids=['013','014','102'],construction_acceptance=False,limits=['Fixed glass and perimeter frames had18..25cm unsupported ground gap.013 shows floor contact.','Two existing bottom frame sections moved toz0; fixed glass above them meetsz.07. Central fixed side panes continue tofloor.','Top/plan coordinates and all operable leaves preserved. Profiles and exact floor tolerances remain candidates.'])
bpy.context.scene['stage']='R84 fixed entry glazing lower enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R84_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R84_build_report.json').write_text(json.dumps(r,indent=2));print('R84',len(changed),'fixed elements')
