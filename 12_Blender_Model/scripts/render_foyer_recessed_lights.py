from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R69_build_report.json').read_text());t=json.loads((B/'reports/R05_build_report.json').read_text());j=json.loads((B/'reports/R48_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1100;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R69_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;center=Vector(t['center_world']);ex=Vector(t['canonical_x_world']);ey=Vector(t['canonical_y_world']);up=Vector((0,0,1));LOW=t['lower_z'];images=[]
ld=bpy.data.lights.new('R69_INSPECTION','AREA');ld.energy=350;ld.size=4;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light);light.location=center-ex*2+ey*2+up*(-.2)
def render(name,eye,target,lens):
 light.location=eye+up*.7;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=900 if name=='lower_context' else 350;cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R69_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=f'R69_{name}.png',eye=list(eye),target=list(target),lens=lens))
render('lower_context',center-ex*8+ey*5+up*(LOW+1.65),center+up*(-1.2),22)
render('ceiling',center-ex*2+ey*2+up*(LOW+2.8),center+ey*.6+up*(-.6),24)
p=Vector(r['fixtures'][3]['center']);render('fixture',p+ex*.3+ey*.2-up*.32,p+up*.02,55)
(B/'reports/R69_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False,images=images),indent=2))
