"""R06: source-limited lower foyer ceiling and curved void-edge fascia."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
r=json.loads((B/'reports/R05_build_report.json').read_text());q=json.loads((B/'reports/R05_verification.json').read_text());assert r['file']==q['file'] and not q['failures']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R06_ALT_FUAYE_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;root=bpy.data.collections.new('P16_LOWER_FOYER_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
lower=r['lower_z'];clear_height=4.67;bottom=lower+clear_height;top=-.2
# Copy raw source-aligned footprint, including its existing void Boolean.
floor=bpy.data.objects[r['changed_floor']];ceiling=floor.copy();ceiling.data=floor.data.copy();ceiling.name='R06_FOYER_CEILING_AND_CURVED_FASCIA';root.objects.link(ceiling)
oldlo=min(v.co.z for v in ceiling.data.vertices);oldhi=max(v.co.z for v in ceiling.data.vertices)
for v in ceiling.data.vertices:v.co.z=bottom+(v.co.z-oldlo)/(oldhi-oldlo)*(top-bottom)
# Intersect with the actual registered 104 basement floor footprint. This avoids
# inventing ceiling beyond the foyer boundary merely because L00 extends there.
base=bpy.data.objects['P05_ZONE_LM1_GALLERIES_FOYER'];clip=base.copy();clip.data=base.data.copy();clip.name='R06_BASEMENT_FOOTPRINT_CLIP';root.objects.link(clip);clip.modifiers.clear()
lo=min(v.co.z for v in clip.data.vertices);hi=max(v.co.z for v in clip.data.vertices)
for v in clip.data.vertices:v.co.z=bottom-1+(v.co.z-lo)/(hi-lo)*(top-bottom+2)
clip.hide_render=True;clip.hide_set(True);clip.display_type='WIRE';mod=ceiling.modifiers.new('registered_104_foyer_extent','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=clip
# Resolve the intersection into an independent mesh; remove numerical slivers
# within 10 micrometres, while keeping both source objects and recipe intact.
deps=bpy.context.evaluated_depsgraph_get();evaluated=ceiling.evaluated_get(deps);clean=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);ceiling.modifiers.clear();ceiling.data=clean
bm=bmesh.new();bm.from_mesh(clean);before=bm.calc_volume(signed=True);verts_before=len(bm.verts);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after=bm.calc_volume(signed=True);cleanup=dict(merge_tolerance_m=1e-5,vertices_removed=verts_before-len(bm.verts),volume_change_m3=after-before);bm.to_mesh(clean);bm.free()
for k in list(ceiling.keys()):del ceiling[k]
for k,v in dict(element_id=ceiling.name,element_type='ceiling_finish_volume_with_curved_void_fascia',zone_id='LOWER_FOYER',level_id='LM1_L00',source_ids='051,052,054,055,102,104,114,LCB_FOYER',confidence_xy='C registered visitor footprints and conditional R05 void',confidence_z='C published room clearance combined with D lower floor datum',confidence_detail='D finish thickness inferred from conditional datum',confidence_material='D generic limestone family; no measured finish',assumption_note='4.67 m is published foyer clear height, not floor-to-floor height. Applying it to the current conditional basement datum is a candidate. Curved edge and broad ceiling visible in 055. No hidden structure or light layout invented.',status='conditional_foyer_ceiling_pilot',visibility_group='LOWER_FOYER',export_group='R06_CANDIDATE',collision_role='review_only').items():ceiling[k]=v
S['stage']='R06 lower foyer ceiling with R05 retained peninsula';S['current_file']=out.name
cfg=dict(base_scene=r['file'],source_ids=['051','052','054','055','102','104','114'],height_source_url='https://lcb.lu/en/partners/122?favorite=show',height_source_local_record='reports/P02_P04_KESIT_VE_KOT_ETUDU.md',published_clear_height_m=clear_height,conditional_lower_datum_m=lower,ceiling_underside_m=bottom,ceiling_top_m=top,finish_volume_thickness_m=top-bottom,source_footprint_104_object=base.name,source_ground_footprint_object=floor.name,opening_from='R05 v004 / 102 corner and PDF218 peninsula',full_foyer_ceiling_complete=False,lighting_positions_verified=False,construction_acceptance=False)
bpy.data.texts.new('R06_SOURCE_AND_ASSUMPTIONS').write(json.dumps(cfg,indent=2))
center=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);up=Vector((0,0,1));cd=bpy.data.cameras.new('R06_FOYER_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam)
cam.location=center-ex*8+ey*5+up*(lower+1.65);target=center+up*(-1.2);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=22;S.camera=cam
S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100;S.cycles.samples=64;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R06_foyer_ceiling.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
keep=set(r['closed_objects']+[floor.name,base.name,ceiling.name])
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
cfg.update(numerical_cleanup=cleanup,file=out.relative_to(R).as_posix(),closed_objects=[ceiling.name],cutters=[clip.name],prior_scene=r['file']);(B/'reports/R06_build_report.json').write_text(json.dumps(cfg,indent=2),encoding='utf8');(B/'config/lower_foyer.json').write_text(json.dumps(cfg,indent=2),encoding='utf8');print('R06_SAVED',out)
