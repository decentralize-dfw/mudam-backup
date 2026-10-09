from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R40_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R40_exterior.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('R40_WINDOW_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;a=Vector(r['origin']);ax=Vector(r['axis']);n=Vector(r['inside']);up=Vector((0,0,1))
for key,t,d,z,tt,tz,lens in [('moat_front',14,-18,0,13,-1,40),('window_detail',11,-5,-1.9,12.87,-2.15,30),('oblique_reveals',25,-7,-.4,17.97,-2,36)]:
 cam.location=a+ax*t+n*d+up*z;target=a+ax*tt+n*1.25+up*tz;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R40_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R40_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_pose=False,dimensions_accepted=False),indent=2),encoding='utf8')
