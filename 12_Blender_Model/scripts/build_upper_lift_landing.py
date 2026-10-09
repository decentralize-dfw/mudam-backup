"""R30 upper lift landing; exact shaft continuity is deliberately unresolved."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/upper_lift_landing.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R30_UST_ASANSOR_SAHANLIK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P12_UPPER_LIFT_LANDING_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];up=Vector((0,0,1));stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials.new('R30_BRUSHED_METAL_CANDIDATE');metal.use_nodes=True;n=metal.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.3,.31,.32,1);n.inputs['Metallic'].default_value=.85;n.inputs['Roughness'].default_value=.3;dark=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1',zone_id='UPPER_LIFT_LANDING',source_ids=','.join(P['source_ids']),confidence_xy='C PDF jamb footprint',confidence_z='D unmeasured',confidence_detail='D photo family transfer',status='conditional_upper_lift_landing',assumption_note='077 floor unknown; family transfer only. No continuous lift shaft or mechanical system implied.').items():o[k]=v
 made.append(name);return o
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);return mesh(name,[p+up*z for z in [z0,z1] for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
def box(name,x0,x1,y0,y1,z0,z1,mat=stone,kind='landing_stone_envelope_candidate'):
 return prism(name,[point(x,y) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],z0,z1,mat,kind)
TOP=UP+P['landing_clear_height_candidate_m'];HEAD=UP+P['door_clear_height_candidate_m'];x0,x1=P['door_span_canonical'];y=P['door_plane_y'];scale=C['meters_per_canonical_pixel'];th=P['wall_display_thickness_m']/scale
box('R30_LEFT_JAMB',644.74,x0,529.52,y+.2,UP,TOP);box('R30_RIGHT_JAMB',x1,685.56,529.52,y+.2,UP,TOP);box('R30_STONE_HEAD',x0,x1,529.52,y+.2,HEAD,TOP)
box('R30_LANDING_WEST',644.74-th,644.74,y,558.5,UP,TOP);box('R30_LANDING_EAST',685.56,685.56+th,y,558.5,UP,TOP)
poly=[point(*p) for p in P['landing_polygon']];prism('R30_LANDING_FLOOR',poly,UP-.2,UP,stone,'landing_floor_connection_candidate');prism('R30_LANDING_CEILING',poly,TOP,TOP+.2,stone,'landing_ceiling_candidate')
# Four closed telescopic-looking panels, all closed and independently editable.
fw=.04/scale;depth=P['metal_thickness_m']/scale;gap=P['leaf_seam_m']/scale;left=x0+fw;right=x1-fw;bottom=UP+.025;top=HEAD-.04;panel_width=(right-left)/4
for i in range(4):box('R30_DOOR_LEAF_'+str(i+1),left+i*panel_width+gap/2,left+(i+1)*panel_width-gap/2,y-depth,y,bottom,top,metal,'closed_metal_lift_leaf_candidate')
box('R30_FRAME_L',x0,left,y-.08/scale,y+.015/scale,UP,HEAD,metal,'lift_frame_candidate');box('R30_FRAME_R',right,x1,y-.08/scale,y+.015/scale,UP,HEAD,metal,'lift_frame_candidate');box('R30_FRAME_HEAD',x0,x1,y-.08/scale,y+.015/scale,top,HEAD,metal,'lift_frame_candidate');box('R30_THRESHOLD',x0,x1,y-.12/scale,y+.16/scale,UP,UP+.025,metal,'lift_threshold_candidate')
# Dark backing prevents the modelling seam from showing through an unmodelled shaft.
box('R30_DOOR_BACKING',x0,x1,y-.06/scale,y-.05/scale,UP,HEAD,dark,'door_seam_backing_candidate')
ex=(point(1,0)-point(0,0)).normalized();ey=(point(0,1)-point(0,0)).normalized()
def disc(name,x,z,radius,depth,mat):
 center=point(x,y+.025/scale,z);ring=[ex*(radius*math.cos(i*math.tau/32))+up*(radius*math.sin(i*math.tau/32)) for i in range(32)];return mesh(name,[center+q+ey*d for d in [0,depth] for q in ring],[tuple(range(31,-1,-1)),tuple(range(32,64))]+[(i,(i+1)%32,(i+1)%32+32,i+32) for i in range(32)],mat,'round_lift_control_appearance_candidate')
disc('R30_CALL_PLATE',652,UP+1.1,.055,.006,metal);disc('R30_CALL_BUTTON',652,UP+1.115,.015,.012,metal)
for i,z in enumerate([UP+2.02,UP+2.15]):disc('R30_INDICATOR_DISC_'+str(i),652,z,.027,.004,metal)
bpy.context.scene['stage']='R30 upper lift landing and closed door family candidate';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R30_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R30_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],upper_z=UP,door_head=HEAD,landing_top=TOP,construction_acceptance=False),indent=2),encoding='utf8')
