from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R47_build_report.json').read_text());Q=json.loads((B/'reports/R08_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R47_exterior.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('R47_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;center=Vector(Q['center_world'])
for key,eye,target,lens in [('lantern_detail',Vector((8,-11,20.5)),Vector((0,0,16)),42),('reading_interior',Vector((2,-2,Q['floor_z']+1.5)),Vector((0,0,12.8)),22)]:
 cam.location=center+eye;cam.rotation_euler=(center+target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R47_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R47_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_camera_match=False),indent=2),encoding='utf8')
