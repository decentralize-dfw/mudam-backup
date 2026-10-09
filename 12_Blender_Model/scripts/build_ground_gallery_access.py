"""R28 source-supported detached entrance walls and gallery finish candidates."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/ground_gallery_access.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R28_ZEMIN_GALERI_GIRIS_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P16_GROUND_GALLERY_ACCESS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];wood=bpy.data.materials['R23_GALLERY_WOOD_FLOOR_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);vs=[tuple(p+up*z) for z in [z0,z1] for p in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='L00',zone_id='GROUND_GALLERIES',source_ids=','.join(P['source_ids']),confidence_xy='C diagram topology; thickness conditional',confidence_z='D candidate',confidence_detail='D unmeasured',status='conditional_source_ground_access',assumption_note='Flat ceiling 4.35m is a candidate; exhibition partitions omitted.').items():o[k]=v
 made.append(name);return o
for side in ['E','W']:
 prism('R28_'+side+'_CIRCULATION_FLOOR',[point(*p) for p in P['floor_connectors'][side]],-.2,0,stone,'ground_circulation_floor_connection_candidate')
 prism('R28_'+side+'_DETACHED_ENTRY_WALL',[point(*p) for p in P['spur_polygons_canonical'][side]],0,P['ceiling_z'],white,'source_detached_gallery_wall_candidate')
 prism('R28_'+side+'_FLAT_CEILING',[point(*p) for p in P['source_gallery_polygons'][side]],P['ceiling_z'],P['ceiling_z']+P['ceiling_thickness'],white,'gallery_suspended_ceiling_candidate')
 o=bpy.data.objects['P05_FLOOR_L00_'+side+'0'];o.data.materials.clear();o.data.materials.append(wood);changed.append(o.name)
 old=bpy.data.objects['P05_GALLERY_HALL_'+('EAST1' if side=='E' else 'WEST1')];old.hide_render=True;old.hide_set(True);changed.append(old.name)
 ob=old.copy();ob.data=old.data.copy();ob.name='R28_'+side+'_HIGH_GALLERY_WALL';root.objects.link(ob);ob.hide_render=False;ob.hide_set(False)
 for v in ob.data.vertices:
  if v.co.z<.1:v.co.z=P['ceiling_z']
 ob['element_id']=ob.name;ob['status']='conditional_high_wall_above_open_ground_entrances';ob['source_ids']='102,PDF2016';ob['assumption_note']='Inherited high wall retained above candidate gallery ceiling; ground passage is open per plan.'
bpy.context.scene['stage']='R28 source ground-gallery entries and ceiling candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R28_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R28_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,construction_acceptance=False),indent=2),encoding='utf8')
