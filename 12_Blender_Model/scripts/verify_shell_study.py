import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
p=B/'reports/P05_build_report.json';report=json.loads(p.read_text());path=R/report['file'];bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene
F=json.loads((B/'config/foundation.json').read_text(encoding='utf8'));C=F['calibration'];A=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (A[0][0]*u+A[0][1]*v+A[0][2]-293425,A[1][0]*u+A[1][1]*v+A[1][2]-5499960)
assert S.unit_settings.system=='METRIC' and S.unit_settings.scale_length==1
assert not any(min(o.scale)<0 for o in S.objects)
obs=[o for o in S.objects if o.name.startswith('P05_') and o.type=='MESH'];bad=[]
for ob in obs:
 for p in ob.data.polygons:
  if p.area<1e-8:bad.append([ob.name,p.index])
assert not bad,bad
deps=bpy.context.evaluated_depsgraph_get();ground=bpy.data.objects['P05_FLOOR_L00_GH'];evaluated=ground.evaluated_get(deps)
def hit(ob,p):return ob.ray_cast(Vector((*xy(p),1)),Vector((0,0,-1)),distance=2)[0]
assert not hit(evaluated,(656,367)),'Down-stair opening is filled'
assert hit(evaluated,(550,400)),'Adjacent ground floor missing'
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume());bm.free();return v
base=volume(ground.data);ev=evaluated.to_mesh();cut=volume(ev);evaluated.to_mesh_clear();assert base-cut>5
# All provisional roofs meet the authored edge levels, without interpreting them as surveyed.
roof=bpy.data.objects['P05_EAST_GLAZED_ROOF'];z=[v.co.z for v in roof.data.vertices];assert abs(z[0]-z[1])<1e-5 and abs(z[2]-z[3])<1e-5 and z[0]>z[2]
assert len(bpy.data.objects['P04_PAV_WALL_ENVELOPE'].data.polygons)==7,'Pavilion link bay still closed'
packed=sum(bool(i.packed_file) for i in bpy.data.images);assert packed>=20
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE' and i.type=='IMAGE')
floor_gates=json.loads((R/'11_Blender_Modelleme_Plani/is_paketleri.json').read_text(encoding='utf8'))
result=dict(status='pass',file=report['file'],fresh_process=True,unit_scale=1,mesh_objects=len(obs),degenerate_faces=bad,packed_images=packed,ground_volume_before_m3=base,ground_volume_after_m3=cut,down_stair_void_removed_volume_m3=base-cut,down_void_raycast_clear=True,adjacent_floor_raycast_hit=True,pavilion_link_bay_open=True,architectural_accuracy_verified=False,photographic_camera_match_verified=False)
(B/'reports/P05_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('P05_VERIFIED',result)
