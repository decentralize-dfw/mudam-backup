from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R57_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=1200;origin,u,n=map(Vector,[r['origin'],r['axis'],r['outward']]);up=Vector((0,0,1));cd=bpy.data.cameras.new('R57_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[]
for name,eye,target,lens in [('inside',origin-n*2+up*1.65,origin+n*1+up*.8,25),('floor',origin-n*.55+u*.38+up*1.7,origin+n*1.1+up*.03,29),('outside',origin+n*4-u*2+up*1.65,origin+n*.6+up*1.4,26)]:
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R57_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R57_{name}.png',eye=list(eye),target=list(target)))
(B/'reports/R57_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
