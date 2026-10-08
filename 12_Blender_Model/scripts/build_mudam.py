"""Run in Blender 4.2 background. Builds only this standalone v001 scene.
XY follows calibrated source; all Z and construction details remain draft.
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'12_Blender_Model'
CFG=json.loads((B/'config/model_config.json').read_text(encoding='utf-8'))
GATE=json.loads((B/'config/reference_gate.json').read_text(encoding='utf-8'))
if not GATE['production_geometry_enabled']:
 raise RuntimeError(GATE['reason'])
V=json.loads((B/'config/vector_reference.json').read_text(encoding='utf-8'))
C=CFG['calibration'];A=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];Z=CFG['provisional_z']
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['project']='MUDAM';scene['stage']='v001 source-based shell with provisional heights'
scene['georeference']='EPSG:32632; local=(E-293425,N-5499960,Zrelative)'
scene['unverified_dimensions']=CFG['warning']
collections={}
for name in ['00_REFERENCE_LOCKED','01_DATUMS','02_STRUCTURE_LM1','02_STRUCTURE_L00','02_STRUCTURE_LP1','03_ENVELOPE','04_ROOFS','05_INTERIORS','06_CIRCULATION_PROXY','07_SITE_REFERENCE','10_CAMERAS_LIGHTS','90_UNCERTAIN_PROXY']:
 col=bpy.data.collections.new(name);scene.collection.children.link(col);collections[name]=col
def link(obj,col):collections[col].objects.link(obj)
def tag(obj,source='102',level='MULTI',status='draft',detail='U'):
 obj['element_id']=obj.name;obj['source_ids']=source;obj['level_id']=level;obj['status']=status
 obj['confidence_xy']='C calibrated schematic';obj['confidence_z']='U provisional'
 obj['confidence_detail']=detail;obj['confidence_material']='family only; shader provisional'
 return obj
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (A[0][0]*u+A[0][1]*v+A[0][2]-293425,A[1][0]*u+A[1][1]*v+A[1][2]-5499960)
def p3(p,z):return (*xy(p),z)
def mat(name,color,metal=0,rough=.65,glass=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough
 if glass:n.inputs['Transmission Weight'].default_value=.6;n.inputs['IOR'].default_value=1.45;n.inputs['Alpha'].default_value=.7;m.diffuse_color=(*color,.45)
 return m
stone=mat('MAT_STONE_DRAFT',(.66,.58,.45));floor=mat('MAT_STONE_FLOOR_DRAFT',(.74,.70,.61));wood=mat('MAT_WOOD_DRAFT',(.38,.25,.13));metal=mat('MAT_STEEL_DRAFT',(.12,.19,.21),.7,.32);glass=mat('MAT_GLASS_DRAFT',(.32,.58,.66),.15,.2,True);proxy=mat('MAT_UNVERIFIED',(.64,.38,.18));line_mat=mat('MAT_REFERENCE',(.06,.33,.43));base_mat=mat('MAT_DATUM',(.19,.23,.22))
def mesh(name,verts,faces,col,material,source='102',level='MULTI'):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);link(ob,col);ob.data.materials.append(material);tag(ob,source,level);return ob
def prism_world(name,points,z,h,col,material,source='102',level='MULTI'):
 # closed simple polygon, no implicit triangulation fan across concavities
 pts=[Vector((p[0],p[1],0)) for p in points]
 if (pts[0]-pts[-1]).length<1e-5:pts.pop()
 n=len(pts);verts=[(p.x,p.y,z) for p in pts]+[(p.x,p.y,z+h) for p in pts]
 tris=tessellate_polygon([pts]);faces=[]
 def idx(v):return v if isinstance(v,int) else min(range(n),key=lambda i:(pts[i]-v).length_squared)
 for tri in tris:
  ids=[idx(t) for t in tri];faces.extend([list(reversed(ids)),[i+n for i in ids]])
 faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
 return mesh(name,verts,faces,col,material,source,level)
def prism(name,pts,z,h,col,material,source='102',level='MULTI'):return prism_world(name,[xy(p) for p in pts],z,h,col,material,source,level)
def compound(name,loops,z,h,col,material,source,level):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='2D';cu.resolution_u=1;cu.fill_mode='BOTH';cu.extrude=h/2
 for pts in loops:
  sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
  for point,p in zip(sp.points,pts):point.co=(p[0],p[1],0,1)
  sp.use_cyclic_u=True
 ob=bpy.data.objects.new(name,cu);ob.location.z=z+h/2;link(ob,col);ob.data.materials.append(material);tag(ob,source,level,detail='C schematic line widths')
 return ob
def beam_world(name,a,b,r=.07,col='04_ROOFS',material=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
 ob=bpy.data.objects.new(name,cu);link(ob,col);ob.data.materials.append(material or metal);tag(ob,'photographic topology proxy');return ob
def polyline(name,pts,z,col='00_REFERENCE_LOCKED',material=None,r=.04,close=True):
 world=[p3(p,z) for p in pts]
 for j in range(len(world) if close else len(world)-1):beam_world(name+f'_{j:03}',world[j],world[(j+1)%len(world)],r,col,material or line_mat)
def wallseg(name,a,b,z,h,t=.35,col='03_ENVELOPE'):
 a=Vector(xy(a));b=Vector(xy(b));d=(b-a).normalized();n=Vector((-d.y,d.x))*t/2
 return prism_world(name,[a+n,b+n,b-n,a-n],z,h,col,stone)
def opening_wall(name,a,b,z,h,openings,t=.6):
 # openings [(fraction_from,fraction_to,sill,height)]
 va=Vector(a);vb=Vector(b);f=lambda s:tuple(va.lerp(vb,s));previous=0
 for i,(lo,hi,sill,oh) in enumerate(openings):
  if lo>previous:wallseg(name+f'_pier{i}',f(previous),f(lo),z,h,t)
  if sill>0:wallseg(name+f'_sill{i}',f(lo),f(hi),z,sill,t)
  if sill+oh<h:wallseg(name+f'_head{i}',f(lo),f(hi),z+sill+oh,h-sill-oh,t)
  verts=[p3(f(lo),z+sill),p3(f(hi),z+sill),p3(f(hi),z+sill+oh),p3(f(lo),z+sill+oh)]
  ob=mesh(name+f'_glazing_proxy{i}',verts,[(0,1,2,3)],'03_ENVELOPE',glass);ob['assumption_note']='Opening proportions are draft, not measured; replace after photo calibration'
  previous=hi
 if previous<1:wallseg(name+'_end',f(previous),f(1),z,h,t)

# Source vector wall geometry, no raster tracing. Datum heights remain assumptions.
for key,level,z,h in [('walls_L00_A','L00',0,4.5),('walls_L00_B','L00',0,4.5),('walls_LP1','LP1',4.5,4.5)]:
 ob=compound('MUD_'+key,V[key]['loops_xy'],z,h,'02_STRUCTURE_'+level,stone,'2016_pdf_p5_path_'+str(V[key]['pdf_path_index']),level)
 ob['assumption_note']='Extruded source diagram ink. Not verified concrete wall thickness or current construction.'

# Slab footprints: lower level is a simplified public-floor proxy; upper slabs keep hall void.
main=[(289,161),(462,334),(688,334),(862,161),(862,259),(939,337),(862,414),(862,532),(689,709),(617,709),(595,689),(557,689),(537,709),(465,709),(289,532)]
base_main=prism('MUD_LM1_SLAB_PROXY',main,-4.5,.3,'02_STRUCTURE_LM1',floor,'104 approximate footprint','LM1')
base_main['assumption_note']='LM1 outline simplified from envelope; not a fully solved basement layout'
ground=prism('MUD_L00_SLAB',main,-.3,.3,'02_STRUCTURE_L00',floor,'102','L00')
for key,level,z in [('gallery_L00_E','L00',.005),('gallery_L00_W','L00',.005),('gallery_LP1_E','LP1',4.2),('gallery_LP1_W','LP1',4.2)]:
 compound('MUD_'+key,V[key]['loops_xy'],z,.04 if level=='L00' else .3,'02_STRUCTURE_'+level,wood,'2016_pdf_p5_path_'+str(V[key]['pdf_path_index']),level)
prism('MUD_LP1_CROSS_BRIDGE',[(465,555),(689,555),(689,598),(465,598)],4.2,.3,'02_STRUCTURE_LP1',floor,'103','LP1')
prism('MUD_LP1_STUDIO_PROXY',[(465,598),(535,598),(535,709),(465,709)],4.2,.3,'02_STRUCTURE_LP1',floor,'103','LP1')

# A true hole in the ground slab is cut with editable boolean, so it reads in section.
hole=[(638+53*math.cos(math.radians(-135+i*180/24)),383+53*math.sin(math.radians(-135+i*180/24))) for i in range(25)]
cutter=prism('VOID_MAIN_STAIR_EDITABLE',hole,-1,2,'01_DATUMS',proxy)
cutter.hide_render=True;cutter.display_type='WIRE';cutter.hide_set(True)
mod=ground.modifiers.new('Source_schematic_stair_void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter

# Exterior stone envelope, with explicit draft gallery windows.
opening_wall('MUD_EAST_FACADE',(289,352),(289,532),-4.2,13.2,[(.12,.27,4.5,2.8),(.48,.63,4.5,2.8),(.78,.93,4.5,2.8)])
opening_wall('MUD_WEST_FACADE',(862,414),(862,532),-4.2,13.2,[(.28,.43,4.5,2.8),(.68,.83,4.5,2.8)])
opening_wall('MUD_FRONT_EAST',(289,532),(465,709),-4.2,13.2,[])
opening_wall('MUD_FRONT_WEST',(862,532),(689,709),-4.2,13.2,[])
opening_wall('MUD_ENTRANCE',(465,709),(689,709),0,9,[(.32,.68,0,3.2)])
for name,a,b in [('EAST_HIGH',(289,161),(462,334)),('WEST_HIGH',(862,161),(862,259))]:wallseg('MUD_'+name,a,b,0,9,.65)

# Roof surfaces are explicit provisional envelopes, not final structural details.
def quadgrid(name,corners,nu,nv,material=glass):
 a,b,c,d=map(Vector,corners);verts=[]
 for j in range(nv+1):
  v=j/nv
  for i in range(nu+1):u=i/nu;verts.append(tuple(a.lerp(b,u).lerp(d.lerp(c,u),v)))
 faces=[]
 for j in range(nv):
  for i in range(nu):q=j*(nu+1)+i;faces.append((q,q+1,q+nu+2,q+nu+1))
 ob=mesh(name+'_GLASS',verts,faces,'04_ROOFS',material,'026/034/087/093 approximate');ob['assumption_note']='Panel grid and all heights are visual placeholders; not counted or engineered'
 for j in range(nv+1):beam_world(name+f'_ROW_{j}',verts[j*(nu+1)],verts[j*(nu+1)+nu],.055)
 for i in range(nu+1):beam_world(name+f'_COL_{i}',verts[i],verts[nv*(nu+1)+i],.055)
 return ob
center=(575,447)
outer=[(575,334),(688,447),(575,560),(462,447)]
inner=[(575,427),(595,447),(575,467),(555,447)]
for i in range(4):
 j=(i+1)%4
 quadgrid('MAIN_PYRAMID_'+str(i),[p3(outer[i],9),p3(outer[j],9),p3(inner[j],17.5),p3(inner[i],17.5)],8,5)
 quadgrid('MAIN_LANTERN_'+str(i),[p3(inner[i],17.5),p3(inner[j],17.5),p3(inner[j],22),p3(inner[i],22)],2,3)
 apex=p3(center,23);mesh('MAIN_CAP_'+str(i),[p3(inner[i],22),p3(inner[j],22),apex],[(0,1,2)],'04_ROOFS',glass)
 beam_world('MAIN_CAP_EDGE_'+str(i),p3(inner[i],22),apex,.06)
quadgrid('EAST_SALON',[p3((289,161),9),p3((462,334),9),p3((462,438),4.5),p3((289,265),4.5)],10,4)
# Curved west perimeter follows a quadratic sketch; explicitly a geometry hypothesis.
west=[]
for i in range(13):
 t=i/12;west.append(((1-t)**2*688+2*(1-t)*t*746+t*t*862,(1-t)**2*334+2*(1-t)*t*218+t*t*161))
for i in range(12):
 a,b=west[i],west[i+1];c=(b[0],b[1]+99);d=(a[0],a[1]+99)
 quadgrid('WEST_SALON_'+str(i),[p3(a,9),p3(b,9),p3(c,4.5),p3(d,4.5)],1,4)

# Pavilion and link, all linked Z values visibly provisional.
pav=[(42,264),(92,215),(122,215),(171,264),(171,294),(122,344),(92,344),(42,294)]
prism('MUD_PAV_SLAB',pav,-.3,.3,'02_STRUCTURE_L00',floor)
prism('MUD_PAV_LOWER_PROXY',pav,-4.5,.3,'02_STRUCTURE_LM1',floor,'104','LM1')
for i in range(8):
 a,b=pav[i],pav[(i+1)%8]
 if i!=3:wallseg('MUD_PAV_WALL_'+str(i),a,b,0,4.8,.45)
 c=(107+(b[0]-107)*.22,279+(b[1]-279)*.22);d=(107+(a[0]-107)*.22,279+(a[1]-279)*.22)
 quadgrid('PAV_ROOF_'+str(i),[p3(a,4.8),p3(b,4.8),p3(c,7.8),p3(d,7.8)],3,3)
 quadgrid('PAV_LANTERN_'+str(i),[p3(d,7.8),p3(c,7.8),p3(c,10.8),p3(d,10.8)],1,2)
 mesh('PAV_CAP_'+str(i),[p3(d,10.8),p3(c,10.8),p3((107,279),11.5)],[(0,1,2)],'04_ROOFS',glass)
prism('MUD_LINK_SLAB',[(171,264),(289,264),(289,294),(171,294)],-.3,.3,'02_STRUCTURE_L00',floor)
quadgrid('LINK_ROOF',[p3((171,264),3.8),p3((289,264),3.8),p3((289,294),3.8),p3((171,294),3.8)],8,2)
for side in [264,294]:quadgrid('LINK_WALL_'+str(side),[p3((171,side),0),p3((289,side),0),p3((289,side),3.8),p3((171,side),3.8)],8,2)

# Spiral stair proxy follows observed plan center; dimensions are not yet solved.
def spiral(name,center,rout,rin,z0,z1,n=26,start=0,sweep=math.tau*.9):
 cx,cy=xy(center);rail=[]
 for i in range(n):
  a=start+sweep*i/n;b=start+sweep*(i+1)/n;z=z0+(z1-z0)*(i+1)/n
  pts=[(cx+r*math.cos(t),cy+r*math.sin(t)) for r,t in [(rin,a),(rout,a),(rout,b),(rin,b)]]
  ob=prism_world(name+f'_STEP_{i:02}',pts,z-.12,.12,'06_CIRCULATION_PROXY',floor);ob['assumption_note']='Working staircase proxy; riser count and sweep unverified'
  rail.append((cx+rout*math.cos(a),cy+rout*math.sin(a),z+1.05))
 for i in range(len(rail)-1):beam_world(name+f'_RAIL_{i:02}',rail[i],rail[i+1],.025,'06_CIRCULATION_PROXY',metal)
spiral('EAST_SPIRAL_DRAFT',(308,329),1.45,.35,0,4.5,26)
spiral('MAIN_LOWER_DRAFT',(638,383),5.5,3.1,-4.2,0,26,start=.7,sweep=math.pi)

# Reference images and lines, packed and selectable only through Outliner.
for level,z,ident in [('LM1',-4.2,'104'),('L00',0,'102'),('LP1',4.5,'103')]:
 path=B.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/01_Planlar'/f'kat_{{"LM1":"-1","L00":"0","LP1":"1"}}_ortak_olcek.svg' # actual raster below
 raster=B.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/01_Planlar'/('kat_'+{'LM1':'-1','L00':'0','LP1':'1'}[level]+'_4000px.png')
 image=bpy.data.images.load(str(raster));image.pack()
 ob=bpy.data.objects.new('REF_PLAN_'+level,None);ob.empty_display_type='IMAGE';ob.data=image;ob.empty_display_size=1108*C['meters_per_canonical_pixel'];ob.empty_image_depth='BACK';ob.color[3]=.35
 # local image X canonical +x, local image Y canonical -y
 axis=Vector((A[0][0],A[1][0],0)).normalized();angle=math.atan2(axis.y,axis.x)
 ob.rotation_euler.z=angle;ob.location=(*xy((554,480)),z+.02);link(ob,'00_REFERENCE_LOCKED');ob.hide_render=True;ob.hide_set(True);ob.hide_select=True
 ob['source_ids']=ident;ob['registration']='canonical aligned raster, source transform in config'
 for name in ['gallery_L00_E','gallery_L00_W'] if level=='L00' else ['gallery_LP1_E','gallery_LP1_W'] if level=='LP1' else []:
  for j,loop in enumerate(V[name]['loops_xy']):
   for i in range(len(loop)):beam_world('REF_'+level+f'_{j}_{i}',(*loop[i],z+.025),(*loop[(i+1)%len(loop)],z+.025),.025,'00_REFERENCE_LOCKED',line_mat)
collections['00_REFERENCE_LOCKED'].hide_render=True
ways=json.loads((ROOT/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'))
for w in ways:
 if w['id']=='9042342' or (w['tags'].get('building') and any(abs(p[0]-293425)<100 and abs(p[1]-5499960)<100 for p in w['xy'])):
  for i,(a,b) in enumerate(zip(w['xy'],w['xy'][1:])):beam_world('OSM_'+w['id']+'_'+str(i),(a[0]-293425,a[1]-5499960,-4.55),(b[0]-293425,b[1]-5499960,-4.55),.09,'07_SITE_REFERENCE',line_mat)
prism_world('DISPLAY_DATUM_NOT_TERRAIN',[(-95,-90),(95,-90),(95,105),(-95,105)],-4.8,.15,'90_UNCERTAIN_PROXY',base_mat)

# Draft photo cameras: ground-plane hypothesis plus explicitly provisional eye level.
photos=json.loads((ROOT/'10_Olcekli_Plan_ve_Fotograf_Analizi/atlas_data.json').read_text(encoding='utf-8'))['photos']
for p in photos:
 if not p.get('camera_pose_verified') or not p.get('metric_geometry_approved'):continue
 if p['id'] not in ['021','026','041','051','062','067','087','088']:continue
 if not p['target_world']:continue
 cam=bpy.data.cameras.new('PHOTO_'+p['id']);ob=bpy.data.objects.new('PHOTO_'+p['id']+'_UNCALIBRATED',cam);link(ob,'10_CAMERAS_LIGHTS')
 zz=(-4.2 if p['level']=='-1' else 0)+1.65;ob.location=(p['x_m'],-p['y_m'],zz)
 target=Vector((p['target_world'][0],-p['target_world'][1],zz));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.lens=28
 tag(ob,p['id']);ob['assumption_note']='Atlas XY seed only. Camera Z, lens, pitch not calibrated.'

scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.78,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
sun=bpy.data.lights.new('Studio_sun_not_solar_calibration','SUN');sun.energy=2.5;ob=bpy.data.objects.new('Studio_sun',sun);link(ob,'10_CAMERAS_LIGHTS');ob.rotation_euler=(.5,-.4,-.6)
cam=bpy.data.cameras.new('QA_ISO');ob=bpy.data.objects.new('QA_ISO',cam);link(ob,'10_CAMERAS_LIGHTS');ob.location=(125,135,105);target=Vector((0,5,5));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=150;scene.camera=ob
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_distance=125;area.spaces.active.region_3d.view_location=(0,5,4)
   area.spaces.active.region_3d.view_rotation=ob.rotation_euler.to_quaternion();area.spaces.active.clip_end=1000
readme=bpy.data.texts.new('READ_ME_FIRST');readme.write('MUDAM v001\nSource-based initial shell. All Z heights and roof grids are provisional.\nThree floor datums: -4.2 / 0 / +4.5 m (working assumptions).\nSource vector wall thickness represents schematic ink, NOT verified construction.\nRoof / facade openings / spiral stairs are draft geometry, not final details.\nReference images are packed; enable individual REF_PLAN objects in Outliner.\nSee external reports and config. No surveyed/as-built claim.\n')
scene['readme']='READ_ME_FIRST'
report={'stage':'v001 initial shell','blender_version':bpy.app.version_string,'objects':len(bpy.data.objects),'collections':list(collections),'z_values_are_unverified':Z,'vector_paths':{n:v['pdf_path_index'] for n,v in V.items()},'not_completed':['height calibration','upper floor photographic verification','final roof shape and panel count','window positions/dimensions calibration','door families','railing connections','materials','terrain heights','real-time export'],'upper_raster_registration_corrected':True}
(B/'reports/build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(B/'scenes/MUDAM_MASTER_v001.blend'))
scene.render.filepath=str(B/'renders/qa/01_exterior_draft.png');bpy.ops.render.render(write_still=True)
collections['04_ROOFS'].hide_render=True;collections['03_ENVELOPE'].hide_render=True
ob.location=(105,100,135);ob.rotation_euler=(Vector((0,5,0))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(B/'renders/qa/02_cutaway_draft.png');bpy.ops.render.render(write_still=True)
print('MUDAM_BUILD_FINISHED',report['objects'])
