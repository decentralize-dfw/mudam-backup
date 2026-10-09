"""R22 photo-derived auditorium doors, screen and candidate recessed fixtures."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';prior=json.loads((B/'reports/R21_build_report.json').read_text());P=json.loads((B/'config/auditorium_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];LOW=json.loads((B/'reports/R19_build_report.json').read_text())['lower_z'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R22_ODITORYUM_DONATI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/prior['file']));root=bpy.data.collections.new('P16_AUDITORIUM_FIXTURES_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];cutters=[];s,dx,dy=C['basement_registration']['source_to_canonical'];unit=s*C['meters_per_canonical_pixel'];up=Vector((0,0,1));wood=bpy.data.materials['R19_WOOD_FINISH_CANDIDATE'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];white=bpy.data.materials['R19_CEILING_WHITE_CANDIDATE'];dark=bpy.data.materials['R21_DARK_CAVITY_CANDIDATE'];emitter=white.copy();emitter.name='R22_LIGHT_DIFFUSER_CANDIDATE';bs=emitter.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.83,.59,1);bs.inputs['Emission Strength'].default_value=3
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
ex=(point(465,440)-point(464,440)).normalized();ey=(point(464,441)-point(464,440)).normalized()
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='AUDITORIUM',level_id='LM1',source_ids='071,073,074,076,LCB_auditorium3,LCB_aschman2',confidence_xy='D photo/plan candidate',confidence_z='D unmeasured',confidence_detail='D visible form only',status='conditional_auditorium_fixture',assumption_note='Source images support fixture families. Exact positions, angles, counts, brightness, hardware and equipment dimensions remain candidates.').items():ob[k]=v
 made.append(name);return ob
def box(name,o,a,b,w,d,h,mat,kind):
 vs=[o+a*x+b*y+up*z for z in [0,h] for x,y in [(0,0),(w,0),(w,d),(0,d)]];return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,kind)
def tube(name,a,b,r,mat,kind,n=24):
 axis=(b-a).normalized();u=axis.cross(Vector((1,0,0)))
 if u.length<.01:u=axis.cross(Vector((0,1,0)))
 u.normalize();v=axis.cross(u);vs=[p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for p in [a,b] for i in range(n)];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,vs,fs,mat,kind)
# Both leaves are shown open for review. 073 proves the right opening; left state is candidate.
door_records=[]
for side,x0,x1 in [('L',469,480),('R',565,576)]:
 w=(x1-x0)*unit;z=LOW;origin=point(x0,421,z);H=2.25
 for label,u,v,ww,hh in [('L',0,0,.04,H),('R',w-.04,0,.04,H),('T',0,H-.04,w,.04)]:box('R22_DOOR_FRAME_'+side+'_'+label,origin+ex*u+up*v-ey*.025,ex,ey,ww,.07,hh,wood,'timber_door_frame_candidate')
 # Leaf stands along the jamb, outside the central passage; direction adjustable.
 hinge=point(x0+.4,421,LOW+.015);leaf=box('R22_DOOR_LEAF_'+side,hinge,ey,ex,w-.10,.045,H-.055,wood,'open_flush_timber_leaf_candidate');door_records.append(dict(side=side,width=w-.10,open_angle_degrees=90,objects=[leaf.name]))
 for z in [.28,1.1,1.98]:tube(f'R22_HINGE_{side}_{z}',hinge+up*z,hinge+up*(z+.08),.012,metal,'visible_hinge_envelope_candidate')
 handle=hinge+ey*(w-.26)+up*1.02+ex*.065;tube('R22_HANDLE_STEM_'+side,handle-ex*.045,handle,.009,metal,'lever_envelope_candidate');tube('R22_HANDLE_'+side,handle,handle-ey*.12,.009,metal,'lever_envelope_candidate')
# Blank equipment surface from 071/073, without importing projected artwork/content.
screen_width=4.8;screen_height=2.7;screen_bottom=LOW+.75;center=point(522,405,screen_bottom)
box('R22_PROJECTION_SURFACE',center-ex*screen_width/2,ex,ey,screen_width,.025,screen_height,white,'projection_surface_candidate');box('R22_SCREEN_LOWER_PLINTH',point(522,405,LOW+.42)-ex*screen_width/2,ex,ey,screen_width,.12,.33,white,'screen_base_candidate')
# Photographs show small round recessed downlights in the flat perimeter soffit.
H=P['ceiling_bottom_z'];fixtures=[];changed=[];locations=[]
for side,x in [('LEFT',474),('RIGHT',571)]:
 for y in [435,448,461,474,487,500]:locations.append((x,y,'R19_CEILING_'+side))
for x in [494,508,536,550]:locations.append((x,425,'R19_CEILING_FRONT'))
for i,(x,y,ceiling_name) in enumerate(locations):
 c=point(x,y,H);radius=.065;n=32
 cut=tube(f'R22_LIGHT_CUT_{i:02d}',c-up*.05,c+up*.17,radius,dark,'hidden_downlight_opening_operand',n);cut.hide_render=True;cut.hide_set(True);cutters.append(cut.name);ceiling=bpy.data.objects[ceiling_name];mod=ceiling.modifiers.new(f'R22_recess_{i:02d}','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
 if ceiling_name not in changed:changed.append(ceiling_name)
 # Closed annular trim and tapered reflector shell, with real center opening.
 for label,radii,levels,mat in [('TRIM',[.078,.058],[-.012,.002],metal),('REFLECTOR',[.058,.031],[0,.065],metal)]:
  if label=='TRIM':rings=[(r,z) for z in levels for r in radii]
  else:rings=[(.058,0),(.056,0),(.031,.065),(.029,.065)]
  vs=[c+ex*(r*math.cos(j*math.tau/n))+ey*(r*math.sin(j*math.tau/n))+up*z for r,z in rings for j in range(n)];fs=[]
  for a,b in [(0,1),(1,3),(3,2),(2,0)]:
   for j in range(n):k=(j+1)%n;fs.append((a*n+j,a*n+k,b*n+k,b*n+j))
  mesh(f'R22_LIGHT_{label}_{i:02d}',vs,fs,mat,'recessed_downlight_'+label.lower()+'_candidate')
 tube(f'R22_LIGHT_DIFFUSER_{i:02d}',c+up*.063,c+up*.067,.028,emitter,'light_diffuser_candidate',32)
 ld=bpy.data.lights.new(f'R22_DOWNLIGHT_{i:02d}','SPOT');ld.energy=32;ld.color=(1,.88,.70);ld.spot_size=math.radians(80);ld.spot_blend=.55;ld.shadow_soft_size=.018;lo=bpy.data.objects.new(ld.name,ld);root.objects.link(lo);lo.location=c+up*.045;lo['status']='conditional fixture intensity and placement';fixtures.append(dict(x=x,y=y,ceiling=ceiling_name,center=list(c),operand=cut.name))
config=dict(base_scene=prior['file'],source_ids=['071','073','074','076','LCB_auditorium3','LCB_aschman2'],door_state='both 90deg open candidates; only right open state directly visible in 073',screen_m=[screen_width,screen_height],downlight_count=len(fixtures),fixture_placement='perimeter-family candidate, not individually photo-matched',limits=['Exact equipment/screen placement and current exhibition configuration unverified.','Light distribution, color and energy are preview values, not photometry.','No concealed wiring, fire-rating or door mechanism specification inferred.']);(B/'config/auditorium_fixtures.json').write_text(json.dumps(config,indent=2),encoding='utf8');bpy.data.texts.new('R22_SOURCE_AND_LIMITS').write(json.dumps(config,indent=2));bpy.context.scene['stage']='R22 auditorium doors, screen and recessed fixture candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=prior['file'],closed_objects=made,changed_inherited_objects=changed,cutters=cutters,fixtures=fixtures,doors=door_records,construction_acceptance=False);(B/'reports/R22_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
