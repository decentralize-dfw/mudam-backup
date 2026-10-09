from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R62_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=1100;cd=bpy.data.cameras.new('R62_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[]
for name,eye,target,lens in [('outside',(42,58,2),(37.7,44,1),27),('column',(33,36,1.65),(38,42,2.1),23),('park',(68,67,1.65),(30,30,5),24)]:
 cam.location=Vector(eye);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R62_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R62_{name}.png',eye=eye,target=target))
(B/'reports/R62_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
