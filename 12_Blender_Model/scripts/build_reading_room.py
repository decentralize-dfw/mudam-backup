"""R09: PDF103 room walls, three passages and consistent ceiling perimeter."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/reading_room.json').read_text());Q=json.loads((B/'config/reading_ceiling.json').read_text());old=json.loads((B/'reports/R08_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=old['floor_z'];TOP=Q['ceiling_lower_z'];HEAD=UP+P['portal_head_above_upper_floor_m'];up=Vector((0,0,1))
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R09_OKUMA_MEKANI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P17_READING_ROOM_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];made=[];cutters=[];changed=[]
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.get(name)
 if ob is None:ob=bpy.data.objects.new(name,me);root.objects.link(ob)
 else:ob.data=me;changed.append(name)
 me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='READING',level_id='LP1',source_ids='PDF2016,103,015,016',confidence_xy='C fitted PDF103 inner contour',confidence_z='D inherited candidate ceiling and portal height',confidence_detail='D thickness and connections',parameter_ids='reading_room.json',status='conditional_reading_room_candidate',assumption_note='Inner contour fit maximum 0.809 canonical pixel. Plan source is not warped. Three openings retained; door identity and hardware unverified.',export_group='R09_CANDIDATE',collision_role='review_only').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);return mesh(name,[tuple(p+up*z) for z in [z0,z1] for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def solid(name,poly,delta,mat,kind):
 n=len(poly);return mesh(name,[tuple(p) for p in poly]+[tuple(p+delta) for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def tube(name,a,b,diam,kind,sides=12):
 t=(b-a).normalized();ref=up if abs(t.z)<.9 else Vector((1,0,0));u=t.cross(ref).normalized()*diam/2;v=t.cross(u).normalized()*diam/2;ring=[u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides) for i in range(sides)];return mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],metal,kind)
inner=list(map(point,P['room_inner_polygon']));center=sum(inner,Vector())/8;outer=[]
for i,p in enumerate(inner):
 prev=(p-inner[(i-1)%8]).normalized();nxt=(inner[(i+1)%8]-p).normalized();n1=up.cross(prev);n2=up.cross(nxt)
 if n1.dot(p-center)<0:n1=-n1
 if n2.dot(p-center)<0:n2=-n2
 bis=(n1+n2).normalized();outer.append(p+bis*P['wall_display_thickness_m']/bis.dot(n1))
portal_by_edge={p['edge']:p for p in P['portals']};portals=[];walls=[]
for i in range(8):
 j=(i+1)%8;cuts=[(0,1,UP,TOP,'FULL')]
 if i in portal_by_edge:
  p=portal_by_edge[i];axis=p['coordinate_axis'];a=P['room_inner_polygon'][i][axis];b=P['room_inner_polygon'][j][axis];t0,t1=sorted((v-a)/(b-a) for v in p['source_range']);assert 0<t0<t1<1;cuts=[(0,t0,UP,TOP,'A'),(t0,t1,HEAD,TOP,'HEAD'),(t1,1,UP,TOP,'B')];portals.append(dict(id=p['id'],edge=i,a=list(inner[i].lerp(inner[j],t0)),b=list(inner[i].lerp(inner[j],t1)),floor_z=UP,head_z=HEAD,width=(inner[j]-inner[i]).length*(t1-t0)))
 for a,b,z0,z1,label in cuts:
  poly=[inner[i].lerp(inner[j],a),inner[i].lerp(inner[j],b),outer[i].lerp(outer[j],b),outer[i].lerp(outer[j],a)];name=f'R09_READING_WALL_{i}_{label}';prism(name,poly,z0,z1,stone,'room_wall_or_portal_head_envelope');walls.append(name)
# Floor passage unions fill only the three source-identified links, retaining
# the earlier floor opening and independently editable connector cutters.
floor=bpy.data.objects['P17_READING_FLOOR'];changed.append(floor.name)
for p in P['portals']:
 cut=prism('R09_FLOOR_LINK_'+p['id'],list(map(point,p['connector_polygon'])),UP-.2,UP,bpy.data.materials['P05_FLOOR_REFERENCE'],'hidden_source_passage_floor_union');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';cutters.append(cut.name);mod=floor.modifiers.new('R09 source passage '+p['id'],'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=cut
# The new source-based perimeter also replaces the provisional ceiling transfer
# from the older floor outline. Inner square aperture and heights stay fixed.
ceiling_outer=[p+up*TOP for p in inner];ceiling_inner=list(map(Vector,old['inner_ceiling_world']));facets=[]
for i in range(8):
 j=(i+1)%8;k=i//2;poly=[ceiling_outer[i],ceiling_outer[j],ceiling_inner[k]] if i%2==0 else [ceiling_outer[i],ceiling_outer[j],ceiling_inner[(k+1)%4],ceiling_inner[k]];name=f'R08_STONE_CEILING_{i}';solid(name,poly,up*Q['ceiling_display_thickness_m'],stone,'source_aligned_inclined_stone_ceiling');facets.append(name)
faces=[tuple(range(7,-1,-1)),tuple(range(8,12))]
for i in range(8):
 j=(i+1)%8;k=i//2;faces.append((i,j,8+k) if i%2==0 else (i,j,8+(k+1)%4,8+k))
cut=mesh('R08_FUNNEL_VOID',list(map(tuple,ceiling_outer+ceiling_inner)),faces,stone,'hidden_source_aligned_funnel_cutter');cut.hide_render=True;cut.hide_set(True);cutters.append(cut.name)
# Reattach the existing candidate wires to the changed ceiling geometry.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();anchors=[]
for row in old['light_anchors']:
 p=Vector(row['point']);start=Vector((p.x,p.y,UP));hits=[]
 for name in facets:
  ob=bpy.data.objects[name].evaluated_get(deps);inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@start,inv.to_3x3()@up,distance=15)
  if hit:hits.append(ob.matrix_world@loc)
 assert hits;anchor=min(hits,key=lambda v:v.z)-up*.03;j=row['index'];tube(f'R08_LIGHT_WIRE_{j:02}',Vector(row['tube_end']),anchor,Q['wire_diameter_m'],'simple_radial_suspension_candidate',8);tube(f'R08_CEILING_ANCHOR_{j:02}',anchor,anchor+up*.03,.016,'ceiling_attachment_envelope');anchors.append(dict(index=j,point=list(anchor),tube_end=row['tube_end']))
S['stage']='R09 reading room walls and three source passages';S['current_file']=out.name;bpy.data.texts.new('R09_SOURCE_AND_ASSUMPTIONS').write(json.dumps(P,indent=2));cam=bpy.data.objects['R08_READING_UPWARD_REVIEW'];cam.location=center+Vector((2.5,-2.5,UP+1.65));target=center+up*8;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20;S.camera=cam;S.render.filepath=str(B/'renders/qa/R09_reading_room.png');S.render.resolution_x=1600;S.render.resolution_y=1250;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
keep=(set(old['closed_objects'])|set(made)|{'P17_READING_FLOOR'})-set(cutters);keep.update(o.name for o in S.objects if o.name.startswith('P15_READING_'))
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=sorted(set(made)-set(cutters)),changed_floor=floor.name,cutters=cutters,changed_inherited_objects=sorted(set(changed)),walls=walls,portals=portals,room_inner_world=list(map(list,inner)),outer_ceiling_world=list(map(list,ceiling_outer)),inner_ceiling_world=old['inner_ceiling_world'],light_anchors=anchors,source_corner_max_offset_canonical=P['fit_max_offset_canonical'],ceiling_facets=facets,roof_boolean_targets=old['roof_boolean_targets'],floor_z=UP,center_world=old['center_world'],construction_acceptance=False);(B/'reports/R09_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R09_SAVED',out)
