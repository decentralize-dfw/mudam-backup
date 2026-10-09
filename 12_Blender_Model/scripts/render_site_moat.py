from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R35_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R35_exterior.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('R35_SITE_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=24
for key,eye,target in [('moat_from_bridge',(48,33,1.65),(43,-5,-3.2)),('site_oblique',(88,87,38),(18,23,1)),('moat_inside',(46,4,-3.8),(39,32,-1.6))]:
 cam.location=Vector(eye);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R35_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R35_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_pose=False,lighting_calibration=False),indent=2),encoding='utf8')
