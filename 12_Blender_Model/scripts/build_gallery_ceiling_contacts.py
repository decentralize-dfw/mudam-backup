"""R100 reconcile existing suspended-ceiling edges with source-traced entry walls."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());base='MUDAM_R99_BATI_GALERI_GIRIS_DUVARI_v002.blend';out=B/'scenes/MUDAM_R100_GALERI_TAVAN_DUVAR_TEMASI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
def pt(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
mapping={'E':{4:4,5:5,6:6,7:7,8:0},'W':{3:5,4:6,5:7,6:0}};records=[];changed=[]
for side,indices in mapping.items():
 ob=bpy.data.objects[f'R28_{side}_FLAT_CEILING'];ob.data=ob.data.copy();inv=ob.matrix_world.inverted();floor=P['source_gallery_polygons'][side];wall=P['spur_polygons_canonical'][side]
 for old_index,new_index in indices.items():
  a=pt(floor[old_index]);b=pt(wall[new_index]);matched=[]
  for v in ob.data.vertices:
   q=ob.matrix_world@v.co
   if Vector((q.x-a.x,q.y-a.y,0)).length<.0001:v.co=inv@Vector((b.x,b.y,q.z));matched.append(v.index)
  assert matched,(ob.name,old_index)
  records.append(dict(object=ob.name,old_xy=floor[old_index],new_xy=wall[new_index],delta_m=(a-b).length,vertices=matched))
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['R100_note']='Ceiling inner edge locally meets the corresponding source-traced gallery entry wall. Existing0/4.35m entry opening heights preserved. Small inconsistent traces reconciled; not surveyed.';changed.append(ob.name)
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=base,closed_objects=changed,changed_inherited_objects=changed,records=records,construction_acceptance=False,limits=['Only existing ceiling-edge coordinates reconciled to existing source wall faces; ceiling height4.35m and thickness150mm stay conditional.','True passage ends and tall stair-side opening remain open. No invented wall closes the circulation route.','Upper-floor room relationships and roof/frame detailing not accepted by this local repair.']);bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R100 local gallery ceiling to source wall contact';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R100_build_report.json').write_text(json.dumps(r,indent=2));print('R100',len(records),'edge stations; max',max(x['delta_m'] for x in records))
