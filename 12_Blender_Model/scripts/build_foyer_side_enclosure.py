"""R81 trace the fixed lateral foyer returns shown in source104; preserve auditorium entrances."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R80_KUZEY_CAM_ALT_KAPANIS_v001.blend';out=B/'scenes/MUDAM_R81_ALT_FUAYE_YAN_KABUK_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];L=json.loads((B/'config/lower_foyer.json').read_text());LOW=L['conditional_lower_datum_m'];H=L['ceiling_underside_m'];up=Vector((0,0,1));s,dx,dy=C['basement_registration']['source_to_canonical'];made=[];root=bpy.data.collections.new('R81_SOURCE104_FOYER_SIDE_ENCLOSURE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);mat=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];th=.2
paths={'E':[[420,412],[435,424],[435,432],[431,433],[431,442],[457,442],[457,432],[454,432],[454,424],[457,424],[457,413],[468,413],[468,420],[464.5,421]],'W':[[580.5,421],[576,420],[576,413],[588,413],[588,424],[591,424],[591,432],[588,433],[588,460],[615,460],[615,433],[612,432],[612,424],[616,424],[623,417]]}
# Source104 outlines small side vestibule and lift-side volume. No lift mechanism or door detail inferred.
volumes={'E':[[435,424],[454,424],[454,432],[457,432],[457,442],[431,442],[431,433],[435,432]],'W':[[591,424],[612,424],[612,432],[615,433],[615,460],[588,460],[588,433],[591,432]]}
def point(p,z=0):
 x,y=p;x=x*s+dx;y=y*s+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,kind):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p+up*z) for z in [z0,z1] for p in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LM1',zone_id='LOWER_FOYER',source_ids='104,101',confidence_xy='C traced schematic fixed boundary',confidence_z='D inherited foyer datum and soffit',status='conditional_source_boundary',assumption_note='104 side returns traced; .2m centered wall envelope inherited candidate. Door/window details deferred; lift mechanism not modeled.').items():ob[k]=v
 made.append(name);return ob
for side,path in paths.items():
 pts=[point(p) for p in path];normals=[(b-a).normalized().cross(up)*th/2 for a,b in zip(pts,pts[1:])];offsets=[normals[0]]
 for a,b in zip(normals,normals[1:]):
  m=(a.normalized()+b.normalized()).normalized();offsets.append(m*(th/2)/m.dot(b.normalized()))
 offsets.append(normals[-1])
 for i,(a,b) in enumerate(zip(pts,pts[1:])):prism(f'R81_{side}_RETURN_{i:02d}',[a-offsets[i],b-offsets[i+1],b+offsets[i+1],a+offsets[i]],LOW,H,'fixed_foyer_return_wall_candidate')
 poly=[point(p) for p in volumes[side]];prism(f'R81_{side}_SIDE_FLOOR',poly,LOW-.2,LOW,'side_volume_floor_candidate');prism(f'R81_{side}_SIDE_CEILING',poly,H,-.2,'side_volume_ceiling_candidate')
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],source_ids=['104','101'],native_paths=paths,native_side_volumes=volumes,wall_thickness_candidate_m=th,lower_z=LOW,soffit_z=H,construction_acceptance=False,limits=['Source104 fixed ink boundaries support side returns; exact wall widths and levels remain candidates.','Auditorium door openings at x469..480 and565..576 are preserved.','Lift-side outer volume only; cabin, shaft depth, doors and equipment deferred.','General building enclosure audit remains open.'])
bpy.context.scene['stage']='R81 lower foyer side enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R81_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R81_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R81',len(made),'enclosure elements')
