"""R18 open double-leaf pavilion door and round interior link portal members."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R18_PAVYON_GECIT_DETAY_{version}.blend';assert not out.exists();base='MUDAM_R17_PAVYON_MEKAN_v001.blend';bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('P12_PAVILION_LINK_DETAIL_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);up=Vector((0,0,1));made=[];panels=[];metal=bpy.data.materials['P10_FRAME_PREVIEW'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];H=Z['Z_LINK_CEILING'];P=dict(source_ids=['067','068','PA0098','102','101'],door_clear_nominal_m=1.70,door_head_z=3.35,frame_width_m=.07,leaf_frame_m=.045,leaf_thickness_m=.045,glass_thickness_m=.018,open_angle_degrees=90,link_round_member_diameter_m=.12,link_bays=8,limits=['067 shows two open framed glass leaves, side lights and divided transom. Exact hardware/angles and measurements unverified.','068 shows round internal bridge members alongside rectangular glazing frames. Eight bays inherited candidate, not new count verification.','Frame/rod/joint fabrication and structural sizing not asserted.'])
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
origin=point(171,279);ey=(point(171,280)-origin).normalized();ex=(point(172,279)-origin).normalized();width=30*C['meters_per_canonical_pixel'];w=P['door_clear_nominal_m'];fw=P['frame_width_m'];dh=P['door_head_z']
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV_LINK',level_id='L00',source_ids=','.join(P['source_ids']),status='conditional_source_detail',confidence_xy='C existing link outline; D module split',confidence_z='D inherited section and photo ratio',confidence_detail='D provisional member sizes',parameter_ids='pavilion_link_detail.json',assumption_note='Round bridge members and open double leaves supported by 067/068; exact assembly dimensions and mechanisms unverified.').items():ob[k]=v
 made.append(name);return ob
fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,org,axis,u0,u1,d0,d1,z0,z1,mat,kind):
 normal=axis.cross(up);return mesh(name,[org+axis*u+normal*d+up*z for z in [z0,z1] for u,d in [(u0,d0),(u1,d0),(u1,d1),(u0,d1)]],fs,mat,kind)
def fixed(name,u0,u1,z0,z1):
 for tag,l,r,b,t in [('L',u0,u0+fw,z0,z1),('R',u1-fw,u1,z0,z1),('B',u0,u1,z0,z0+fw),('T',u0,u1,z1-fw,z1)]:box(name+'_FRAME_'+tag,origin,ey,l,r,-.05,.05,b,t,metal,'fixed_door_surround_frame_candidate')
 ob=box(name+'_GLASS',origin,ey,u0+fw,u1-fw,-.009,.009,z0+fw,z1-fw,glass,'fixed_sidelight_or_transom');panels.append(ob.name)
fixed('R18_SIDE_LEFT',-width/2,-w/2,0,dh);fixed('R18_SIDE_RIGHT',w/2,width/2,0,dh);fixed('R18_TRANSOM_LEFT',-width/2,0,dh,H);fixed('R18_TRANSOM_RIGHT',0,width/2,dh,H)
leaves=[]
for suffix,sign in [('LEFT',-1),('RIGHT',1)]:
 hinge=origin+ey*sign*(w/2-.02);axis=ex;leafw=w/2;lf=P['leaf_frame_m'];th=P['leaf_thickness_m'];prefix='R18_LEAF_'+suffix
 for tag,l,r,b,t in [('HINGE',0,lf,.02,dh-.02),('FREE',leafw-lf,leafw,.02,dh-.02),('BOTTOM',0,leafw,.02,.02+lf),('TOP',0,leafw,dh-.02-lf,dh-.02)]:box(prefix+'_FRAME_'+tag,hinge,axis,l,r,-th/2,th/2,b,t,metal,'open_glass_door_leaf_frame_candidate')
 ob=box(prefix+'_GLASS',hinge,axis,lf,leafw-lf,-.009,.009,.02+lf,dh-.02-lf,glass,'open_door_leaf_glass_candidate');panels.append(ob.name);leaves.append(dict(id=prefix,hinge=list(hinge),free_edge=list(hinge+axis*leafw),angle_candidate=90))
def tube(name,a,b,diam,kind):
 axis=(b-a).normalized();ref=up if abs(axis.z)<.9 else ex;x=axis.cross(ref).normalized()*diam/2;y=axis.cross(x).normalized()*diam/2;N=16;ring=[x*math.cos(i*math.tau/N)+y*math.sin(i*math.tau/N) for i in range(N)];ob=mesh(name,[p+q for p in [a,b] for q in ring],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],metal,kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
for row in leaves:
 hinge=Vector(row['hinge']);free=Vector(row['free_edge']);a=free-ex*.09+ey*.07+up*1.05;b=a+ex*.15;tube(row['id']+'_LEVER',a,b,.018,'visible_door_lever_envelope_candidate');tube(row['id']+'_LEVER_STUB',a-ey*.07,a,.018,'door_handle_standoff_candidate')
portals=[]
for i in range(P['link_bays']+1):
 x=171+118*i/P['link_bays'];a=point(x,264,0)+ey*.13;b=point(x,294,0)-ey*.13;top=H-.18
 for suffix,p in [('L',a),('R',b)]:tube(f'R18_LINK_COLUMN_{i}_{suffix}',p,p+up*top,P['link_round_member_diameter_m'],'round_bridge_interior_member_candidate')
 tube(f'R18_LINK_TRANSVERSE_{i}',a+up*top,b+up*top,P['link_round_member_diameter_m'],'round_bridge_interior_member_candidate');portals.append(dict(x=x,left=list(a),right=list(b),top_z=top))
bpy.context.scene['stage']='R18 pavilion link double door and round portal members';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R18_SOURCE_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'config/pavilion_link_detail.json').write_text(json.dumps(P,indent=2),encoding='utf8');(B/'reports/R18_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,panels=panels,leaves=leaves,portals=portals,changed_inherited_objects=[],construction_acceptance=False),indent=2),encoding='utf8')
