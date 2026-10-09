"""R99 restore the short gallery entry boundary drawn independently in102 and2016."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());base='MUDAM_R98_UST_KOPRU_DUVAR_SINIRI_v001.blend';out=B/'scenes/MUDAM_R99_BATI_GALERI_GIRIS_DUVARI_v002.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
poly=P['spur_polygons_canonical']['W'];ps=[pt(*p) for p in poly];n=len(ps);lookup={tuple(p):i for i,p in enumerate(ps)}
def ix(v):return v if isinstance(v,int) else lookup[tuple(v)]
tri=tessellate_polygon([ps]);fs=[tuple(ix(v) for v in reversed(t)) for t in tri]+[tuple(ix(v)+n for v in t) for t in tri]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];name='R99_W_GROUND_GALLERY_ENTRY_WALL';me=bpy.data.meshes.new(name);me.from_pydata([p+Vector((0,0,z)) for z in [0,P['ceiling_z']] for p in ps],[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.data.collections['90_UNCERTAIN_OR_PROXY'].objects.link(o);me.materials.append(bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'])
for k,v in dict(element_id=name,element_type='source_ground_gallery_entry_boundary',level_id='L00',zone_id='GROUND_GALLERY_W',source_ids='102,PDF2016',status='source_plan_boundary_candidate_height',assumption_note='Short detached wall follows102 and2016 plan. Distinct from the long cafe diagonal removed at user request. Ground ceiling4.35m and drawn wall thickness remain unmeasured. End passages remain open.').items():o[k]=v
probes=[]
for t in [.1,.25,.5,.75,.9]:
 a=pt(*poly[2]).lerp(pt(*poly[3]),t);b=pt(*poly[7]).lerp(pt(*poly[6]),t);normal=(b-a).normalized()
 for z in [.4,1.6,3.9]:p=a.lerp(b,.5);p.z=z;probes.append(dict(point=list(p),normal=list(normal)))
legacy=bpy.data.objects['R87_VOLUME_FRONT_LOW'];legacy.hide_render=True;legacy.hide_set(True);legacy['R99_note']='Upper small-room boundary has no corresponding ground wall in102; its ground extension obstructed the north gallery route.'
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=base,closed_objects=[name],changed_inherited_objects=['R87_VOLUME_FRONT_LOW'],probes=probes,source_polygon=poly,construction_acceptance=False,limits=['Height and thickness inherited candidates; wall footprint appears in102 and2016, not a new invented room.','North and south source entry routes remain open; long cafe diagonal remains open at ground floor.','Second marked stair-side gallery junction and remaining upper-floor regions still require source/camera matched review.']);bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R99 west gallery source boundary restored';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R99_build_report.json').write_text(json.dumps(r,indent=2));print('R99 saved')
