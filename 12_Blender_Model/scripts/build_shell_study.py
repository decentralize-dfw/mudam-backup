"""P05 whole-building schematic shell. All uncertainty remains explicit.
Run Blender --factory-startup --background --python this_file.py.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
out=B/'scenes'/f'MUDAM_P05_KABUK_{version}.blend'
if out.exists():raise RuntimeError('Version exists; use a new version.')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_P04_KOT_ETUDU_v002.blend'))
S=bpy.context.scene;S.name='MUDAM_P05_SCHEMATIC_SHELL'
F=json.loads((B/'config/foundation.json').read_text(encoding='utf8'));C=F['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
D=json.loads((B/'config/vertical_study.json').read_text(encoding='utf8'));Z={p['id']:p['draft_value'] for p in D['parameters']}
V=json.loads((B/'config/vector_reference.json').read_text());H=Z['Z_ROOF_MAIN_BASE'];UP=Z['Z_LP1_FINISH'];LOW=Z['Z_LM1_FINISH']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960)
def pt(p,z):return (*xy(p),z)
root=bpy.data.collections['90_UNCERTAIN_OR_PROXY'];shell=bpy.data.collections.new('P05_SCHEMATIC_BUILDING');root.children.link(shell)
def col(name):
 c=bpy.data.collections.new(name);shell.children.link(c);return c
walls=col('P05_ENVELOPE');floors=col('P05_FLOOR_REGIONS');roofs=col('P05_ROOF_VOLUMES');voids=col('P05_EDITABLE_VOIDS');markers=col('P05_CIRCULATION_PATHS');detail=col('P05_UPPER_GALLERY_ROOF_STUDY')
for name in ['PLAN_LM1','PLAN_L00','PLAN_LP1','CONDITIONAL_DATUMS','01_DATUMS_AND_AXES']:
 bpy.data.collections[name].hide_render=True;bpy.data.collections[name].hide_viewport=True
def mat(name,c,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Roughness'].default_value=.65;n.inputs['Metallic'].default_value=metal;return m
stone=mat('P05_NEUTRAL_ENVELOPE',(.67,.63,.52));glass=mat('P05_ROOF_SURFACE_NOT_PANELIZED',(.18,.37,.42),.12);concrete=mat('P05_CONCRETE_FORM_STUDY',(.67,.7,.7));floor_mat=mat('P05_FLOOR_REFERENCE',(.45,.44,.38));ink=mat('P05_DIAGRAM_EDGE',(.09,.15,.16));upmat=mat('P05_UP_PATH',(.08,.4,.55));downmat=mat('P05_DOWN_PATH',(.8,.26,.07))
objects=[]
def tag(ob,zone,source,level='MULTI',note='',kind='schematic_envelope'):
 values=dict(element_id=ob.name,element_type=kind,zone_id=zone,level_id=level,source_ids=source,source_date='see manifests',confidence_xy='C registered source diagram',confidence_z='D conditional section proportion',confidence_detail='U not detailed',confidence_material='U diagram colors only',status='schematic_not_as_built',permanent_or_temporary='candidate_permanent',parameter_ids='vertical_study.json',assumption_note=note or 'Schematic surface only; no construction thickness or detailed openings.',export_group='P05_STUDY_ONLY',collision_role='none')
 for key,value in values.items():ob[key]=value
 objects.append(ob);return ob
def mesh(name,verts,faces,c,material,zone='MAIN',source='102,103,101',level='MULTI',note=''):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();ob=bpy.data.objects.new(name,d);c.objects.link(ob);d.materials.append(material);tag(ob,zone,source,level,note)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False);return ob
def prism(name,points,z,depth,c,material,zone,source,level='MULTI'):
 n=len(points);v=[(p[0],p[1],z-depth) for p in points]+[(p[0],p[1],z) for p in points]
 # Blender triangulates source regions; no wall width inferred from ink thickness.
 poly=[Vector((p[0],p[1],0)) for p in points];tris=tessellate_polygon([poly]);lookup={tuple(p):i for i,p in enumerate(poly)}
 def index(p):return p if isinstance(p,int) else lookup[tuple(p)]
 fs=[tuple(index(p) for p in reversed(t)) for t in tris]+[tuple(index(p)+n for p in t) for t in tris]
 fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,fs,c,material,zone,source,level,'0.20m floor display thickness only; floor boundary and source role remain schematic.')
def segment(name,a,b,z0,z1,c=walls,material=stone,zone='MAIN',note=''):
 return mesh(name,[pt(a,z0),pt(b,z0),pt(b,z1),pt(a,z1)],[(0,1,2,3)],c,material,zone,note=note)
def surface(name,poly,z,c,material,zone='MAIN',source='102,103,101'):
 return mesh(name,[pt(p,z) for p in poly],[tuple(range(len(poly)))],c,material,zone,source)
def curve(name,points,c,material,zone,r=.055,closed=False):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=1;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for v,p in zip(sp.points,points):v.co=(*p,1)
 sp.use_cyclic_u=closed;ob=bpy.data.objects.new(name,d);c.objects.link(ob);d.materials.append(material);tag(ob,zone,'102,103,104',note='Graphical guide; not a measured member or stair.',kind='diagram_guide');return ob
# Main external frontage follows the 2016 outline, but openings remain separately unresolved.
front=[(289.5,347.3),(289.5,534.7),(478.7,723.3),(488.9,712.8),(538,712.8),(562.6,688.1),(589,688.1),(613.9,712.8),(665.1,712.8),(674.7,721.6),(862.5,534.7),(862.5,416)]
for i,(a,b) in enumerate(zip(front,front[1:])):
 opening=i in [4,5,6];segment('P05_FRONT_'+str(i),a,b,H*.60 if opening else LOW,H,note='Entrance recess retained; portal head ratio 0.60 is a visual placeholder, not measured.' if opening else 'External source contour. Gallery window voids await P08; do not detail this face.')
# Roof-backed opaque walls separating galleries from the glazed halls.
east=[(289.5,347.3),(349,347.3),(462.4,460.7),(462.4,555)]
west=[(685.9,555),(685.9,468.7),(798,356),(862.5,356),(862.5,416)]
for label,path in [('EAST',east),('WEST',west)]:
 for i,(a,b) in enumerate(zip(path,path[1:])):segment('P05_GALLERY_HALL_'+label+str(i),a,b,0,H,zone=label,note='Room boundary approximation from source diagram; opening locations not finalized.')
# Side-hall high edges are at the galleries; exterior eaves are lower.
low_eave=UP+.8
segment('P05_EAST_HIGH',(289.5,266.5),(462.4,441.1),0,H,zone='GARDEN')
mesh('P05_EAST_END',[pt((289.5,161.5),0),pt((289.5,266.5),0),pt((289.5,266.5),H),pt((289.5,161.5),low_eave)],[(0,1,2,3)],walls,stone,'GARDEN')
mesh('P05_WEST_END',[pt((862.5,162.9),0),pt((862.5,262.6),0),pt((862.5,262.6),H),pt((862.5,162.9),low_eave)],[(0,1,2,3)],walls,stone,'CAFE')
# Source floor regions: official diagrams, no full plate filling the Grand Hall on +1.
for lev,z in [('L00',0),('LP1',UP)]:
 for side in ['E','W']:
  for i,loop in enumerate(V['gallery_'+lev+'_'+side]['loops_xy']):prism('P05_FLOOR_'+lev+'_'+side+str(i),loop,z,.2,floors,floor_mat,side,'PDF2016',lev)
for zone in ['GH','ENT','EAST_GARDEN','WEST_CAFE']:
 ob=prism('P05_FLOOR_L00_'+zone,[xy(p) for p in F['polygons'][zone]],0,.2,floors,floor_mat,zone,'102','L00')
 if zone=='GH':ground=ob
for zone,poly in {'BRIDGE':[(465,555),(689,555),(689,598),(465,598)],'STUDIO':[(465,598),(535,598),(535,709),(465,709)]}.items():prism('P05_FLOOR_LP1_'+zone,list(map(xy,poly)),UP,.2,floors,floor_mat,zone,'103','LP1')
for src in [o for o in bpy.data.collections['PLAN_LM1'].objects if o.name.startswith('ZONE_')]:
 pts=[(p.co.x,p.co.y) for p in src.data.splines[0].points];z=Z['Z_PAV_LM1_FINISH'] if src.name.endswith('_PAV') else LOW
 prism('P05_'+src.name,pts,z,.2,floors,floor_mat,'BASEMENT','104','LM1')
# True downward stair opening in ground region, with a retained editable cutter.
center=(636,386);radius=49
hole=[xy((center[0]+radius*math.cos(math.radians(-135+i*180/64)),center[1]+radius*math.sin(math.radians(-135+i*180/64)))) for i in range(65)]
cutter=prism('P05_GH_DOWN_VOID',hole,1,2,voids,downmat,'GH_DOWN','102','L00');cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE';cutter['assumption_note']='Semicircular opening fitted approximately to 102; not the upper stair.'
mod=ground.modifiers.new('GH_down_void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
# Gallery roof bases and curved north-facing clerestory form tests.
def clip(poly,y,keep_above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>=y-1e-8 if keep_above else a[1]<=y+1e-8;ib=b[1]>=y-1e-8 if keep_above else b[1]<=y+1e-8
  if ia:out.append(a)
  if ia!=ib:
   t=(y-a[1])/(b[1]-a[1]);out.append((a[0]+t*(b[0]-a[0]),y))
 return out
bay_count=5
for side in ['E','W']:
 poly=[tuple(p) for p in V['gallery_LP1_'+side]['loops_xy'][0]];ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly);pitch=(ymax-ymin)/bay_count
 base=UP+6.2;rise=max(.8,H-base-.2)
 for bay in range(bay_count):
  ya=ymin+bay*pitch
  for j in range(16):
   y0=ya+j*pitch/16;y1=ya+(j+1)*pitch/16;region=clip(clip(poly,y0,True),y1,False)
   if len(region)<3:continue
   verts=[(x,y,base+rise*(math.sin((y-ya)/pitch*math.pi/2))) for x,y in region]
   ob=mesh(f'P05_SHED_{side}_{bay}_{j}',verts,[tuple(range(len(verts)))],detail,concrete,side,'UG02,UG03,UC01,UC02,116','LP1','Curved clerestory topology supported by project architect. Five bays and dimensions are a schematic hypothesis; not counted/verified.')
  edge=clip(poly,ya+pitch,False);cross=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   if min(a[1],b[1])<=ya+pitch<=max(a[1],b[1]) and abs(a[1]-b[1])>1e-9:
    t=(ya+pitch-a[1])/(b[1]-a[1]);cross.append(a[0]+t*(b[0]-a[0]))
  if len(cross)>=2:
   x0,x1=min(cross),max(cross);yy=ya+pitch
   if x1-x0>.01:mesh(f'P05_CLERESTORY_{side}_{bay}',[(x0,yy,base),(x1,yy,base),(x1,yy,base+rise),(x0,yy,base+rise)],[(0,1,2,3)],detail,glass,side,'UG02,UG03,UC01,116','LP1','North-facing glazing plane; dimensions and bay count remain schematic.')
# Central entrance/bridge roof stays below main lantern and leaves the atrium clear.
deck_poly=[(289.5,347.3),(349,347.3),(462.4,460.7),(462.4,336.1),(685.9,336.1),(685.9,468.7),(798,356),(862.5,356),(862.5,534.7),(674.7,721.6),(665.1,712.8),(613.9,712.8),(589,688.1),(562.6,688.1),(538,712.8),(488.9,712.8),(478.7,723.3),(289.5,534.7)]
deck=prism('P05_MAIN_ROOF_DECK',list(map(xy,deck_poly)),H-1.2,.2,roofs,stone,'MAIN','102,103,116')
for side in ['E','W']:
 cut=prism('P05_GALLERY_ROOF_VOID_'+side,V['gallery_LP1_'+side]['loops_xy'][0],H+1,5,voids,glass,side,'PDF2016','LP1');cut.hide_set(True);cut.hide_render=True
 mod=deck.modifiers.new('Gallery_roof_opening_'+side,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
# Main roof: clipped diamond envelope, editable ring vertices; no invented panel grid.
outer=[(565,334),(585,334),(688,437),(688,457),(585,560),(565,560),(462,457),(462,437)]
cut=prism('P05_ATRIUM_ROOF_VOID',list(map(xy,outer)),H+1,5,voids,glass,'GH','102');cut.hide_set(True);cut.hide_render=True
mod=deck.modifiers.new('Atrium_opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
center=(575,447);inner=[(center[0]+(p[0]-center[0])*.18,center[1]+(p[1]-center[1])*.18) for p in outer]
shoulder=(436-170)*D['section_m_per_px'];lantern_top=(436-131)*D['section_m_per_px'];apex=Z['Z_ROOF_MAIN_APEX']
for i in range(8):
 j=(i+1)%8
 segment('P05_MAIN_ATRIUM_BASE_'+str(i),outer[i],outer[j],0,H,roofs,glass,'GRAND_HALL',note='Provisional enclosure below roof. Stone/glass boundaries, lower inclined facets and portals remain unresolved; camera fitting required.')
 mesh('P05_MAIN_ROOF_'+str(i),[pt(outer[i],H),pt(outer[j],H),pt(inner[j],shoulder),pt(inner[i],shoulder)],[(0,1,2,3)],roofs,glass,'GRAND_HALL','101,084,116,119',note='Single clipped-diamond candidate envelope; asymmetric lower facets and vertical glass slot still require camera matching.')
 mesh('P05_MAIN_LANTERN_'+str(i),[pt(inner[i],shoulder),pt(inner[j],shoulder),pt(inner[j],lantern_top),pt(inner[i],lantern_top)],[(0,1,2,3)],roofs,glass,'GRAND_HALL')
 mesh('P05_MAIN_CAP_'+str(i),[pt(inner[i],lantern_top),pt(inner[j],lantern_top),pt(center,apex)],[(0,1,2)],roofs,glass,'GRAND_HALL')
for ring,z in [(outer,H),(inner,shoulder),(inner,lantern_top)]:curve('P05_MAIN_RING',list(map(lambda p:pt(p,z),ring)),roofs,ink,'GRAND_HALL',.055,True)
# East planar roof and west curved roof remain distinct; no mirrored curve.
east_hi=[(289.5,266.5),(462.4,441.1)];east_lo=[(289.5,161.5),(462.4,336.1)]
mesh('P05_EAST_GLAZED_ROOF',[pt(east_hi[0],H),pt(east_hi[1],H),pt(east_lo[1],low_eave),pt(east_lo[0],low_eave)],[(0,1,2,3)],roofs,glass,'GARDEN','034,041,102,116')
segment('P05_EAST_LOW_GLAZING',east_lo[0],east_lo[1],0,low_eave,roofs,glass,'GARDEN')
west_curve=[(p[0],p[1]) for p in F['polygons']['WEST_CAFE'][:-2]]
for i,(a,b) in enumerate(zip(west_curve,west_curve[1:])):
 da=(a[0],a[1]+99);db=(b[0],b[1]+99)
 mesh('P05_WEST_CURVED_ROOF_'+str(i),[pt(a,low_eave),pt(b,low_eave),pt(db,H),pt(da,H)],[(0,1,2,3)],roofs,glass,'CAFE','093,102,119',note='Quadratic source contour; elevation mapping is provisional, independent of east roof.')
 segment('P05_WEST_LOW_GLAZING_'+str(i),a,b,0,low_eave,roofs,glass,'CAFE')
# Pavilion link faces, keeping its portal in the pavilion wall editable.
link=F['polygons']['LINK'];surface('P05_LINK_FLOOR',link,0,floors,floor_mat,'LINK');surface('P05_LINK_ROOF',link,Z['Z_LINK_CEILING'],roofs,glass,'LINK')
for i in [0,2]:segment('P05_LINK_SIDE_'+str(i),link[i],link[(i+1)%4],0,Z['Z_LINK_CEILING'],roofs,glass,'LINK')
pavwall=bpy.data.objects['P04_PAV_WALL_ENVELOPE'];d=pavwall.data
# Omit the east-facing bridge bay wall below its roof; retain a lintel surface above.
faces=[tuple(p.vertices) for p in d.polygons if set(p.vertices)!=set([3,4,12,11])]
oldverts=[tuple(v.co) for v in d.vertices];d.clear_geometry();d.from_pydata(oldverts,[],faces);d.update()
segment('P05_PAV_LINK_LINTEL',link[0],link[3],Z['Z_LINK_CEILING'],Z['Z_PAV_WALL_TOP'],walls,stone,'PAV')
# Circulation connection paths carry endpoints only; no assumed riser count is built.
curve('P05_PATH_GH_UP',[pt((548,555),0),pt((500,510),.6),pt((473,483),UP)],markers,upmat,'GH_UP',.12)
arc=[pt((636+36*math.cos(math.radians(45-t*180)),386+36*math.sin(math.radians(45-t*180))),LOW*t) for t in [i/48 for i in range(49)]]
curve('P05_PATH_GH_DOWN',arc,markers,downmat,'GH_DOWN',.12)
# Add new published roof evidence as packed, hidden reference boards.
manifest=json.loads((B/'references/upper_gallery_2007/manifest.json').read_text(encoding='utf8'))
for n,p in enumerate(manifest):
 im=bpy.data.images.load(str(R/p['path']));im.pack();ob=bpy.data.objects.new('REF_'+p['id'],None);bpy.data.collections['00_REFERENCE_LOCKED'].objects.link(ob);ob.empty_display_type='IMAGE';ob.data=im;ob.location=(130,n*20,0);ob.empty_display_size=18;ob.hide_set(True);ob.hide_render=True;ob.hide_select=True;ob['source_ids']=p['id'];ob['credit']=p['credit']
# Design-review camera presets, intentionally not photograph calibrated.
qa=bpy.data.collections['99_QA'];cameras={}
for name,cp,target,scale in [('ENTRY',(-150,1120,75),(510,440,7),142),('GLAZED',(700,-600,75),(550,360,8),145),('TOP',(490,440,180),(490,440,0),175)]:
 cd=bpy.data.cameras.new('P05_CAMERA_'+name);cam=bpy.data.objects.new('P05_CAMERA_'+name,cd);qa.objects.link(cam);cd.type='ORTHO';cd.ortho_scale=scale;cam.location=pt(cp[:2],cp[2]);tp=Vector(pt(target[:2],target[2]));cam.rotation_euler=(tp-cam.location).to_track_quat('-Z','Y').to_euler();cameras[name]=cam
S.camera=cameras['ENTRY'];S.render.resolution_x=1800;S.render.resolution_y=1350;S.render.resolution_percentage=100
S['stage']='P05 whole-building schematic shell; detailed production and camera validation pending';S['readme']='P05_READ_ME';S['current_file']=out.name
readme=bpy.data.texts.new('P05_READ_ME');readme.write('P05 SCHEMATIC SHELL\nMetre coordinates, source-registered floor regions and editable ground stair void.\nWhole building now has envelope/roof masses, central lantern, distinct east/west glazed halls, pavilion and link. Upper gallery curved roof form is based on architect evidence; five bays are NOT a verified count.\nNo construction wall thickness, detailed windows, steel grid or stair risers. Colored curves show circulation hypotheses only.\nAll P05 objects remain in 90_UNCERTAIN_OR_PROXY. P02/P04 residuals are documented. This is the model for upcoming P06 silhouette/camera testing, not a survey-grade building.\n')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.region_3d.view_location=pt((510,440),7);sp.region_3d.view_distance=125;sp.region_3d.view_rotation=S.camera.rotation_euler.to_quaternion();sp.shading.color_type='MATERIAL'
S.render.filepath=str(B/'renders/qa/P05_01_entry.png');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for name,cam in cameras.items():
 S.camera=cam;S.render.filepath=str(B/'renders/qa'/('P05_'+{'ENTRY':'01_entry','GLAZED':'02_glazed','TOP':'03_top'}[name]+'.png'));bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),stage='schematic',objects_added=len(objects),mesh_count=sum(o.type=='MESH' for o in objects),floor_levels={'L00':0,'LP1':UP,'LM1':LOW},main_roof_apex=apex,upper_gallery_roof_bays_are_unverified=bay_count,verified_photo_cameras=0,construction_details_complete=False)
(B/'reports/P05_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P05_SAVED',report)
