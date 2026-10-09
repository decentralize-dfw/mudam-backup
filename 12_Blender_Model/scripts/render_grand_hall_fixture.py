from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R50_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R50_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;c=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);up=Vector((0,0,1));target=c+up*(r['bottom_z']+.35);images=[]
ld=bpy.data.lights.new('R50_INSPECTION','AREA');ld.energy=1100;ld.size=4;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light)
def render(name,eye,look,lens):
 cam.location=eye;cam.rotation_euler=(look-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;light.location=target+ex*3-up*2;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R50_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=f'R50_{name}.png',eye=list(eye),target=list(look),lens=lens))
render('fixture_detail',target+ex*4+ey*5-up*2,target,43)
render('upward',c+up*1.7,target,40)
render('hall_context',c+ex*4+ey*4+up*1.7,c+up*11,22)
(B/'reports/R50_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False,images=images),indent=2),encoding='utf8')
