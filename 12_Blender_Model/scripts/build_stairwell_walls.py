"""R07: the two flat stone walls behind the lower stair, supported by 114/055."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R06_build_report.json').read_text());q=json.loads((B/'reports/R06_verification.json').read_text());assert r['file']==q['file'] and not q['failures']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R07_MERDIVEN_BOSLUGU_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene
C=json.loads((B/'config/foundation.json').read_text())['calibration'];L=json.loads((B/'config/entry_package.json').read_text())['lower_roof'];band=L['band_bottom_z'];low=L['low_eave_z'];bottom=r['conditional_lower_datum_m'];thickness=.3;offset=thickness/C['meters_per_canonical_pixel'];root=bpy.data.collections.new('P07_P16_STAIRWELL_WALLS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
made=[];definitions=[]
for side,poly,heights in [('NORTH',[[592,334],[688,334],[688+offset,334-offset],[592,334-offset]],[band,low,low,band]),('WEST',[[688,334],[688,430],[688+offset,430],[688+offset,334-offset]],[low,band,band,low])]:
 name='R07_STAIRWELL_STONE_'+side;verts=[tuple(point(p,bottom)) for p in poly]+[tuple(point(p,z)) for p,z in zip(poly,heights)];faces=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(bpy.data.materials['P05_NEUTRAL_ENVELOPE'])
 for k,v in dict(element_id=name,element_type='flat_stone_wall_envelope',zone_id='GH_DOWN',level_id='LM1_L00',source_ids='114,045,051,055,102,104,087,119',confidence_xy='C visitor plan boundary',confidence_z='D inherited section/photo roof edge and basement datum',confidence_detail='D 0.30 m display thickness; no hidden wall buildup',confidence_material='C stone family, D uncalibrated generic shader',parameter_ids='stairwell_walls.json',status='conditional_stairwell_wall_candidate',assumption_note='114 shows two flat stone walls meeting below the triangular roof. This is not a curved wall inferred from stair lines. Roof-end heights inherit the earlier conditional fit; basement floor edge alignment remains approximate.',export_group='R07_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);definitions.append(dict(name=name,footprint_canonical=poly,top_heights=heights,inner_edge_canonical=poly[:2],bottom=bottom))
hidden=[]
for name in ['P06_NORTH_BASE_W','P06_NORTH_STONE_GABLE_WEST']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_by_R07_continuous_stone_wall';hidden.append(name)
S['stage']='R07 flat stone stairwell walls and inherited lower foyer';S['current_file']=out.name
cd=bpy.data.cameras.new('R07_GROUND_STAIRWELL_REVIEW');cam=bpy.data.objects.new(cd.name,cd);root.objects.link(cam);cam.location=point([557,456],1.65);target=point([673,348],4);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=23;S.camera=cam
cfg=dict(file=out.relative_to(R).as_posix(),base_scene=r['file'],closed_objects=made,hidden_superseded_objects=hidden,wall_definitions=definitions,display_thickness_m=thickness,conditional_corner_roof_z=low,conditional_side_roof_z=band,source_ids=['114','045','051','055','102','104','087','119'],wall_topology_observed=True,wall_dimensions_measured=False,lower_floor_edge_registration_accepted=False,construction_acceptance=False)
bpy.data.texts.new('R07_SOURCE_AND_ASSUMPTIONS').write(json.dumps(cfg,indent=2));S.render.resolution_x=1600;S.render.resolution_y=1250;S.render.resolution_percentage=100;S.cycles.samples=64;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R07_stairwell_ground.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
lower=json.loads((B/'reports/R05_build_report.json').read_text());keep=set(made+lower['closed_objects']+[lower['changed_floor'],'P05_ZONE_LM1_GALLERIES_FOYER','R06_FOYER_CEILING_AND_CURVED_FASCIA']);keep.update(ob.name for ob in S.objects if ob.name.startswith(('P11_GH_LOWER_WEST','P11_GH_BAND_1')))
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
S.camera=bpy.data.objects['R06_FOYER_REVIEW'];S.render.filepath=str(B/'renders/qa/R07_stairwell_lower.png');bpy.ops.render.render(write_still=True)
(B/'reports/R07_build_report.json').write_text(json.dumps(cfg,indent=2),encoding='utf8');(B/'config/stairwell_walls.json').write_text(json.dumps(cfg,indent=2),encoding='utf8');print('R07_SAVED',out)
