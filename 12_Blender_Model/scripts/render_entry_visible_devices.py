from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R63_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1300;S.render.resolution_y=1500;cd=bpy.data.cameras.new('R63_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[];O,U,N=map(Vector,[r['origin'],r['axis'],r['outward']]);Z=Vector((0,0,1))
def pnt(x,d,z):return O+U*x+N*d+Z*z
for name,eye,target,lens in [('inside',pnt(0,-4.5,1.65),pnt(0,.8,2.1),32),('panel',pnt(-.7,-.75,1.65),pnt(-1.16,-.1,1.58),55),('sign',pnt(0,-1,3.5),pnt(0,-.07,3.97),55)]:
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R63_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R63_{name}.png',eye=list(eye),target=list(target)))
(B/'reports/R63_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
