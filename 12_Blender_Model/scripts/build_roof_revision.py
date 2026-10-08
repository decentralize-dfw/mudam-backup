"""P06 conditional roof revision and photograph camera. Run with Blender 4.2."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2]; B=R/'12_Blender_Model'
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
out=B/'scenes'/f'MUDAM_P06_CATI_KONTROL_{version}.blend'
if out.exists():raise RuntimeError('Output exists; use a new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_P05_KABUK_v002.blend'))
S=bpy.context.scene;F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
D=json.loads((B/'config/roof_revision.json').read_text());fit=json.loads((B/'reports/P06_camera_fit_119.json').read_text());camfit=fit['candidates']['revised']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960)
def pt(p,z):return (*xy(p),z)
root=bpy.data.collections['90_UNCERTAIN_OR_PROXY'];c=bpy.data.collections.new('P06_ROOF_REVISION_CONDITIONAL');root.children.link(c)
old=[]
for ob in bpy.data.objects:
 if ob.name.startswith(('P05_MAIN_ROOF_','P05_MAIN_LANTERN_','P05_MAIN_CAP_','P05_MAIN_RING')) and ob.name!='P05_MAIN_ROOF_DECK':
  ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_by_P06_roof_candidate';old.append(ob.name)
glass=bpy.data.materials['P05_ROOF_SURFACE_NOT_PANELIZED'];objects=[]
def mesh(name,vs,fs):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 # The registered plan transform reflects image Y. Ensure exterior normals.
 centre=Vector(pt((575,447),0))
 for poly in me.polygons:
  if 'ROOF_FACE' in name or 'MAIN_CAP' in name:flip=poly.normal.z<0
  else:
   radial=poly.center-centre;radial.z=0;flip=poly.normal.dot(radial)<0
  if flip:poly.flip()
 me.update();ob=bpy.data.objects.new(name,me);c.objects.link(ob);me.materials.append(glass)
 for key,value in dict(element_id=name,element_type='roof_surface_study',zone_id='GH',source_ids='102,101,119,116,026',status='conditional_not_accepted',confidence_xy='C plan extent, D strip and lantern footprint',confidence_z='D section proportion',confidence_detail='U',assumption_note='See roof_revision.json and P06_CAMERA_ROOF_REVIEW.md. No member size or panel grid.',export_group='P06_STUDY_ONLY',collision_role='none').items():ob[key]=value
 objects.append(ob);return ob
o=D['outer_canonical'];inn=D['inner_canonical'];a=D['eave_z'];b=D['shoulder_z'];top=D['lantern_top_z'];apex=D['apex_z']
for i in range(8):
 j=(i+1)%8
 mesh('P06_MAIN_ROOF_FACE_'+str(i),[pt(o[i],a[i]),pt(o[j],a[j]),pt(inn[j],b[j]),pt(inn[i],b[i])],[(0,1,2,3)])
 mesh('P06_MAIN_LANTERN_'+str(i),[pt(inn[i],b[i]),pt(inn[j],b[j]),pt(inn[j],top),pt(inn[i],top)],[(0,1,2,3)])
 mesh('P06_MAIN_CAP_'+str(i),[pt(inn[i],top),pt(inn[j],top),pt((575,447),apex)],[(0,1,2)])
# Bridge old low enclosure to higher eave on the entrance side, visibly provisional.
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
for i in [3,4,5]:
 j=(i+1)%8
 ob=mesh('P06_HIGH_EAVE_UPSTAND_'+str(i),[pt(o[i],min(a)),pt(o[j],min(a)),pt(o[j],a[j]),pt(o[i],a[i])],[(0,1,2,3)])
 if i!=4:ob.data.materials.clear();ob.data.materials.append(stone)
 ob['assumption_note']='116 shows raised opaque atrium walls with central glass strip. Lower continuity and openings remain unresolved.'
# Local fit coordinates: +X = minus canonical X, +Y = canonical Y, +Z up.
origin=Vector(pt((575,447),0));xp=(Vector(pt((574,447),0))-origin).normalized();yp=(Vector(pt((575,448),0))-origin).normalized()
T=Matrix((xp,yp,Vector((0,0,1)))).transposed()
p=camfit['camera_parameters'];rows=[Vector(v) for v in camfit['camera_basis_rows']]
cd=bpy.data.cameras.new('P06_PHOTO_119_CONDITIONAL');cam=bpy.data.objects.new(cd.name,cd);bpy.data.collections['99_QA'].objects.link(cam)
cam.location=origin+T@Vector(p[:3]);cam.rotation_euler=Matrix((T@rows[0],T@rows[1],-(T@rows[2]))).transposed().to_euler()
cd.type='PERSP';cd.sensor_fit='HORIZONTAL';cd.sensor_width=36;cd.lens=camfit['focal_px']*36/1600;cd.clip_end=3000
cam['status']='conditional_diagnostic_not_metric_pose';cam['source_ids']='119';cam['fit_rmse_px']=camfit['fit_rmse_px'];cam['holdout_rmse_px']=camfit['holdout_rmse_px'];cam['assumption_note']='Fixed principal point and unknown crop/lens. Do not transfer this camera to atlas as verified.'
im=bpy.data.images.load(str(R/fit['source_path']));im.pack();cd.show_background_images=True;bg=cd.background_images.new();bg.image=im;bg.alpha=.5;bg.display_depth='BACK';bg.frame_method='FIT'
S.name='MUDAM_P06_ROOF_CAMERA_STUDY';S['stage']='P06 partial: roof topology and camera 119 diagnostic; no accepted metric cameras';S['current_file']=out.name
txt=bpy.data.texts.new('P06_READ_ME');txt.write('P06 CONDITIONAL ROOF REVISION\nTwo eave/shoulder levels from section 101, constrained against photo 119.\nFixed model geometry, 7 fitted camera parameters. Withheld shoulder landmarks are on the SAME photo, not independent views.\n116/102/026 visually inspected; 116 not metrically fitted. Old roof surfaces hidden, preserved in P05 file.\nFloor envelope and lower atrium still schematic. No steel panels, physical glass, wall thickness or construction details are validated.\nRead reports/P06_CAMERA_ROOF_REVIEW.md.\n')
S.camera=cam;S.render.resolution_x=1600;S.render.resolution_y=754;S.render.resolution_percentage=100
# Validate Blender camera projection against numerical solver before any render/save.
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update();errs=[]
for point in camfit['points']:
 world=origin+T@Vector(point['model_local_xyz']);v=world_to_camera_view(S,cam,world);pixel=Vector((v.x*1600,(1-v.y)*754));errs.append((pixel-Vector(point['projected_px'])).length)
assert max(errs)<.02,errs
S.render.film_transparent=True
visible={ob.name:ob.hide_render for ob in S.objects}
for ob in S.objects:
 if ob.type not in ['CAMERA','LIGHT'] and ob not in objects:ob.hide_render=True
S.render.filepath=str(B/'renders/qa/P06_119_roof_transparent.png');bpy.ops.render.render(write_still=True)
for name,value in visible.items():bpy.data.objects[name].hide_render=value
S.render.film_transparent=False
S.camera=bpy.data.objects['P05_CAMERA_ENTRY'];S.render.resolution_x=1800;S.render.resolution_y=1350;S.render.filepath=str(B/'renders/qa/P06_01_entry.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.render.render(write_still=True)
S.camera=bpy.data.objects['P05_CAMERA_GLAZED'];S.render.filepath=str(B/'renders/qa/P06_02_glazed.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),objects_added=len(objects),superseded_objects=old,blender_projection_max_error_px=max(errs),verified_metric_cameras=0,conditional_cameras=1,photo119=camfit)
(B/'reports/P06_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P06_SAVED',out,'projection_max_error_px',max(errs))
