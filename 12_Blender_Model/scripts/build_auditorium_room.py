"""R19 source-limited auditorium envelope, tiers and coffered ceiling."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/auditorium_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R19_ODITORYUM_MEKAN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P16_AUDITORIUM_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];up=Vector((0,0,1));LOW=Z['Z_LM1_FINISH'];s,dx,dy=C['basement_registration']['source_to_canonical'];unit=s*C['meters_per_canonical_pixel']
def material(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
wood=material('R19_WOOD_FINISH_CANDIDATE',(.28,.115,.044),.48);white=material('R19_CEILING_WHITE_CANDIDATE',(.72,.70,.65),.75);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];dark=material('R19_RECESSED_GRILLE_CANDIDATE',(.04,.04,.04),.8)
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='AUDITORIUM',level_id='LM1',source_ids=','.join(P['source_ids']),confidence_xy='C registered 104; D detail widths',confidence_z='D section/photo candidate',confidence_detail='D unmeasured',status='conditional_auditorium_room',parameter_ids='auditorium_room.json',assumption_note='Tier rises, coffer count and thicknesses are candidates. Source seat symbols do not establish actual capacity.').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 pts=[point(*p) for p in poly];N=len(pts);return mesh(name,[p+up*z for z in [z0,z1] for p in pts],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat,kind)
def box(name,x0,x1,y0,y1,z0,z1,mat=wood,kind='auditorium_finish_volume'):
 return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,kind)
L,RX=P['room_x'];front=P['front_y'];rear=P['rear_y'];A,D=P['seat_block_x'];ys,ye=P['seat_y'];H=P['ceiling_bottom_z'];t=P['wall_thickness_m']/unit
# Preserve source pilot but supersede it with a full, closed interior floor.
old=bpy.data.objects['P05_ZONE_LM1_AUDITORIUM'];old.hide_render=True;old.hide_set(True);changed=[old.name]
box('R19_ROOM_FLOOR',L,RX,front,rear,LOW-.2,LOW,stone)
# Front stage footprint traced from the 104 recess; forward lip is visible in 071/073.
stagepoly=[(486,428),(558,428),(558,414),(554,414),(540,398),(504,398),(488,414),(486,414)]
prism('R19_STAGE',stagepoly,LOW-.2,LOW+P['stage_rise_m'],stone,'stage_platform_candidate')
for i in range(P['row_count']):
 y0=ys+(ye-ys)*i/P['row_count'];y1=ys+(ye-ys)*(i+1)/P['row_count'];z=LOW+(i+1)*P['row_rise_m'];box(f'R19_TIER_{i+1:02d}',A,D,y0,y1,LOW,z,stone,'seating_tier_candidate')
for side,x0,x1 in [('L',L,A),('R',D,RX)]:
 for i in range(P['row_count']*2):
  y0=ys+(ye-ys)*i/16;y1=ys+(ye-ys)*(i+1)/16;box(f'R19_AISLE_{side}_{i+1:02d}',x0,x1,y0,y1,LOW,LOW+(i+1)*P['row_rise_m']/2,stone,'aisle_tread_candidate')
box('R19_REAR_LANDING',L,RX,ye,rear,LOW,LOW+8*P['row_rise_m'],stone)
# Two shallow side access steps alongside the visible raised stage front.
for side,x0,x1 in [('L',486,492),('R',552,558)]:
 for i in range(2):box(f'R19_STAGE_STEP_{side}_{i}',x0,x1,428+(1-i)*2.4,428+(2-i)*2.4,LOW,LOW+(i+1)*P['stage_rise_m']/3,stone)
box('R19_WALL_L',L-t,L,front,rear,LOW,H);box('R19_WALL_R',RX,RX+t,front,rear,LOW,H);box('R19_WALL_REAR',L-t,RX+t,rear,rear+t,LOW,H)
# Door openings at front wings; position and height conditional to source diagram.
for side,x0,x1,d0,d1 in [('L',L,486,469,480),('R',558,RX,565,576)]:
 box('R19_FRONT_'+side+'_OUTER',x0,d0,front-t,front,LOW,H);box('R19_FRONT_'+side+'_INNER',d1,x1,front-t,front,LOW,H);box('R19_FRONT_'+side+'_HEAD',d0,d1,front-t,front,LOW+2.25,H)
 # Flooring joins foyer footprint across the front opening.
 box('R19_ENTRY_FLOOR_'+side,d0,d1,413,front,LOW-.2,LOW,stone)
# Recess walls follow stage backing; stone front piers are supported by 071/073.
path=[(486,front),(486,414),(488,414),(504,398),(540,398),(554,414),(558,414),(558,front)]
for i,(a,b) in enumerate(zip(path,path[1:])):
 va=Vector(a);vb=Vector(b);n=Vector((vb.y-va.y,va.x-vb.x)).normalized()*t
 prism(f'R19_STAGE_BACK_{i}',[a,b,tuple(vb+n),tuple(va+n)],LOW,H,wood,'stage_backing_wall_candidate')
for side,x0,x1 in [('L',484.5,488),('R',556,559.5)]:box('R19_STONE_PIER_'+side,x0,x1,front,428,LOW,H,stone,'visible_stage_pier_candidate')
# New LCB view shows the rear projection booth projecting to the last row.
for side,x0,x1 in [('L',494,512),('R',534,552)]:box('R19_BOOTH_FRONT_'+side,x0,x1,505,505+t,LOW+1.92,H)
box('R19_BOOTH_WINDOW_BELOW',512,534,505,505+t,LOW+1.92,LOW+2.75);box('R19_BOOTH_WINDOW_ABOVE',512,534,505,505+t,LOW+3.65,H)
box('R19_BOOTH_WINDOW_GLASS',512,534,505+.08/unit,505+.098/unit,LOW+2.75,LOW+3.65,bpy.data.materials['P10_GLASS_PREVIEW'],'projection_booth_glass_candidate')
for side,x0,x1 in [('L',494-t,494),('R',552,552+t)]:box('R19_BOOTH_SIDE_'+side,x0,x1,505,rear,LOW+1.92,H)
for side,x0,x1 in [('L',484.5,488),('R',556,559.5)]:box('R19_REAR_PIER_'+side,x0,x1,501.5,506.5,LOW,H,stone,'visible_rear_stone_pier_candidate')
# Flat perimeter soffit and a 5x5 candidate field of tapered coffers.
cx0,cx1=484.5,560.5;cy0,cy1=429,505;top=P['ceiling_top_z']
box('R19_CEILING_LEFT',L,cx0,front,rear,H,top,white);box('R19_CEILING_RIGHT',cx1,RX,front,rear,H,top,white);box('R19_CEILING_FRONT',cx0,cx1,front,cy0,H,top,white);box('R19_CEILING_REAR',cx0,cx1,cy1,rear,H,top,white)
prism('R19_STAGE_SOFFIT',[(486,front),(486,414),(488,414),(504,398),(540,398),(554,414),(558,414),(558,front)],H,top,white,'stage_soffit_candidate')
beam=P['coffer_beam_width_m']/unit;inset=P['coffer_inset_m']/unit
for ix in range(P['coffer_columns']):
 for iy in range(P['coffer_rows']):
  x0=cx0+(cx1-cx0)*ix/5;x1=cx0+(cx1-cx0)*(ix+1)/5;y0=cy0+(cy1-cy0)*iy/5;y1=cy0+(cy1-cy0)*(iy+1)/5
  outer=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)];ring=[(x0+beam/2,y0+beam/2),(x1-beam/2,y0+beam/2),(x1-beam/2,y1-beam/2),(x0+beam/2,y1-beam/2)];inner=[(x0+inset,y0+inset),(x1-inset,y0+inset),(x1-inset,y1-inset),(x0+inset,y1-inset)];vs=[point(*p,H) for p in outer]+[point(*p,H) for p in ring]+[point(*p,P['coffer_inset_top_z']) for p in inner]+[point(*p,top) for p in outer];fs=[]
  for i in range(4):j=(i+1)%4;fs.extend([(i,j,4+j,4+i),(4+i,4+j,8+j,8+i),(i,12+i,12+j,j)])
  fs.extend([(8,9,10,11),(12,15,14,13)]);mesh(f'R19_COFFER_{ix}_{iy}',vs,fs,white,'tapered_coffer_candidate');xc=(x0+x1)/2;yc=(y0+y1)/2;g=.15/unit;box(f'R19_GRILLE_{ix}_{iy}',xc-g,xc+g,yc-g,yc+g,P['coffer_inset_top_z']-.012,P['coffer_inset_top_z'],dark,'coffer_center_insert_candidate')
bpy.context.scene['stage']='R19 auditorium room/tier/coffer candidates; seat layout unresolved';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R19_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,hidden_superseded=changed,lower_z=LOW,rear_landing_z=LOW+8*P['row_rise_m'],native_pixel_m=unit,construction_acceptance=False);(B/'reports/R19_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
