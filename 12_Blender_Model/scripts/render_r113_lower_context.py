from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R113_build_report.json').read_text());t=json.loads((B/'reports/R05_build_report.json').read_text());j=json.loads((B/'reports/R48_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1500;S.render.resolution_y=1100;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R113_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;center=Vector(t['center_world']);ex=Vector(t['canonical_x_world']);ey=Vector(t['canonical_y_world']);up=Vector((0,0,1));LOW=t['lower_z'];images=[]
ld=bpy.data.lights.new('R113_INSPECTION','AREA');ld.energy=350;ld.size=4;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light);light.location=center-ex*2+ey*2+up*(-.2)
def render(name,eye,target,lens):
 light.location=eye+up*.7;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=900 if name=='lower_context' else 350;cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R113_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=f'R113_{name}.png',eye=list(eye),target=list(target),lens=lens))
render('lower_context',center-ex*8+ey*5+up*(LOW+1.65),center+up*(-1.2),22)
def path(f):
 a=t['bottom_angle']+(t['top_angle_midradius']-t['bottom_angle'])*f;rad=(t['inner_radius']+t['outer_radius'])/2;return center+(ex*math.cos(a)+ey*math.sin(a))*rad+up*(LOW-f*LOW)


(B/'reports/R113_lower_context_render.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False,images=images),indent=2))
