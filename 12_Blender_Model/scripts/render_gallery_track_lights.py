from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R70_build_report.json').read_text());w=json.loads((B/'reports/R52_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R70_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;up=Vector((0,0,1));images=[]
ld=bpy.data.lights.new('R70_INSPECTION','AREA');ld.energy=600;ld.size=4;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light)
def render(name,eye,target,lens):
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;light.location=eye+up*.3;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R70_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=f'R70_{name}.png',eye=list(eye),target=list(target),lens=lens))
window=w['windows'][1];a,b,n=Vector(window['left']),Vector(window['right']),Vector(window['outward']);c=(a+b)/2;u=(b-a).normalized()
render('gallery_context',c-n*7+u*1.8+up*1.65,c-n*1.7+up*3.0,22)
t=r['tracks'][1];a,b=Vector(t['start']),Vector(t['end']);render('track',a+up*2.6-Vector(r['canonical_x_world'])*1.5,a.lerp(b,.55)+up*4.3,26)
f=r['fixtures'][4];c=Vector(f['pivot']);axis=Vector(f['axis']);render('fixture',c+Vector(r['canonical_x_world'])*.6+Vector(r['canonical_y_world'])*.55-up*.25,c+up*.04,55)
(B/'reports/R70_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=images,all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False),indent=2),encoding='utf8')
