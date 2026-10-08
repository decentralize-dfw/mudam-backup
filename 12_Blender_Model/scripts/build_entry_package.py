"""P07/P08 regional pilot, canopy/entry and lower roof corrections. Blender 4.2."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P07_GIRIS_{version}.blend'
if out.exists():raise RuntimeError('Version exists; use a new version.')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_P06_CATI_KONTROL_v002.blend'))
S=bpy.context.scene;P=json.loads((B/'config/entry_package.json').read_text());E=P['entry'];L=P['lower_roof'];Q=json.loads((B/'config/roof_revision.json').read_text());F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];scale=C['meters_per_canonical_pixel']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960))
def pt(p,z):return (*xy(p),z)
root=bpy.data.collections['90_UNCERTAIN_OR_PROXY'];package=bpy.data.collections.new('P07_P08_REGIONAL_PILOT');root.children.link(package)
def col(name):
 c=bpy.data.collections.new(name);package.children.link(c);return c
canopy=col('P07_ENTRY_CANOPY');facade=col('P07_ENTRY_ENVELOPE');openings=col('P08_ENTRY_OPENINGS');lower=col('P06_LOWER_ROOF_REVISION');reading=col('P06_READING_LANTERN')
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];roofglass=bpy.data.materials['P05_ROOF_SURFACE_NOT_PANELIZED'];floor_mat=bpy.data.materials['P05_FLOOR_REFERENCE']
def material(name,color,metal=0,transmission=0,roughness=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=roughness;n.inputs['Transmission Weight'].default_value=transmission;return m
metal=material('P08_FRAME_PREVIEW_NOT_SPECIFICATION',(.19,.22,.21),.65,roughness=.3);glass=material('P08_GLAZING_PREVIEW_NOT_SPECIFICATION',(.23,.4,.42),transmission=.6,roughness=.12)
objects=[];hidden=[];solid_names=[];opening_checks=[]
def hide(ob):
 ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_in_P07_regional_pilot';hidden.append(ob.name)
def mesh(name,verts,faces,c,mat,source='102,008,011,013,116',closed=False):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
 if closed:
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();solid_names.append(name)
 else:
  for poly in d.polygons:
   if poly.normal.z<0:poly.flip()
  d.update()
 ob=bpy.data.objects.new(name,d);c.objects.link(ob);d.materials.append(mat)
 for key,value in dict(element_id=name,element_type='regional_reconstruction',zone_id='ENTRY' if c in [canopy,facade,openings] else 'GH',level_id='MULTI',source_ids=source,status='conditional_parametric_study',confidence_xy='C source registration',confidence_z='D conditional',confidence_detail='D preview sizes; U unresolved joints',parameter_ids='entry_package.json',assumption_note='Source-specific assumptions in entry_package.json. Solid envelope is not a structural concrete specification.',export_group='P07_P08_STUDY_ONLY',collision_role='preview').items():ob[key]=value
 objects.append(ob);return ob
def prism(name,points,z0,z1,c,mat,source='102,008,011,116'):
 points=[tuple(p) for p in points];n=len(points);poly=[Vector((*p,0)) for p in points];lookup={tuple(p):i for i,p in enumerate(poly)};tris=tessellate_polygon([poly])
 def idx(x):return x if isinstance(x,int) else lookup[tuple(x)]
 faces=[tuple(idx(p) for p in reversed(t)) for t in tris]+[tuple(idx(p)+n for p in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,[(x,y,z0) for x,y in points]+[(x,y,z1) for x,y in points],faces,c,mat,source,True)
def wall(name,a,b,z0,z1,depth,c,mat,source='102,008,013'):
 a,b=Vector(a),Vector(b);v=(b-a).normalized();normal=Vector((-v.y,v.x))*depth/2
 return prism(name,[a-normal,b-normal,b+normal,a+normal],z0,z1,c,mat,source)
def surface(name,poly,z,c,mat,source):return mesh(name,[pt(p,z) for p in poly],[tuple(range(len(poly)))],c,mat,source)
# 1. Canopy outline is distinct from recessed ground enclosure.
tri=list(map(xy,E['roof_triangle']));alcove=list(map(xy,E['chain']+[E['roof_triangle'][1]]))
prism('P07_CANOPY_SLAB_ENVELOPE',alcove,E['soffit_z'],E['roof_top_z'],canopy,stone)
prism('P07_CANOPY_PAVING_DISPLAY',alcove,-.2,0,canopy,floor_mat)
for i,j in [(0,1),(1,2)]:wall(f'P07_CANOPY_FASCIA_{i}',tri[i],tri[j],E['soffit_z'],E['parapet_top_z'],.30,canopy,stone)
tip=tri[1];v0=(tri[0]-tip).normalized();v1=(tri[2]-tip).normalized();side=E['column_side_m']
prism('P07_CORNER_SUPPORT_ENVELOPE',[tip,tip+v0*side,tip+(v0+v1)*side,tip+v1*side],0,E['soffit_z'],canopy,stone)
# 2. Recessed entry wall replaced by opening-aware closed volumes.
for i in range(2,9):hide(bpy.data.objects['P05_FRONT_'+str(i)])
chain=list(map(xy,E['chain']));head=E['glass_head_z'];H=E['parapet_top_z'];depth=E['wall_depth_m'];pw=E['pier_width_m'];fw=E['frame_width_m']
schedule=json.loads((B/'config/entry_openings.json').read_text())
for i in [0,1,5,6]:wall(f'P07_ENTRY_RETURN_{i}',chain[i],chain[i+1],0,H,depth,facade,stone)
for bay,i in enumerate([2,3,4],1):
 a,b=chain[i],chain[i+1];v=(b-a).normalized();length=(b-a).length;l=a+v*pw/2;r=b-v*pw/2;mid=(l+r)/2;clear=(r-l).length
 wall(f'P07_ENTRY_{bay}_LEFT_PIER',a,a+v*pw/2,0,H,depth,facade,stone)
 wall(f'P07_ENTRY_{bay}_RIGHT_PIER',b-v*pw/2,b,0,H,depth,facade,stone)
 wall(f'P07_ENTRY_{bay}_HEAD',l,r,head,H,depth,facade,stone)
 wall(f'P07_ENTRY_{bay}_TRANSOM',l,r,E['transom_bottom_z'],E['transom_bottom_z']+E['transom_height_m'],depth,facade,stone)
 for lev,z0,z1 in [('L00',E['glass_bottom_z'],E['transom_bottom_z']),('LP1',E['transom_bottom_z']+E['transom_height_m'],head)]:
  ident=f'ENT-{bay:02}-{lev}'
  # Perimeter frames remain separate from masonry and glass.
  for label,u,w,bot,top in [('LEFT',l,l+v*fw,z0,z1),('RIGHT',r-v*fw,r,z0,z1),('SILL',l,r,z0,z0+fw),('HEAD',l,r,z1-fw,z1)]:
   ob=wall(ident+'_FRAME_'+label,u,w,bot,top,E['frame_depth_m'],openings,metal);ob['opening_id']=ident
  ll,rr=l+v*fw,r-v*fw
  if bay==2 and lev=='L00':
   dw=E['vestibule_width_m'];door_l=mid-v*dw/2;door_r=mid+v*dw/2;dh=E['vestibule_height_m']
   for label,u,w,bot,top in [('LEFT_SIDE',ll,door_l,z0+fw,z1-fw),('RIGHT_SIDE',door_r,rr,z0+fw,z1-fw),('OVER_DOOR',door_l,door_r,dh,z1-fw)]:
    ob=wall(ident+'_GLASS_'+label,u,w,bot,top,E['glass_thickness_m'],openings,glass);ob['opening_id']=ident
   outward=(xy([575,816])-xy([575,688])).normalized();front_l=door_l+outward*E['vestibule_depth_m'];front_r=door_r+outward*E['vestibule_depth_m']
   for label,u,w in [('LEFT',door_l,front_l),('RIGHT',door_r,front_r)]:
    ob=wall('P08_VESTIBULE_GLASS_'+label,u,w,.08,dh,.02,openings,glass);ob['opening_id']=ident
    wall('P08_VESTIBULE_TOP_'+label,u,w,dh-.1,dh,.08,openings,metal)
    for n,p in enumerate([u,w]):wall(f'P08_VESTIBULE_POST_{label}_{n}',p-v*.04,p+v*.04,0,dh,.08,openings,metal)
   prism('P08_VESTIBULE_TOP_GLASS',[door_l,door_r,front_r,front_l],dh,dh+.02,openings,glass)
   wall('P08_VESTIBULE_FRONT_HEAD',front_l,front_r,dh-.1,dh,.08,openings,metal)
   opening_checks.append(dict(id=ident,world_midpoint=[mid.x,mid.y,1.4],normal_xy=list(outward),clear_width_m=dw,clear_head_z=dh,revolving_leaves_modeled=False))
  else:
   ob=wall(ident+'_GLASS',ll,rr,z0+fw,z1-fw,E['glass_thickness_m'],openings,glass);ob['opening_id']=ident
  marker=bpy.data.objects.new(ident,None);openings.objects.link(marker);marker.location=(*mid,(z0+z1)/2);marker.empty_display_size=.12;marker.hide_render=True;marker['schedule_id']=ident;marker['status']='pilot_opening_not_final';marker['clear_width_m']=clear;marker['clear_height_m']=z1-z0
# 3. Lower north-facing main roof: glass band, inclined triangular faces, gable.
for i in [0,1,7]:hide(bpy.data.objects['P05_MAIN_ATRIUM_BASE_'+str(i)])
# The full atrium footprint must remain open through the opaque roof deck.
cut=bpy.data.objects['P05_ATRIUM_ROOF_VOID'];cutter=prism('P07_ATRIUM_SQUARE_CUTTER',list(map(xy,[[462,334],[688,334],[688,560],[462,560]])),H-4,H+1,lower,stone,'102,026,087,119')
cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE';cutter['collision_role']='boolean_cutter'
for mod in bpy.data.objects['P05_MAIN_ROOF_DECK'].modifiers:
 if mod.type=='BOOLEAN' and mod.object==cut:mod.object=cutter
for i in [3,5]:
 ob=bpy.data.objects['P05_MAIN_ATRIUM_BASE_'+str(i)];ob.data.materials.clear();ob.data.materials.append(stone);ob['assumption_note']='Opaque high-side enclosure supported by 116; internal openings remain unresolved.'
outer=Q['outer_canonical'];band=L['band_bottom_z'];low=L['low_eave_z'];eave=min(Q['eave_z'])
for i in [1,7]:
 j=(i+1)%8;mesh(f'P06_LOWER_BAND_{i}',[pt(outer[i],band),pt(outer[j],band),pt(outer[j],eave),pt(outer[i],eave)],[(0,1,2,3)],lower,roofglass,'087,119,026')
for label,a,b,corn in [('WEST',outer[1],outer[2],[688,334]),('EAST',outer[7],outer[0],[462,334])]:
 mesh('P06_LOWER_SLOPE_'+label,[pt(a,band),pt(b,band),pt(corn,low)],[(0,1,2)],lower,roofglass,'087,119,026,102')
 near=outer[1] if label=='WEST' else outer[0]
 mesh('P06_NORTH_STONE_GABLE_'+label,[pt(near,low),pt(corn,low),pt(near,band)],[(0,1,2)],lower,stone,'087,119,026')
mesh('P06_NORTH_GLASS_SLOT',[pt(outer[0],low),pt(outer[1],low),pt(outer[1],eave),pt(outer[0],eave)],[(0,1,2,3)],lower,roofglass,'087,119')
for label,a,b in [('E',[462,334],outer[0]),('W',outer[1],[688,334])]:wall('P06_NORTH_BASE_'+label,xy(a),xy(b),0,low,.3,lower,stone,'087,119,102')
# 4. Side hall roof heights replace the previous UP+.8 / H guess. Contours unchanged.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('P05_EAST_GLAZED_ROOF','P05_EAST_LOW_GLAZING','P05_WEST_CURVED_ROOF_','P05_WEST_LOW_GLAZING_')):hide(ob)
hi_e=[[289.5,266.5],[462.4,441.1]];lo_e=[[289.5,161.5],[462.4,336.1]]
mesh('P06_EAST_GLAZED_ROOF',[pt(hi_e[0],band),pt(hi_e[1],band),pt(lo_e[1],low),pt(lo_e[0],low)],[(0,1,2,3)],lower,roofglass,'034,087,119,102')
mesh('P06_EAST_LOW_GLAZING',[pt(lo_e[0],0),pt(lo_e[1],0),pt(lo_e[1],low),pt(lo_e[0],low)],[(0,1,2,3)],lower,roofglass,'034,087,102')
curve=F['polygons']['WEST_CAFE'][:-2];high=[]
for i,p in enumerate(curve):
 t=i/(len(curve)-1);high.append(([688+(862-688)*t,432+(258-432)*t],band+2.55*math.sin(math.pi*t)))
for i,(a,b) in enumerate(zip(curve,curve[1:])):
 u,zu=high[i];v,zv=high[i+1]
 ob=mesh('P06_WEST_GLAZED_ROOF_'+str(i),[pt(a,low),pt(b,low),pt(v,zv),pt(u,zu)],[(0,1,2),(0,2,3)],lower,roofglass,'093,119,101,102')
 ob['assumption_note']='Curved roof candidate: plan curved outer boundary and straight inner boundary; sinusoidal high-edge rise 2.55 m from 101 visual section, not fitted/accepted.'
 mesh('P06_WEST_LOW_GLAZING_'+str(i),[pt(a,0),pt(b,0),pt(b,low),pt(a,low)],[(0,1,2,3)],lower,roofglass,'093,102')
# 5. Small documentation-space roof lantern, independently anchored in plan 103.
T=P['reading_lantern'];center=T['center_canonical'];angles=[math.pi/8+i*math.pi/4 for i in range(8)]
def ring(radius):return [[center[0]+radius*math.cos(t),center[1]+radius*math.sin(t)] for t in angles]
oo,ii=ring(T['outer_radius_canonical']),ring(T['inner_radius_canonical'])
prism('P06_READING_CURB',list(map(xy,oo)),E['roof_top_z'],T['curb_top'],reading,stone,'103,116')
for i in range(8):
 j=(i+1)%8
 mesh('P06_READING_SLOPE_'+str(i),[pt(oo[i],T['curb_top']),pt(oo[j],T['curb_top']),pt(ii[j],T['shoulder']),pt(ii[i],T['shoulder'])],[(0,1,2,3)],reading,roofglass,'103,116')
 mesh('P06_READING_LANTERN_'+str(i),[pt(ii[i],T['shoulder']),pt(ii[j],T['shoulder']),pt(ii[j],T['lantern_top']),pt(ii[i],T['lantern_top'])],[(0,1,2,3)],reading,roofglass,'103,116')
 mesh('P06_READING_CAP_'+str(i),[pt(ii[i],T['lantern_top']),pt(ii[j],T['lantern_top']),pt(center,T['apex'])],[(0,1,2)],reading,roofglass,'103,116')
# Photo cameras for both rear images and the independent entrance-side photograph.
origin=Vector(pt((575,447),0));xp=(Vector(pt((574,447),0))-origin).normalized();yp=(Vector(pt((575,448),0))-origin).normalized();transform=Matrix((xp,yp,Vector((0,0,1)))).transposed()
multi=json.loads((B/'reports/P06_multiview.json').read_text());entry=json.loads((B/'reports/P06_camera_fit_116.json').read_text());camera_info={**multi['photos'],'116':{**entry['candidates']['triangular_canopy'],'source_path':entry['source_path'],'size':entry['size']}}
cameras={};projection_errors={}
for key,d in camera_info.items():
 cd=bpy.data.cameras.new('P07_PHOTO_'+key+'_CONDITIONAL');cam=bpy.data.objects.new(cd.name,cd);bpy.data.collections['99_QA'].objects.link(cam);p=d['camera'];rows=[Vector(v) for v in d['basis_rows']]
 cam.location=origin+transform@Vector(p[:3]);cam.rotation_euler=Matrix((transform@rows[0],transform@rows[1],-(transform@rows[2]))).transposed().to_euler();cd.type='PERSP';cd.sensor_fit='HORIZONTAL';cd.sensor_width=36;cd.lens=d['focal_px']*36/d['size'][0];cd.clip_end=3000;cam['status']='conditional_not_metric_pose';cam['source_ids']=key;cam['fit_rmse_px']=d['fit_rmse_px'];cam['holdout_rmse_px']=d['holdout_rmse_px']
 im=bpy.data.images.load(str(R/d['source_path']),check_existing=True);im.pack();cd.show_background_images=True;bg=cd.background_images.new();bg.image=im;bg.alpha=.4;bg.display_depth='BACK';bg.frame_method='FIT'
 S.camera=cam;S.render.resolution_x,S.render.resolution_y=d['size'];S.render.resolution_percentage=100;bpy.context.view_layer.update();errs=[]
 for point in d['landmarks']:
  v=world_to_camera_view(S,cam,origin+transform@Vector(point['local_xyz']));pixel=Vector((v.x*d['size'][0],(1-v.y)*d['size'][1]));errs.append((pixel-Vector(point['predicted_px'])).length)
 assert max(errs)<.05,(key,max(errs));projection_errors[key]=max(errs);cameras[key]=cam
# Close entry camera and default review view.
cd=bpy.data.cameras.new('P07_ENTRY_DETAIL');detailcam=bpy.data.objects.new(cd.name,cd);bpy.data.collections['99_QA'].objects.link(detailcam);detailcam.location=pt((515,865),5);target=Vector(pt((575,707),5.5));detailcam.rotation_euler=(target-detailcam.location).to_track_quat('-Z','Y').to_euler();cd.lens=24;cd.clip_end=1000
S.camera=cameras['116'];S.render.resolution_x=1600;S.render.resolution_y=1066;S.render.film_transparent=False;S['stage']='P07/P08 regional entry pilot, three conditional photo cameras; global shell and detailed dimensions unaccepted';S['current_file']=out.name
txt=bpy.data.texts.new('P07_READ_ME');txt.write('P07/P08 REGIONAL ENTRY PILOT\nCanopy outline follows 102; corner support and three facade bays follow 008/011/013/116.\nSix opening IDs; glass, preview frames, masonry envelope separated. Revolving mechanism NOT modeled.\nLower GH glazing corrected; side-hall roof surfaces and small reading lantern remain candidates.\nConditional cameras 087/119/116; no metric pose accepted. Parameters/provenance in entry_package.json.\nThicknesses are envelope visualization parameters, not structural or fabrication specifications.\n')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=pt((560,620),8);area.spaces.active.region_3d.view_distance=105
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for name,cam,size in [('116',cameras['116'],[2000,1333]),('087',cameras['087'],[1920,1281]),('entry_detail',detailcam,[1600,1400])]:
 S.camera=cam;S.render.resolution_x,S.render.resolution_y=size;S.render.filepath=str(B/f'renders/qa/P07_{name}.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),new_objects=len(objects),solid_objects=solid_names,hidden_superseded=hidden,projection_errors_px=projection_errors,opening_count=len(schedule),door_clearance_checks=opening_checks,camera_count=3,metric_cameras=0,accepted_for_construction=False)
(B/'reports/P07_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P07_SAVED',out,'new_objects',len(objects),'projection_errors',projection_errors)
