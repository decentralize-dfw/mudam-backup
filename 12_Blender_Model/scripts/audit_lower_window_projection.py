from pathlib import Path
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R54_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;S.render.resolution_x=2000;S.render.resolution_y=1333;cam=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];source=json.loads((B/'reports/R54_lower_window_registration_study.json').read_text())['osm_glass_plane_study'][1]['windows'];rows=[]
for w,src in zip(r['windows'],source):
 p=Vector(w['glass_center']);p.z=w['head'];q=world_to_camera_view(S,cam,p);pixel=[q.x*2000,(1-q.y)*1333];err=math.dist(pixel,src['top']);rows.append(dict(window=w['id'],projected_head_px=pixel,manual_head_px=src['top'],error_px=err))
report=dict(file=r['file'],camera='P07_PHOTO_116_CONDITIONAL',landmarks=rows,rmse_px=math.sqrt(sum(q['error_px']**2 for q in rows)/len(rows)),independent_holdout=False,status='in_sample_conditional_projection_check_not_metric_accuracy',limits=['The same source/camera constrains candidate centers. Low residual is not independent validation.','Rounded equal spacing/common head height differ from raw wall-plane intersections; source reading and OSM errors are unbounded here.']);(B/'reports/R54_projection_audit.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
