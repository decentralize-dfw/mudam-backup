"""R87 enclose the accepted PDF west return route; remove obsolete straight landing overshoot."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R86_PAVYON_CAM_KENAR_KAPANISI_v001.blend';out=B/'scenes/MUDAM_R87_KUCUK_BATI_GALERISI_KABUK_v003.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/west_glazed_stair.json').read_text());U=json.loads((B/'config/upper_gallery_room.json').read_text());UP=json.loads((B/'reports/R23_build_report.json').read_text())['upper_z'];head=UP+P['glass_head_clearance_m'];made=[];changed=[];up=Vector((0,0,1));root=bpy.data.collections.new('R87_PETITE_WEST_ENCLOSURE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p+up*z) for z in [z0,z1] for p in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1',zone_id='PETITE_WEST',source_ids='102,103,PDF2016,097',confidence_xy='C PDF portal / D schematic connection reconciliation',confidence_z='D inherited upper level and head',status='conditional_return_enclosure',assumption_note='PDF2016 small room inner wall path; 103 confirms Petite Galerie Ouest. Outer envelope closes existing stone stair walls. Source registration, hidden room partitions, slab and roof heights remain conditional.').items():ob[k]=v
 made.append(name);return ob
def uvrect(name,u0,u1,v0,v1,z0,z1,mat,kind):return prism(name,[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)],z0,z1,mat,kind)

TOP=13.923118
# Existing exterior stone walls define the volume behind the cafe and inside the west stair.
# No hidden technical subdivisions or furnishings are inferred.
for name,z0,z1 in [('BASE_FLOOR',-.2,0),('UPPER_FLOOR',UP-.2,UP),('OPAQUE_ROOF',TOP-.2,TOP)]:
 uvrect('R87_'+name,1120,1252,452,578,z0,z1,stone,'petite_outer_envelope_'+name.lower())
# Connect the PDF doorway to the existing R23 return passage; keep its gallery portal route.
old=bpy.data.objects['R85_RETURN_INNER_WALL'];old.hide_render=True;old.hide_set(True);changed.append(old.name)
uvrect('R87_RETURN_INNER_RETAINED',1203.26,1252,452,455.57,UP,head+.15,stone,'retained_return_boundary')
uvrect('R87_VOLUME_FRONT_LOW',1120,1252,452,455.57,0,UP,stone,'outer_volume_boundary_candidate')
uvrect('R87_VOLUME_FRONT_HIGH',1120,1252,452,455.57,head+.15,TOP,stone,'outer_volume_boundary_candidate')
uvrect('R87_VOLUME_FRONT_END',1120,1177,452,455.57,UP,head+.15,stone,'outer_volume_boundary_candidate')
uvrect('R87_ACCESS_HEAD',1177,1203.26,452,455.57,UP+2.6,head+.15,white,'connection_opening_head_candidate')
uvrect('R87_LANDING_SIDE_LOW',1248.43,1252,452,502.5,0,UP,stone,'opaque_stair_backing_candidate')
uvrect('R87_LANDING_SIDE_HIGH',1248.43,1252,452,502.5,head+.15,TOP,stone,'opaque_stair_backing_candidate')
# Inner limits measured from the archived vector path, not the offset visitor fill.
# The actual 2016 wall has a broad return; thickness here is the inherited envelope candidate.
th=3.57
for name,u0,u1,v0,v1 in [('ROOM_BACK',1164.18,1221.07,542.79,542.79+th),('ROOM_END',1221.07,1221.07+th,496.3,542.79+th),('ROOM_SIDE',1164.18-th,1164.18,496.3,542.79+th),('ROOM_FRONT_LEFT',1164.18-th,1171.25,496.3-th,496.3),('ROOM_FRONT_RIGHT',1203.26,1221.07+th,496.3-th,496.3)]:
 uvrect('R87_'+name,u0,u1,v0,v1,UP,TOP-.2,white,'pdf_petite_room_wall_candidate')
uvrect('R87_ROOM_DOOR_HEAD',1171.25,1203.26,496.3-th,496.3,UP+2.6,TOP-.2,white,'pdf_petite_opening_head_candidate')
# The legacy ground envelope crosses the source upper doorway. Cut only its upper passage.
cut=uvrect('R87_TEMP_PORTAL_CUT',1171.25,1203.26,452,496.3,UP,UP+2.6,white,'temporary_boolean')
legacy=bpy.data.objects['P05_GALLERY_HALL_WEST2'];bpy.context.view_layer.objects.active=legacy
mod=legacy.modifiers.new('R87_SOURCE_UPPER_PASSAGE','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
made.remove(cut.name);bpy.data.objects.remove(cut,do_unlink=True);changed.append(legacy.name)
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,hidden_superseded=['R85_RETURN_INNER_WALL'],upper_z=UP,roof_z=TOP,room_uv=[[1164.18,496.3],[1221.07,496.3],[1221.07,542.79],[1164.18,542.79]],outer_uv=[[1120,452],[1252,452],[1252,578],[1120,578]],route_uv=[[1188,440],[1188,465],[1188,488],[1188,515]],construction_acceptance=False,limits=['Missing Petite Galerie Ouest room is confirmed by103 and PDF2016; PDF interior path takes precedence over the visitor colored fill.','Outer floor/roof use the existing102/103-based stone volume behind cafe and within west stair; concealed technical subdivisions unknown and omitted.','PDF and visitor stair footprints differ; exterior walls retained and exact full-plan scale reconciliation remains open.','Floor4.859m, roof13.923m,0.2m slabs and2.6m doorway heads are inherited candidates, not measured.','Roof is an opaque envelope supported by097; roof build-up, drainage and local slope are unresolved.'])
bpy.context.scene['stage']='R87 Petite Galerie Ouest missing architectural enclosure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R87_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R87_build_report.json').write_text(json.dumps(r,indent=2));print('R87',len(made),'new',len(changed),'superseded')
