from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R54_build_report.json').read_text());r['file']=json.loads((B/'reports/R55_build_report.json').read_text())['file'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=2000;S.render.resolution_y=1333;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R55_photo116.png');bpy.ops.render.render(write_still=True)
a,u,n=map(Vector,[r['origin'],r['axis'],r['inside']]);up=Vector((0,0,1));cd=bpy.data.cameras.new('R55_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;S.render.resolution_x=1600;S.render.resolution_y=1100;rows=[]
for name,tt,dd,zz,lens in [('context',29.8,-11,1.7,25),('detail',32.3,-4,-1.,30)]:
 eye=a+u*tt+n*dd+up*zz;target=a+u*33.8+n*.1+up*(-1.8 if name=='context' else -2.25);cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R55_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R55_{name}.png',eye=list(eye),target=list(target)))
(B/'reports/R55_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
