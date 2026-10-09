from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R27_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1400;S.render.resolution_y=933;S.render.resolution_percentage=100;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R27_photo116_context.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('R27_FRONT_DETAIL');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;axis=Vector(r['axis']);inside=Vector(r['inside']);origin=Vector(r['origin']);cam.location=origin+axis*25-inside*18+Vector((0,0,3));target=origin+axis*11+Vector((0,0,2.8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=42;S.render.filepath=str(B/'renders/qa/R27_reveal_detail.png');bpy.ops.render.render(write_still=True)
cam.location=origin+axis*10+inside*5+Vector((0,0,1.65));target=origin+axis*17+inside*1.25+Vector((0,0,2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=20;S.render.filepath=str(B/'renders/qa/R27_inside_windows.png');bpy.ops.render.render(write_still=True)
(B/'reports/R27_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,camera_116='inherited conditional fit; not metric validation'),indent=2),encoding='utf8')
