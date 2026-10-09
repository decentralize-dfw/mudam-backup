"""R20: photograph-supported 8x16 seating candidate, separate movable seat pans."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';prior=json.loads((B/'reports/R19_build_report.json').read_text());P=json.loads((B/'config/auditorium_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R20_ODITORYUM_KOLTUK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/prior['file']));root=bpy.data.collections.new('P16_AUDITORIUM_SEATING_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];s,dx,dy=C['basement_registration']['source_to_canonical'];unit=s*C['meters_per_canonical_pixel'];LOW=prior['lower_z']
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def material(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.25;return m
cloth=material('R20_TAN_UPHOLSTERY_CANDIDATE',(.28,.19,.115),.86);metal=material('R20_SEAT_BASE_DARK',(.012,.014,.015),.52)
def proto(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat);return me
def extrude(name,poly,axis,lo,hi,mat,warp=None):
 vs=[]
 for d in [lo,hi]:
  for a,b in poly:
   v=[0.,0.,0.];v[axis]=d;other=[i for i in range(3) if i!=axis];v[other[0]]=a;v[other[1]]=b
   if warp:v=warp(v)
   vs.append(v)
 N=len(poly);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];me=proto(name,vs,fs,mat)
 for face in me.polygons:
  if face.index>=2:face.use_smooth=True
 return me
def rounded(x0,x1,z0,z1,r,n=12):
 pts=[]
 for cx,cz,a in [(x1-r,z1-r,0),(x0+r,z1-r,90),(x0+r,z0+r,180),(x1-r,z0+r,270)]:
  for j in range(n+1):q=math.radians(a+90*j/n);pts.append((cx+r*math.cos(q),cz+r*math.sin(q)))
 return pts
back=extrude('R20_BACK_MESH',rounded(-.245,.245,.36,1.00,.145),1,.18,.30,cloth,lambda v:[v[0],v[1]+.11*(v[2]-.36)/.64,v[2]])
armL=extrude('R20_ARM_L_MESH',rounded(-.31,.36,.11,.72,.11),0,-.283,-.223,cloth)
armR=extrude('R20_ARM_R_MESH',rounded(-.31,.36,.11,.72,.11),0,.223,.283,cloth)
angle=math.radians(75)
def fold(v):
 x,y,z=v;d=y+.24;return [x,.12-d*math.cos(angle)+(z-.44)*math.sin(angle),.36+d*math.sin(angle)+(z-.44)*math.cos(angle)]
seat=extrude('R20_FOLDED_PAN_MESH',rounded(-.218,.218,-.24,.19,.09),2,.40,.48,cloth,fold)
def cube(name,x0,x1,y0,y1,z0,z1):return extrude(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],2,z0,z1,metal)
footL=cube('R20_FOOT_L_MESH',-.27,-.23,-.30,.35,0,.06);footR=cube('R20_FOOT_R_MESH',.23,.27,-.30,.35,0,.06);support=cube('R20_PIVOT_SUPPORT_MESH',-.19,.19,.12,.20,.06,.36)
parts=[('BACK',back),('PAN',seat),('ARM_L',armL),('ARM_R',armR),('FOOT_L',footL),('FOOT_R',footR),('SUPPORT',support)];ex=(point(465,440)-point(464,440)).normalized();ey=(point(464,441)-point(464,440)).normalized();ez=Vector((0,0,1));basis=Matrix((ex,ey,ez)).transposed().to_4x4();chairs=[]
for row in range(8):
 for col in range(16):
  x=487+(col+.5)*(558-487)/16;y=441+(row+.52)*8;z=LOW+(row+1)*P['row_rise_m'];origin=point(x,y,z);ident=f'R20_SEAT_{row+1:02d}_{col+1:02d}';chair=[]
  for label,me in parts:
   name=ident+'_'+label;ob=bpy.data.objects.new(name,me);root.objects.link(ob);ob.matrix_world=basis.copy();ob.location=origin
   for k,v in dict(element_id=name,element_type='auditorium_seat_'+label.lower(),zone_id='AUDITORIUM',level_id='LM1',source_ids='071,LCB_auditorium3,LCB_aschman2,104',confidence_xy='C row envelope; D exact centers',confidence_z='D candidate tier and seat dimensions',confidence_detail='D photo-based generic profile; no manufacturer geometry',status='conditional_seating_8x16',assumption_note='Eight rows and 16 rear seats visible. Occluded seat counts, exact pitch and folded angle not individually verified.',row_index=row+1,seat_index=col+1).items():ob[k]=v
   if label not in ['FOOT_L','FOOT_R','SUPPORT']:
    mod=ob.modifiers.new('soft upholstered edge candidate','BEVEL');mod.width=.009;mod.segments=2;mod.affect='EDGES'
   made.append(name);chair.append(name)
  chairs.append(dict(id=ident,row=row+1,column=col+1,native_xy=[x,y],floor_z=z,objects=chair))
config=dict(row_count=8,seats_per_row=16,total=128,pitch_m=71*unit/16,seat_height_m=1.,folded_pan_degrees=75,source_ids=['071','104','LCB_auditorium3','LCB_aschman2'],base_scene=prior['file'],limits=['Not every occluded seat separately counted. 8x16 arrangement matches visible rows, rear row count and LCB capacity table.','Seat dimensions, exact curvature, hinges and attachment details remain adjustable photo candidates.','No safety, accessibility or egress compliance assertion.']);(B/'config/auditorium_seats.json').write_text(json.dumps(config,indent=2),encoding='utf8');bpy.data.texts.new('R20_SOURCE_AND_LIMITS').write(json.dumps(config,indent=2));bpy.context.scene['stage']='R20 auditorium seating candidate; wall panels and details remain';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=prior['file'],closed_objects=made,chairs=chairs,changed_inherited_objects=[],construction_acceptance=False);(B/'reports/R20_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
