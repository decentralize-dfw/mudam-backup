"""R15 front gallery reveal candidate. Photo-derived dimensions remain conditional."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/gallery_front_reveals.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R15_GALERI_CEPHE_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P08_GALLERY_FRONT_REVEALS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];panels=[]
def xy(p):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
a,b=map(xy,P['facade_endpoints']);axis=(b-a).normalized();up=Vector((0,0,1));inside=axis.cross(up);length=(b-a).length
# Determine inward direction from the gallery plan, not winding assumptions.
if inside.dot(xy([400,500])-(a+b)/2)<0:inside=-inside
def pt(t,d,z):return a+axis*t+inside*d+up*z
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE']
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='EAST_GALLERY_FRONT',level_id='L00',source_ids=','.join(P['source_ids']),confidence_xy='D conditional photo camera on C plan plane',confidence_z='D photo-derived',confidence_detail='D visual envelope',status='conditional_not_surveyed',parameter_ids='gallery_front_reveals.json',assumption_note='Five bays with two glazing positions; all depths and member dimensions remain candidates.').items():ob[k]=v
 made.append(name);return ob
fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,t0,t1,d0,d1,z0,z1,mat=stone,kind='stone_wall_envelope'):
 return mesh(name,[pt(t,d,z) for z in [z0,z1] for t,d in [(t0,d0),(t1,d0),(t1,d1),(t0,d1)]],fs,mat,kind)
depth=P['recess_depth_m'];th=P['wall_depth_m'];head=P['head_z'];sill=P['sill_z'];sp=P['splay_m'];width=P['bay_width_m'];old=bpy.data.objects['P05_FRONT_1'];old.hide_render=True;old.hide_set(True)
# Replace the schematic surface with separate closed cells around openings.
cursor=0;openings=[]
box('R15_CONTINUOUS_HEAD',0,length,0,th,head,Z['Z_ROOF_MAIN_BASE'])
for i,(start,typ) in enumerate(zip(P['bay_starts_m'],P['types'])):
 end=start+width;bot=sill;prefix=f'R15_BAY_{i+1}'
 if start>cursor:box(prefix+'_PIER_BACK',cursor,start,depth,th,Z['Z_LM1_FINISH'],head)
 # 003/005 show the stone return leaning back at its lower end. The
 # previous vertical front jamb was rejected by the photo comparison.
 fin=.30;bottom=P['blind_bottom_z'];outline=[(0,head),(depth,bottom),(th,bottom),(th,head)]
 mesh(prefix+'_SLOPING_FIN',[pt(t,d,z) for t in [start-fin,start] for d,z in outline],fs,stone,'sloping_stone_return_candidate')
 if typ=='blind':box(prefix+'_BLIND_BACK',start,end,depth,th,Z['Z_LM1_FINISH'],head)
 else:
  box(prefix+'_BASE',start,end,depth,th,Z['Z_LM1_FINISH'],bot)
  fw=P['frame_width_m'];fz=bot;fd=P['frame_depth_m'];left=start
  for lab,l,r,z0,z1 in [('L',left,left+fw,fz,head),('R',end-fw,end,fz,head),('B',left,end,fz,fz+fw),('T',left,end,head-fw,head)]:box(prefix+'_FRAME_'+lab,l,r,depth-fd,depth,z0,z1,metal,'fixed_window_frame_candidate')
  ob=box(prefix+'_GLASS',left+fw,end-fw,depth-P['glass_thickness_m'],depth,fz+fw,head-fw,glass,'flat_fixed_window_candidate');panels.append(ob.name)
 openings.append(dict(index=i+1,type=typ,start=start,end=end,bottom=bot,head=head,glass_center=list(pt((start+end)/2,depth,(bot+head)/2))));cursor=end
box('R15_END_PIER',cursor,length,depth,th,Z['Z_LM1_FINISH'],head)
bpy.context.scene['stage']='R15 conditional gallery facade reveals';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R15_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,openings=openings,origin=list(a),axis=list(axis),inside=list(inside),length=length,changed_inherited_objects=[old.name],hidden_superseded=[old.name],construction_acceptance=False);(B/'reports/R15_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
