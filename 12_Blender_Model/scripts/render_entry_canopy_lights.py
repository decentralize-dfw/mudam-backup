from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R61_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=1100;cd=bpy.data.cameras.new('R61_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[];c=Vector(r['fixtures'][1]['center'])
for name,eye,target,lens in [('canopy',(30,34,1.65),(35,40,11),20),('fixture',tuple(c+Vector((.45,-.6,-.7))),tuple(c),60),('group',(30,35,7.5),(32,38,11.5),23)]:
 cam.location=Vector(eye);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R61_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R61_{name}.png',eye=eye,target=target))
(B/'reports/R61_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
