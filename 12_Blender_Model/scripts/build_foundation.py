"""P03 editable plan foundation. Run using Blender --factory-startup --background.
Creates a new versioned file, never overwrites a hand-edited master.
Exploded display spacing is explicitly not a building height.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';A=R/'10_Olcekli_Plan_ve_Fotograf_Analizi'
F=json.loads((B/'config/foundation.json').read_text(encoding='utf-8'))
C=F['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
V=json.loads((B/'config/vector_reference.json').read_text(encoding='utf-8'))
I={p['id']:p for p in json.loads((B/'references/source_manifest.json').read_text(encoding='utf-8'))}
G=json.loads((B/'reports/P03_coordinate_checks.json').read_text(encoding='utf-8'))
assert json.loads((B/'config/reference_gate.json').read_text(encoding='utf-8'))['reference_foundation_enabled']
out=B/'scenes/MUDAM_P03_REFERANS_v002.blend'
if out.exists():raise RuntimeError('Version exists; preserve it and choose a new output version.')
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.name='MUDAM_P03_REFERENCE_FOUNDATION';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
S['project']='MUDAM';S['stage']='P03 editable XY foundation; no approved structural geometry'
S['origin_utm']=json.dumps([293425,5499960]);S['crs']='EPSG:32632';S['xy_contract']='X=E-E0; Y=N-N0; atlas_y=-Y'
S['display_spacing_is_not_elevation']=True;S['measured_floor_levels']=json.dumps(F['measured_levels'])
def col(name,parent=None):
 c=bpy.data.collections.new(name);(parent.children if parent else S.collection.children).link(c);return c
ROOT=col('MUDAM');refs=col('00_REFERENCE_LOCKED',ROOT);sections=col('SECTIONS_UNREGISTERED',refs);photos=col('PHOTO_DETAILS_NOT_CAMERAS',refs)
coords=col('01_DATUMS_AND_AXES',ROOT);diagram=col('90_UNCERTAIN_OR_PROXY',ROOT);qa=col('99_QA',ROOT)
for name in ['02_STRUCTURE','03_ENVELOPE','04_ROOFS','05_INTERIORS','06_CIRCULATION','07_SITE','08_FIXED_FITTINGS','09_TEMPORARY_EXHIBITIONS','91_COLLISION','92_EXPORT_DERIVED']:col(name,ROOT)
floors={};parents={};sheet_objects=[];surface_objects=[]
def tag(ob,source,level='MULTI',zone='REFERENCE',kind='reference',note=''):
 for key,val in dict(element_id=ob.name,element_type=kind,zone_id=zone,level_id=level,source_ids=source,source_date='see source_manifest.json',permanent_or_temporary='reference_only',confidence_xy='C schematic registered to OSM',confidence_z='U unresolved',confidence_detail='U not produced',confidence_material='not assigned',parameter_ids='foundation.json',assumption_note=note or 'Source diagram; not construction geometry',status='reference',visibility_group=level,export_group='DO_NOT_EXPORT_TO_BUILDING',collision_role='none').items():ob[key]=val
 return ob
def link(ob,c,parent=None):c.objects.link(ob);ob.parent=parent;return ob
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.8;return m
ink=mat('REFERENCE_INK',(0.035,.19,.24));red=mat('OSM_REFERENCE',(.7,.18,.09));amber=mat('UNRESOLVED_CIRCULATION',(.8,.42,.09))
floor_mats={l:mat('DIAGRAM_'+l,c) for l,c in [('LM1',(.24,.49,.57)),('L00',(.65,.76,.73)),('LP1',(.42,.64,.65))]}
def curve(name,points,c,parent=None,material=ink,r=.035,closed=True,source='102',level='MULTI'):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=0
 sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for v,p in zip(sp.points,points):v.co=(*p,1)
 sp.use_cyclic_u=closed;ob=link(bpy.data.objects.new(name,d),c,parent);d.materials.append(material);return tag(ob,source,level)
def polygon(name,pts,c,parent,material,source,level):
 # Source floor-zone outline, with a visual edge modifier; this is not a slab specification.
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='2D';d.fill_mode='BOTH';d.resolution_u=1;sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
 for v,p in zip(sp.points,pts):v.co=(p[0],p[1],0,1)
 sp.use_cyclic_u=True;d.extrude=.015;ob=link(bpy.data.objects.new(name,d),c,parent);ob.location.z=.05;d.materials.append(material)
 tag(ob,source,level,kind='schematic_floor_zone',note='0.03 m graphic thickness only. Boundaries are visitor/exhibition diagram regions, not slab/concrete extents.');surface_objects.append(ob);return ob
def packed_image(path):
 im=bpy.data.images.load(str(path),check_existing=True)
 if not im.packed_file:im.pack()
 return im
def image_sheet(name,path,c,parent,z=-.08):
 im=packed_image(path);d=bpy.data.meshes.new(name);verts=[(*xy(p),z) for p in [(0,960),(1108,960),(1108,0),(0,0)]];d.from_pydata(verts,[],[(0,1,2,3)]);d.update();uv=d.uv_layers.new(name='UVMap')
 for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=co
 m=bpy.data.materials.new(name+'_IMAGE');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;em=nt.nodes.new('ShaderNodeEmission');outnode=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],outnode.inputs['Surface'])
 ob=link(bpy.data.objects.new(name,d),c,parent);d.materials.append(m);ob.hide_select=True;ob.hide_render=True;ob.hide_set(True);sheet_objects.append(ob);return ob
def text(name,body,pos,c,parent=None,size=1.1):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.extrude=0;ob=link(bpy.data.objects.new(name,d),c,parent);ob.location=pos;d.materials.append(ink);tag(ob,'project_annotation');return ob
v0=Vector(xy((0,0)));vx=(Vector(xy((1,0)))-v0).normalized();vy=-(Vector(xy((0,1)))-v0).normalized()
rot=Matrix(((vx.x,vy.x,0),(vx.y,vy.y,0),(0,0,1))).to_quaternion()
annotations=[]
for level,num in [('LM1','-1'),('L00','0'),('LP1','1')]:
 c=col('PLAN_'+level,diagram);floors[level]=c
 parent=link(bpy.data.objects.new('DISPLAY_OFFSET_'+level,None),c);parent.location.z=F['display_offsets'][level];parents[level]=parent
 parent['display_only']=True;parent['measured_level']='0 project datum' if level=='L00' else 'UNRESOLVED';parent['reset_display_offset_z']=0
 parent['note']='Exploded diagram spacing; children are local XY traces at z=0. Never use this offset as a building level.'
 ident={'LM1':'104','L00':'102','LP1':'103'}[level]
 ob=image_sheet('SOURCE_PLAN_'+level,A/'01_Planlar'/f'kat_{num}_4000px.png',c,parent);tag(ob,ident,level)
 names=['walls_L00_A','walls_L00_B'] if level=='L00' else ['walls_LP1'] if level=='LP1' else []
 for name in names:
  for j,loop in enumerate(V[name]['loops_xy']):curve('INK_'+name+f'_{j}',[(*p,.11) for p in loop],c,parent,source='PDF2016',level=level)
 for side in ['E','W']:
  name=f'gallery_{level}_{side}'
  if name in V:
   for j,loop in enumerate(V[name]['loops_xy']):polygon('ZONE_'+name+f'_{j}',loop,c,parent,floor_mats[level],'PDF2016',level)
 if level=='L00':
  for zone,pts in F['polygons'].items():polygon('ZONE_L00_'+zone,list(map(xy,pts)),c,parent,floor_mats[level],ident,level)
 if level=='LP1':
  for zone,pts in {'CROSS_BRIDGE':[(465,555),(689,555),(689,598),(465,598)],'STUDIO':[(465,598),(535,598),(535,709),(465,709)]}.items():polygon('ZONE_LP1_'+zone,list(map(xy,pts)),c,parent,floor_mats[level],ident,level)
 if level=='LM1':
  # Direct schematic floor-zone traces in the original 1000 x 866 source.
  s,dx,dy=C['basement_registration']['source_to_canonical']
  pts=[(264,147),(420,303),(623,303)]
  for n in range(1,33):
   t=n/32;pts.append(((1-t)**2*623+2*(1-t)*t*675+t*t*781,(1-t)**2*303+2*(1-t)*t*197+t*t*147))
  pts += [(781,259),(616,424),(590,424),(590,414),(576,414),(576,424),(564,424),(564,414),(555,414),(540,398),(504,398),(488,414),(481,414),(481,424),(468,424),(468,413),(457,413),(457,424),(435,424),(264,258)]
  canonical=[(s*x+dx,s*y+dy) for x,y in pts]
  polygon('ZONE_LM1_GALLERIES_FOYER',list(map(xy,canonical)),c,parent,floor_mats[level],ident,level)
  aud=[(464,440),(582,440),(582,532),(464,532)]
  polygon('ZONE_LM1_AUDITORIUM',[xy((s*x+dx,s*y+dy)) for x,y in aud],c,parent,floor_mats[level],ident,level)
  polygon('ZONE_LM1_PAV',list(map(xy,F['polygons']['PAV'])),c,parent,floor_mats[level],ident,level)
 # Raster perimeter is available locked behind vector traces; no synthetic wall thickness.
 label=text('LABEL_'+level,f'{level} | XY REFERENCE',(*xy((300,820)),.12),c,parent,1.5);label.rotation_quaternion=rot;label.rotation_mode='QUATERNION';annotations.append(label)
 if level!='LM1':
  for sid,center,rad in [('GH_DOWN',(638,383),53),('GH_UP',(500,500),37),('EAST_SPIRAL',(308,329),13)]:
   points=[(*xy((center[0]+rad*math.cos(t*math.tau/64),center[1]+rad*math.sin(t*math.tau/64))),.16) for t in range(64)]
   obj=curve('LOCATOR_'+level+'_'+sid,points,c,parent,amber,.055,source=ident,level=level);obj['assumption_note']='System locator only; radius is a graphical marker, not staircase geometry.'
   label=text('STAIR_LABEL_'+level+'_'+sid,sid,(*xy((center[0]+18,center[1])),.22),c,parent,.8);label.rotation_mode='QUATERNION';label.rotation_quaternion=rot;annotations.append(label)

# OSM and all 11 paired controls stay separate from the museum traces.
ways=json.loads((A/'kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'))
for way in ways:
 if way['id']=='9042342':
  curve('OSM_BUILDING_9042342',[(p[0]-293425,p[1]-5499960,-.35) for p in way['xy']],coords,material=red,r=.09,source='OSM:9042342')
for cp in G['checks']:
 x,y=cp['local_xy'];curve('GCP_'+cp['name'],[(x-.6,y,0),(x+.6,y,0)],coords,r=.06,closed=False,source='calibration')
 curve('GCP_Y_'+cp['name'],[(x,y-.6,0),(x,y+.6,0)],coords,r=.06,closed=False,source='calibration')
 ob=link(bpy.data.objects.new('CONTROL_'+cp['name'],None),coords);ob.location=(x,y,0);ob.empty_display_type='SPHERE';ob.empty_display_size=.4;ob.hide_select=True;ob['numeric_transfer_error_m']=cp['numerical_transfer_error_m'];ob['OSM_residual_m']=cp['source_osm_residual_m']
curve('NORTH_AXIS',[(60,-48,0),(60,-28,0),(59,-31,0),(60,-28,0),(61,-31,0)],coords,closed=False,r=.11)
text('NORTH_LABEL','N / UTM',(58,-26,0),coords,size=1.7)

# Pack actual source images as locked reference empties; not georeferenced cameras.
for n,ident in enumerate(['084','101']+F['photo_ids']):
 image=packed_image(R/I[ident]['path']);ob=link(bpy.data.objects.new('REF_IMAGE_'+ident,None),sections if ident in ['084','101'] else photos)
 ob.empty_display_type='IMAGE';ob.data=image;ob.empty_display_size=25;ob.location=(110+(n%3)*30,-60+(n//3)*30,0);ob.color[3]=1;ob.hide_select=True;ob.hide_render=True;ob.hide_set(True);tag(ob,ident,note='Unregistered reference board. Display width is arbitrary; no metric scale or camera pose inferred.')
refs.hide_render=True

world=bpy.data.worlds.new('QA_NEUTRAL');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8;S.world=world
light=bpy.data.lights.new('QA_SUN','SUN');light.energy=2;lo=link(bpy.data.objects.new('QA_SUN',light),qa);lo.rotation_euler=(.3,-.4,-.3)
cd=bpy.data.cameras.new('QA_CAMERA');cam=link(bpy.data.objects.new('QA_CAMERA',cd),qa);S.camera=cam;cd.type='ORTHO';cd.ortho_scale=135
target=Vector((*xy((470,440)),0));cam.location=target+Vector((110,-140,155));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=160
S.render.engine='BLENDER_EEVEE_NEXT';S.render.resolution_x=1600;S.render.resolution_y=1400;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='Standard'
S.render.film_transparent=False
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_distance=140;sp.region_3d.view_location=(0,0,0);sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion();sp.clip_end=1000;sp.shading.color_type='MATERIAL'
readme=bpy.data.texts.new('READ_ME_FIRST');readme.write('MUDAM / P03 REFERENCE FOUNDATION\n1 unit = 1 metre. X east, Y north.\nAll three local floor drawings are at their own local Z=0.\nDISPLAY_OFFSET_LM1=-12 and LP1=+12 are EXPLODED DIAGRAM SPACING, NOT BUILDING HEIGHTS. Set all DISPLAY_OFFSET Z to 0 to superimpose.\nSource images are packed, hidden and locked. Enable SOURCE_PLAN objects to see underlying official diagrams.\nINK objects are source graphic traces: NEVER treat their width as wall thickness. ZONE objects are schematic floor regions, NOT concrete slabs.\nStair locators identify distinct systems, not their geometry. Photographs and sections are unregistered reference boards.\nNo measured upper/basement levels, no calibrated photo cameras, no construction details.\nSee task board and P03 report.\n')
S['readme']='READ_ME_FIRST'
S.render.filepath=str(B/'renders/qa/P03_00_exploded_reference.png')
saved_object_count=len(bpy.data.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.render.render(write_still=True)
for level in ['LM1','L00','LP1']:
 for l,c in floors.items():c.hide_render=l!=level;parents[l].location.z=0
 for ob in surface_objects:
  ob.hide_render=True
  if ob.parent==parents[level]:
   pts=[(v.co.x,v.co.y,.13) for v in ob.data.splines[0].points]
   curve('QA_EDGE_'+ob.name,pts,floors[level],parents[level],amber,.055,source=ob['source_ids'],level=level)
 for ob in annotations:ob.hide_render=True
 for ob in sheet_objects:ob.hide_render=False
 coords.hide_render=True
 cam.rotation_mode='QUATERNION';cam.rotation_quaternion=rot;cam.location=(*xy((554,480)),150);cd.ortho_scale=135
 S.render.resolution_x=1600;S.render.resolution_y=1386
 S.render.filepath=str(B/'renders/qa'/f'P03_{level}_source_overlay.png');bpy.ops.render.render(write_still=True)
# Geometry-level contract checks, not a claim of surveyed accuracy.
errors=[]
for cp in G['checks']:
 ob=bpy.data.objects['CONTROL_'+cp['name']];errors.append((Vector(cp['local_xy'])-Vector(ob.location[:2])).length)
report=dict(blender_version=bpy.app.version_string,objects=saved_object_count,objects_in_render_session=len(bpy.data.objects),packed_images=len([i for i in bpy.data.images if i.packed_file]),source_count=len(I),max_float_coordinate_error_m=max(errors),unit_scale=S.unit_settings.scale_length,negative_object_scales=[o.name for o in bpy.data.objects if min(o.scale)<0],floor_levels_measured=F['measured_levels'],architectural_height_geometry_generated=False,file=str(out.relative_to(R)),renders=['P03_00_exploded_reference.png']+[f'P03_{l}_source_overlay.png' for l in floors])
assert report['max_float_coordinate_error_m']<1e-4 and not report['negative_object_scales']
(B/'reports/P03_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('P03_FOUNDATION_COMPLETE',report)
