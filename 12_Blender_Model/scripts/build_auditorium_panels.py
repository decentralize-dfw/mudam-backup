"""R21: timber panel joints and through-perforated acoustic face candidates."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';prior=json.loads((B/'reports/R20_build_report.json').read_text());P=json.loads((B/'config/auditorium_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];LOW=json.loads((B/'reports/R19_build_report.json').read_text())['lower_z'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R21_ODITORYUM_PANEL_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/prior['file']));root=bpy.data.collections.new('P16_AUDITORIUM_WOOD_PANELS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];perforated=[];s,dx,dy=C['basement_registration']['source_to_canonical'];unit=s*C['meters_per_canonical_pixel'];up=Vector((0,0,1));wood=bpy.data.materials['R19_WOOD_FINISH_CANDIDATE'];dark=bpy.data.materials.new('R21_DARK_CAVITY_CANDIDATE');dark.use_nodes=True;dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.008,.006,.004,1);dark.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='AUDITORIUM',level_id='LM1',source_ids='071,072,073,076,LCB_auditorium3,LCB_aschman2',confidence_xy='D panel grid candidate on registered room',confidence_z='D unmeasured panel heights',confidence_detail='C one 15x13 hole grid observed; D dimensions/repetition',status='conditional_timber_panel_detail',assumption_note='076 crop shows 15 columns and 13 rows on one panel. Repeated grids, margins, depth and concealed backing are appearance candidates, not manufacturer specification.').items():ob[k]=v
 made.append(name);return ob
def cuboid(name,a,ex,ez,normal,w,h,depth,mat,kind):
 vs=[a+ex*x+ez*z+normal*d for d in [0,depth] for x,z in [(0,0),(w,0),(w,h),(0,h)]];return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,kind)
def panel(name,a,b,z0,z1,normal,holes=False):
 ex=(b-a).normalized();w=(b-a).length-.008;h=z1-z0-.008;origin=a+ex*.004+up*(z0+.004)+normal*.015;depth=.024
 # A thin dark cavity plane supports the observed deep square appearance.
 if not holes:
  return cuboid(name,origin,ex,up,normal,w,h,depth,wood,'plain_timber_panel_candidate')
 cuboid(name+'_DARK_BACK',origin-normal*.005,ex,up,normal,w,h,.003,dark,'perforation_cavity_appearance_only')
 nx,ny=15,13;margin=min(.065,w*.07,h*.07);pitchx=(w-2*margin)/nx;pitchy=(h-2*margin)/ny;hw=min(pitchx,pitchy)*.62
 xs=[0,margin];ys=[0,margin]
 for i in range(nx):
  c=margin+(i+.5)*pitchx;xs.extend([c-hw/2,c+hw/2])
 xs.extend([w-margin,w]);xs=sorted(set(xs))
 for j in range(ny):
  c=margin+(j+.5)*pitchy;ys.extend([c-hw/2,c+hw/2])
 ys.extend([h-margin,h]);ys=sorted(set(ys));holeset=set()
 for ix in range(len(xs)-1):
  for iy in range(len(ys)-1):
   xx=(xs[ix]+xs[ix+1])/2;yy=(ys[iy]+ys[iy+1])/2
   if margin<xx<w-margin and margin<yy<h-margin:
    cx=margin+(min(nx-1,int((xx-margin)/pitchx))+.5)*pitchx;cy=margin+(min(ny-1,int((yy-margin)/pitchy))+.5)*pitchy
    if abs(xx-cx)<hw/2-1e-9 and abs(yy-cy)<hw/2-1e-9:holeset.add((ix,iy))
 vs=[];fs=[];indices={};filled={(i,j) for i in range(len(xs)-1) for j in range(len(ys)-1)}-holeset
 def v(i,j,k):
  key=(i,j,k)
  if key not in indices:indices[key]=len(vs);vs.append(origin+ex*xs[i]+up*ys[j]+normal*(k*depth))
  return indices[key]
 for i,j in filled:
  q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)];fs.extend([tuple(v(x,y,0) for x,y in q[::-1]),tuple(v(x,y,1) for x,y in q)])
  for e,nb in enumerate([(i,j-1),(i+1,j),(i,j+1),(i-1,j)]):
   if nb not in filled:
    x,y=q[e];xx,yy=q[(e+1)%4];fs.append((v(x,y,0),v(xx,yy,0),v(xx,yy,1),v(x,y,1)))
 ob=mesh(name,vs,fs,wood,'through_perforated_timber_face_candidate');centers=[origin+ex*(margin+(i+.5)*pitchx)+up*(margin+(j+.5)*pitchy) for i,j in [(0,0),(7,6),(14,12)]];perforated.append(dict(name=name,hole_count=len(holeset),sample_centers=[list(p) for p in centers],normal=list(normal),thickness=depth));assert len(holeset)==nx*ny
def wall_grid(label,a,b,zs,count,normal,rule):
 a=point(*a);b=point(*b)
 for col in range(count):
  p=a+(b-a)*col/count;q=a+(b-a)*(col+1)/count
  for row,(z0,z1) in enumerate(zip(zs,zs[1:])):panel(f'R21_{label}_{col:02d}_{row:02d}',p,q,z0,z1,normal,rule(col,row))
ex=(point(465,440)-point(464,440)).normalized();ey=(point(464,441)-point(464,440)).normalized();H=P['ceiling_bottom_z'];zs=[LOW,LOW+1,LOW+2,LOW+3,LOW+4,H]
# Long side panels. Only rear fields use the hole motif; exact repeat is candidate.
wall_grid('SIDE_L',(464.5,421),(464.5,530),zs,14,ex,lambda c,r:c>=10 and r in [2,3])
wall_grid('SIDE_R',(580.5,421),(580.5,530),zs,14,-ex,lambda c,r:c>=10 and r in [2,3])
# Rear booth: six columns visible; central two middle modules replaced by glass.
cols=[494,503,512,523,534,543,552];levels=[LOW+1.92,LOW+2.75,LOW+3.65,H]
for col,(x0,x1) in enumerate(zip(cols,cols[1:])):
 for row,(z0,z1) in enumerate(zip(levels,levels[1:])):
  if row==1 and col in [2,3]:continue
  panel(f'R21_BOOTH_{col}_{row}',point(x0,505),point(x1,505),z0,z1,-ey,holes=row in [0,1])
# Stage back central face and both diagonal acoustic fields.
stage=[((488,414),(504,398)),((504,398),(540,398)),((540,398),(554,414))]
for side,(a,b) in enumerate(stage):
 pa=point(*a);pb=point(*b);normal=(pb-pa).normalized().cross(up)
 if normal.dot(point(522,426)-(pa+pb)/2)<0:normal=-normal
 wall_grid('STAGE_'+str(side),a,b,[LOW+.42,LOW+1.35,LOW+2.35,LOW+3.35,H],3 if side!=1 else 4,normal,lambda c,r:r in [1,2])
# Thin timber window surround; actual sash hardware remains unverified.
a=point(512,505,LOW+2.75);w=22*unit;h=.9
for label,u,v,ww,hh in [('L',0,0,.045,h),('R',w-.045,0,.045,h),('B',0,0,w,.045),('T',0,h-.045,w,.045)]:cuboid('R21_BOOTH_WINDOW_FRAME_'+label,a+ex*u+up*v-ey*.022,ex,up,-ey,ww,hh,.06,wood,'projection_window_surround_candidate')
config=dict(base_scene=prior['file'],source_ids=['071','072','073','076','LCB_auditorium3','LCB_aschman2'],single_panel_observed_holes=[15,13],joint_gap_m=.008,panel_thickness_m=.024,backing_status='dark appearance plane; physical system unknown',source_crop='references/R21_076_perforation_crop.png',limits=['Whole-room panel modules/heights are candidates. One visible grid does not establish all panel patterns.','No timber species, acoustic performance, hidden absorption or mounting specification inferred.','Existing wall envelope retained behind face layer; holes pass through face, not through structural wall.']);(B/'config/auditorium_panels.json').write_text(json.dumps(config,indent=2),encoding='utf8');bpy.data.texts.new('R21_SOURCE_AND_LIMITS').write(json.dumps(config,indent=2));bpy.context.scene['stage']='R21 auditorium timber/perforated face candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=prior['file'],closed_objects=made,perforated_panels=perforated,changed_inherited_objects=[],construction_acceptance=False);(B/'reports/R21_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
