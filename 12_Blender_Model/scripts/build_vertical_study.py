"""P04 conditional height study, including editable pavilion envelope prototype.
No production wall, structural, stair or glazing specification is asserted.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
out=B/'scenes/MUDAM_P04_KOT_ETUDU_v002.blend'
if out.exists():raise RuntimeError('Choose a new version; never overwrite a hand-edited scene.')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_P03_REFERANS_v002.blend'))
S=bpy.context.scene;S.name='MUDAM_P04_CONDITIONAL_HEIGHT_STUDY'
D=json.loads((B/'config/vertical_study.json').read_text(encoding='utf8'));Z={p['id']:p['draft_value'] for p in D['parameters']}
F=json.loads((B/'config/foundation.json').read_text(encoding='utf8'));C=F['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960)
root=bpy.data.collections['90_UNCERTAIN_OR_PROXY'];study=bpy.data.collections.new('P04_HEIGHT_STUDY_NOT_PRODUCTION');root.children.link(study)
envelope=bpy.data.collections.new('PAVILION_ENVELOPE_TEST');study.children.link(envelope)
datum=bpy.data.collections.new('CONDITIONAL_DATUMS');study.children.link(datum)
for level,z in [('LM1',Z['Z_LM1_FINISH']),('L00',0),('LP1',Z['Z_LP1_FINISH'])]:
 p=bpy.data.objects['DISPLAY_OFFSET_'+level];p.location.z=z;p['note']='Conditional section-derived height study; not verified finish elevation.';p['display_only']=False;p['height_status']='conditional_section_estimate'
 bpy.data.objects['LABEL_'+level].hide_render=True;bpy.data.objects['LABEL_'+level].hide_set(True)
 for ob in bpy.data.collections['PLAN_'+level].objects:
  if ob.name.startswith('STAIR_LABEL'):ob.hide_render=True;ob.hide_set(True)
  if ob.name.startswith('ZONE_'):ob.hide_render=True;ob.hide_set(True)
bpy.data.objects['ZONE_LM1_PAV'].location.z=Z['Z_PAV_LM1_FINISH']-Z['Z_LM1_FINISH']+.05
S['stage']='P04 conditional height study; P05 acceptance not complete'
S['display_spacing_is_not_elevation']=False;S['heights_are_conditional_estimates']=True
S['measured_floor_levels']=json.dumps({'LM1':None,'L00':0,'LP1':None});S['draft_floor_levels']=json.dumps({'LM1':Z['Z_LM1_FINISH'],'LP1':Z['Z_LP1_FINISH'],'PAV_LM1':Z['Z_PAV_LM1_FINISH']})
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Roughness'].default_value=.65;return m
clay=mat('STUDY_CLAY_NOT_STONE',(.63,.59,.48));blue=mat('STUDY_BLUE_NOT_PHYSICAL_GLASS',(.15,.35,.40));orange=mat('CONDITIONAL_HEIGHT_MARKERS',(.8,.30,.07))
def tags(ob,kind,params):
 for key,val in dict(element_id=ob.name,element_type=kind,zone_id='PAV',level_id='MULTI',source_ids='101,102,104,089,116',source_date='unknown',confidence_xy='C schematic map fit',confidence_z='D conditional section estimate',confidence_detail='U absent',confidence_material='U study colors only',parameter_ids=','.join(params),assumption_note='Conditional volume study only. No wall thickness, doors, panel count, joints or steel sections. Roof topology and elevations await multi-view matching.',permanent_or_temporary='candidate_permanent',status='study_not_accepted',export_group='DO_NOT_EXPORT_TO_BUILDING',collision_role='none').items():ob[key]=val
 return ob
def mesh(name,verts,faces,material,params,kind='envelope_test'):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();ob=bpy.data.objects.new(name,d);envelope.objects.link(ob);d.materials.append(material);tags(ob,kind,params)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
 return ob
def shell(name,bottom,top,material,params):
 n=len(bottom);return mesh(name,bottom+top,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],material,params)
foot=F['polygons']['PAV'];center=(106.5,279.5)
def ring(z,factor=1):return [(*xy((center[0]+(p[0]-center[0])*factor,center[1]+(p[1]-center[1])*factor)),z) for p in foot]
wall=shell('P04_PAV_WALL_ENVELOPE',ring(Z['Z_PAV_LM1_FINISH']),ring(Z['Z_PAV_WALL_TOP']),clay,['Z_PAV_LM1_FINISH','Z_PAV_WALL_TOP'])
wall['assumption_note']+=' Openings intentionally remain unresolved; surfaces are not solid construction walls.'
factor=40/164
roof=shell('P04_PAV_ROOF_SLOPE',ring(Z['Z_PAV_WALL_TOP']),ring(Z['Z_PAV_SHOULDER'],factor),blue,['Z_PAV_WALL_TOP','Z_PAV_SHOULDER'])
lantern=shell('P04_PAV_LANTERN',ring(Z['Z_PAV_SHOULDER'],factor),ring(Z['Z_PAV_LANTERN_TOP'],factor),blue,['Z_PAV_SHOULDER','Z_PAV_LANTERN_TOP'])
top=ring(Z['Z_PAV_LANTERN_TOP'],factor);apex=(*xy(center),Z['Z_PAV_APEX'])
mesh('P04_PAV_CAP',top+[apex],[(i,(i+1)%8,8) for i in range(8)],blue,['Z_PAV_APEX'])
def line(name,points,material=orange,closed=False,width=.045):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=width;d.bevel_resolution=1;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for v,p in zip(sp.points,points):v.co=(*p,1)
 sp.use_cyclic_u=closed;ob=bpy.data.objects.new(name,d);datum.objects.link(ob);d.materials.append(material);tags(ob,'graphical_datum',[]);return ob
for level in ['LM1','L00','LP1']:
 for ob in list(bpy.data.collections['PLAN_'+level].objects):
  if ob.name.startswith('ZONE_'):
   z=bpy.data.objects['DISPLAY_OFFSET_'+level].location.z+ob.location.z
   pts=[(p.co.x,p.co.y,z) for p in ob.data.splines[0].points]
   edge=line('PLAN_EDGE_'+ob.name,pts,bpy.data.materials['REFERENCE_INK'],True,.025)
   edge['zone_id']=ob['zone_id'];edge['level_id']=level;edge['source_ids']=ob['source_ids'];edge['assumption_note']='Visitor-plan zone contour only; not a concrete slab boundary.'
for key in ['Z_PAV_LM1_FINISH','Z_PAV_FINISH','Z_PAV_WALL_TOP','Z_PAV_SHOULDER','Z_PAV_LANTERN_TOP']:
 z=Z[key];factor_here=factor if key in ['Z_PAV_SHOULDER','Z_PAV_LANTERN_TOP'] else 1.008
 line('DATUM_'+key,ring(z,factor_here),closed=True)
# Vertical profiles of the main roof are section evidence in a separate reference board,
# not placed into an invented Y cut plane inside the building.
boards=bpy.data.collections.new('SECTION_PROFILE_UNREGISTERED_IN_Y');study.children.link(boards)
im=bpy.data.images.load(str(B/'references/P04_section_height_study.png'));im.pack()
ob=bpy.data.objects.new('P04_SECTION_SOURCE_WITH_PICKS',None);boards.objects.link(ob);ob.empty_display_type='IMAGE';ob.data=im;ob.empty_display_size=100;ob.location=(110,0,0);ob.hide_select=True;ob.hide_set(True);ob.hide_render=True
ob['note']='Annotated 2D source. Plan cut line unresolved; arbitrary reference-board placement.'
# Pavilion link is kept as a wire volume until its endpoints and opening details are solved.
link=F['polygons']['LINK'];bottom=[(*xy(p),0) for p in link];toplink=[(*xy(p),Z['Z_LINK_CEILING']) for p in link]
line('LINK_DRAFT_FLOOR',bottom,closed=True);line('LINK_DRAFT_CEILING',toplink,closed=True)
for i in range(4):line('LINK_DRAFT_VERTICAL_'+str(i),[bottom[i],toplink[i]])
readme=bpy.data.texts.new('P04_READ_ME');readme.write('P04 / CONDITIONAL HEIGHT STUDY\nThe three plans use section-derived draft elevations. The pavilion has an editable envelope prototype with separate wall, slope, lantern and cap objects. It has no construction thickness, openings or physical glazing specification.\nPavilion basement and main basement use DIFFERENT provisional elevations.\nOrange curves are graphic datums, not steel members. Link is wireframe only.\nThe section cut line and date remain unresolved. P02 and P04 are still in progress. P05 is not accepted.\nChange config/vertical_study.json and rebuild a NEW version; never overwrite manual edits.\n')
S['readme']='P04_READ_ME';S['conditional_height_config']=json.dumps(D,ensure_ascii=False)
cam=S.camera;cam.rotation_mode='XYZ';target=Vector((*xy((470,430)),2));cam.location=target+Vector((110,-140,155));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=155
S.render.resolution_x=1600;S.render.resolution_y=1200;S.render.filepath=str(B/'renders/qa/P04_00_height_study.png')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=target;sp.region_3d.view_distance=125;sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.render.render(write_still=True)
# Close view is a study view, not a photograph-matched camera.
target=Vector((*xy(center),5));cam.location=target+Vector((30,-38,27));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=34
bpy.data.collections['01_DATUMS_AND_AXES'].hide_render=True
for level in ['LM1','L00','LP1']:bpy.data.collections['PLAN_'+level].hide_render=True
for ob in datum.objects:
 if ob.name.startswith(('LINK_','PLAN_EDGE_')):ob.hide_render=True
S.render.filepath=str(B/'renders/qa/P04_01_pavilion_height_prototype.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),stage='P04 in progress',production_model_complete=False,editable_meshes=[o.name for o in envelope.objects],packed_images=sum(bool(i.packed_file) for i in bpy.data.images),draft_levels=Z,source_cut_line_verified=False,main_stair_riser_chain_verified=False)
(B/'reports/P04_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P04_STUDY_SAVED',report)
