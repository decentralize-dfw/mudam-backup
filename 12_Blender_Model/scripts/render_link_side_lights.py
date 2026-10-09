from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R66_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=1100;cd=bpy.data.cameras.new('R66_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[];P=json.loads((B/'reports/R18_build_report.json').read_text())['portals'];center=lambda i:(Vector(P[i]['left'])+Vector(P[i]['right']))/2;Z=Vector((0,0,1));f=r['fixtures'][8];c=Vector(f['center']);inside=Vector(f['inside']);along=(center(7)-center(6)).normalized()
for name,eye,target,lens in [('link',center(7)+Z*1.65,center(0)+Z*2.3,25),('roof',center(6)+Z*2.2,center(3)+Z*4.1,25),('fixture',c+inside*.35+along*.2-Z*.35,c-Z*.06,55)]:
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R66_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R66_{name}.png',eye=list(eye),target=list(target)))
(B/'reports/R66_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
