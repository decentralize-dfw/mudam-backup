"""Read saved P06 file in a fresh Blender process; geometry checks are not survey validation."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
build=json.loads((B/'reports/P06_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/build['file']))
S=bpy.context.scene;objects=list(bpy.data.collections['P06_ROOF_REVISION_CONDITIONAL'].objects)
zero=[o.name for o in objects for p in o.data.polygons if p.area<1e-8]
inward=[o.name for o in objects if ('ROOF_FACE' in o.name or 'MAIN_CAP' in o.name) and any(p.normal.z<=0 for p in o.data.polygons)]
negative=[o.name for o in S.objects if min(o.scale)<0]
assert len(objects)==27 and not zero and not inward and not negative
assert S.unit_settings.system=='METRIC' and S.unit_settings.scale_length==1
assert all(bpy.data.objects[n].hide_render for n in build['superseded_objects'])
cam=bpy.data.objects['P06_PHOTO_119_CONDITIONAL'];assert cam.data.background_images[0].image.packed_file
assert abs(cam.rotation_euler.to_matrix().determinant()-1)<1e-5
roof=json.loads((B/'config/roof_revision.json').read_text())
# Adjacent roof/lantern/cap seam vertices must match exactly after saving.
seams=[]
for i in range(8):
 a=bpy.data.objects[f'P06_MAIN_ROOF_FACE_{i}'].data.vertices
 b=bpy.data.objects[f'P06_MAIN_LANTERN_{i}'].data.vertices
 c=bpy.data.objects[f'P06_MAIN_CAP_{i}'].data.vertices
 seams.extend([(a[3].co-b[0].co).length,(a[2].co-b[1].co).length,(b[3].co-c[0].co).length,(b[2].co-c[1].co).length])
assert max(seams)<1e-6
out=dict(file=build['file'],mesh_objects_checked=len(objects),zero_area_faces=zero,downward_roof_normals=inward,negative_scale_objects=negative,seam_checks=len(seams),max_seam_gap_m=max(seams),packed_camera_photo=True,blender_solver_projection_max_error_px=build['blender_projection_max_error_px'],metric_camera_acceptance=False,architectural_acceptance=False,remaining_gate='Photo119 wing tips mismatch; 116 not camera-fitted; section trace/date unresolved.')
(B/'reports/P06_verification.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
