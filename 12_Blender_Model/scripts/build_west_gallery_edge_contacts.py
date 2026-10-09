"""R105 bridge the mismatched schematic floor/ceiling edge to its existing wall."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];base=json.loads((B/'reports/R104_build_report.json').read_text());out=B/'scenes/MUDAM_R105_BATI_GALERI_DOSEME_TAVAN_TEMASI_v002.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']))
M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def canonical(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2]
 return [((M[1][1]*a-M[0][1]*b)/det-off[0])/k,((-M[1][0]*a+M[0][0]*b)/det-off[1])/k]
def pt(x,y,z=0):
 a=k*x+off[0];b=k*y+off[1]
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
wall=bpy.data.objects['P05_GALLERY_HALL_WEST0'];ps=[canonical(wall.matrix_world@v.co) for v in wall.data.vertices];wall_x=max(p[0] for p in ps);ys=[min(p[1] for p in ps),max(p[1] for p in ps)]
P=json.loads((B/'config/ground_gallery_access.json').read_text());edge_x=P['source_gallery_polygons']['W'][7][0];scale=(pt(1,0)-pt(0,0)).length;overlap=.005/scale
assert .19<(edge_x-wall_x)*scale<.21
poly=[[wall_x-overlap,ys[0]],[edge_x+overlap,ys[0]],[edge_x+overlap,ys[1]+overlap],[wall_x-overlap,ys[1]+overlap]]
root=bpy.data.collections.new('R105_GALLERY_EDGE_CONTACTS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];records=[]
for label,base_name in [('FLOOR','P05_FLOOR_L00_W0'),('CEILING','R28_W_FLAT_CEILING')]:
 ref=bpy.data.objects[base_name];zs=[(ref.matrix_world@v.co).z for v in ref.data.vertices];z0,z1=min(zs),max(zs);name='R105_W_GALLERY_'+label+'_EDGE';me=bpy.data.meshes.new(name);me.from_pydata([pt(x,y,z) for z in [z0,z1] for x,y in poly],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(ref.data.materials[0])
 for key,value in dict(element_id=name,element_type='gallery_'+label.lower()+'_wall_contact_candidate',level_id='L00',zone_id='GROUND_GALLERY_W',source_ids='102,PDF2016,056',status='conditional_existing_boundary_reconciliation',assumption_note='Existing floor/ceiling and wall retained. Closes 199mm schematic-boundary mismatch only along existing wall. 5mm overlap buried inside existing solids; inherited levels, thickness and finish unmeasured.').items():ob[key]=value
 ref.data=ref.data.copy();bpy.context.view_layer.objects.active=ref;mod=ref.modifiers.new('R105 union source edge contact','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(ob,do_unlink=True);ref['R105_note']='Existing wall contact restored with local boolean union; source wall, portals and elevations unchanged.';made.append(ref.name);records.append(dict(name=ref.name,z_range=[z0,z1],material=ref.data.materials[0].name,adjoining=base_name))
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=made,changed_inherited_objects=made,wall=wall.name,wall_x=wall_x,old_edge_x=edge_x,y_range=ys,polygon_canonical=poly,gap_m=(edge_x-wall_x)*scale,overlap_m=.005,records=records,construction_acceptance=False,limits=['Visitor/source2016 circulation continuity supports contact; source056 shows general gallery floor/ceiling construction, not a surveyed pose of this west edge.','Only the existing west ground gallery boundary is bridged. No wall, opening or source height moved.','Floor/ceiling thickness, material and wall position remain inherited model candidates.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R105 west gallery floor and ceiling wall contacts';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R105_build_report.json').write_text(json.dumps(r,indent=2));print('R105',r['gap_m'],'m edge mismatch',made)
