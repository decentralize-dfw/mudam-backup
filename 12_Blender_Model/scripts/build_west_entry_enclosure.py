"""R82 close the omitted ground-level segment of the existing west glazed stair."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R81_ALT_FUAYE_YAN_KABUK_v001.blend';out=B/'scenes/MUDAM_R82_BATI_MERDIVEN_GIRIS_KABUK_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/west_glazed_stair.json').read_text());Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};up=Vector((0,0,1));made=[];root=bpy.data.collections.new('R82_WEST_STAIR_ENTRY_ENCLOSURE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def solid(name,ps,n,depth,mat,kind):
 N=len(ps);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in ps]+[tuple(p-n*depth) for p in ps],[],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='L00',zone_id='WEST_GLAZED_STAIR',source_ids='102,066,097',confidence_xy='C source102 stair entry edges',confidence_z='D existing R14 head and datum',status='conditional_source_enclosure',assumption_note='Only missing ground entry enclosure added. Existing height/profile candidates retained; no panel module count or as-built dimensions claimed.').items():ob[k]=v
 made.append(name);return ob
u0=1120.;u1=P['first_u'][0];v0,v1=P['first_v'];h=P['glass_head_clearance_m'];ev=(point(0,1)-point(0,0)).normalized();glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];panes=[([point(u0,v1,0),point(u1,v1,0),point(u1,v1,h),point(u0,v1,h)],ev),([point(u0,v0,h),point(u1,v0,h),point(u1,v1,h),point(u0,v1,h)],up)];keys=set();frames=[]
for i,(ps,n) in enumerate(panes):
 solid(f'R82_ENTRY_GLASS_{i}',ps,n,P['glass_thickness_m'],glass,'entry_glass_enclosure_candidate')
 for a,b in zip(ps,ps[1:]+ps[:1]):
  key=tuple(sorted(tuple(round(x,5) for x in p) for p in [a,b]))
  if key in keys:continue
  keys.add(key);side=n.cross((b-a).normalized())*P['frame_width_m']/2;name=f'R82_ENTRY_FRAME_{len(frames):02d}';solid(name,[a-side,b-side,b+side,a+side],n,P['frame_depth_m'],metal,'entry_glass_edge_candidate');frames.append(name)
solid('R82_ENTRY_INNER_WALL',[point(u0,v0,0),point(u1,v0,0),point(u1,v0,Z['Z_ROOF_MAIN_BASE']),point(u0,v0,Z['Z_ROOF_MAIN_BASE'])],ev,P['wall_display_thickness_m'],stone,'entry_inner_stone_wall_candidate')
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],entry_u=[u0,u1],entry_v=[v0,v1],entry_head=h,source_ids=['102','066','097'],construction_acceptance=False,limits=['102 has the flat entry footprint before first riser;097 shows glazing continuing across the bottom landing.','Existing R14 ground floor retained. Roof at inherited3.2m head, source height not measured.','Two unsegmented glass surfaces provide enclosure; final pane subdivisions and profiles deferred.'])
bpy.context.scene['stage']='R82 west stair ground entry enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R82_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R82_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R82',len(made),'parts')
