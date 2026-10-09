from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R48_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R48_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;ld=bpy.data.lights.new('R48_INSPECTION','AREA');ld.energy=250;ld.size=3;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light);light.location=Vector(r['joins'][0]['start'])+Vector((1,0,2.3));images=[]
def render(name,eye,target,lens):
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R48_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=f'R48_{name}.png',eye=list(eye),target=list(target),lens=lens))
for j in r['joins']:
 p=(Vector(j['start'])+Vector(j['end']))/2;render(j['side'].lower()+'_join',p+Vector((1.05,-.65,.45)),p,52)
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
render('landing_context',pt(610,427,1.65),pt(641,393,.7),28)
(B/'reports/R48_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False,images=images),indent=2))
