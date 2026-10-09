"""R85 enclose the accepted PDF west return route; remove obsolete straight landing overshoot."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R84_GIRIS_ALT_CAM_KAPANISI_v001.blend';out=B/'scenes/MUDAM_R85_BATI_UST_SAHANLIK_KABUK_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/west_glazed_stair.json').read_text());U=json.loads((B/'config/upper_gallery_room.json').read_text());UP=json.loads((B/'reports/R23_build_report.json').read_text())['upper_z'];head=UP+P['glass_head_clearance_m'];made=[];changed=[];up=Vector((0,0,1));root=bpy.data.collections.new('R85_WEST_UPPER_RETURN_ENCLOSURE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p+up*z) for z in [z0,z1] for p in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1',zone_id='WEST_STAIR_RETURN',source_ids='103,PDF2016,097',confidence_xy='C PDF portal / D schematic connection reconciliation',confidence_z='D inherited upper level and head',status='conditional_return_enclosure',assumption_note='R23 PDF return route retained; obsolete R14 straight floor removed. Roof/side closure follows existing landing and return boundaries; widths and materials require stronger references.').items():ob[k]=v
 made.append(name);return ob
def uvrect(name,u0,u1,v0,v1,z0,z1,mat,kind):return prism(name,[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)],z0,z1,mat,kind)
old=bpy.data.objects['R14_UPPER_LANDING'];old.hide_render=True;old.hide_set(True);changed.append(old.name)
uvrect('R85_UPPER_LANDING_FLOOR',1252,1275,452,502.5,UP-.2,UP,stone,'source_upper_landing_floor')
# Existing R23 floor already turns to the PDF doorway; cover only its two existing footprints.
for i,poly in enumerate(U['west_return_uv']):prism(f'R85_RETURN_CEILING_{i}',[point(u,v) for u,v in poly],head,head+.15,white,'return_passage_ceiling_candidate')
# Close the omitted inside edge of the landing, connecting flight B to the return wall.
uvrect('R85_LANDING_INNER_WALL',1252-3.57,1252,452,502.5,UP,head+.15,stone,'landing_inner_wall_candidate')
# Narrow edge walls lie outside the retained circulation width; no wall across the PDF doorway.
uvrect('R85_RETURN_INNER_WALL',1177,1252,452,455.57,UP,head+.15,stone,'return_boundary_wall_candidate')
uvrect('R85_RETURN_END_WALL',1275,1278.57,424.5,452,UP,head+.15,stone,'return_outer_end_wall_candidate')
uvrect('R85_RETURN_FAR_WALL',1173.43,1177,424.5,452,UP,head+.15,stone,'return_far_wall_candidate')
# Close only the short extension beyond the existing upper-gallery boundary endpoint.
uvrect('R85_RETURN_OUTER_TIP',1266,1275,420.93,424.5,UP,head+.15,stone,'return_outer_tip_wall_candidate')
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,hidden_superseded=changed,landing_uv=[[1252,452],[1275,452],[1275,502.5],[1252,502.5]],return_uv=U['west_return_uv'],upper_z=UP,head_z=head,construction_acceptance=False,limits=['R23 PDF portal and return path retained; R14 straight floor extending into outside/closed room superseded.','Official103 and PDF inner room boundaries differ; no independent full upper-plan re-registration claimed.','097 supports enclosed upper connection with opaque end; detailed exact wall/glass segmentation unresolved.','Existing floor levels, wall thickness and3.2m head remain candidates. Roof silhouette and stair flights unchanged.'])
bpy.context.scene['stage']='R85 west upper return enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R85_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R85_build_report.json').write_text(json.dumps(r,indent=2));print('R85',len(made),'new',len(changed),'superseded')
