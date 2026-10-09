from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R45_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];T=json.loads((B/'reports/R04_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R45_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
ld=bpy.data.lights.new('R45_INSPECTION','AREA');ld.energy=300;ld.shape='DISK';ld.size=4;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=pt(532,515,7.3)
def render(name,eye,target,lens):
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R45_{name}.png');bpy.ops.render.render(write_still=True)
row=r['cavity_samples'][2];p=Vector(row['front']);n=Vector(row['normal']);render('grip_detail',p+n*1.65+Vector((0,0,.28)),p,45)
st=T['steps'][2];p=pt(*[sum(st[k][i] for k in ['outer0','outer1','inner0','inner1'])/4 for i in range(2)],st['z']+1.6);target=Vector(r['cavity_samples'][13]['front']);render('on_stair',p,target,23)
render('hall_context',pt(575,485,1.65),pt(520,535,3.2),23)
(B/'reports/R45_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_light_only=True,metric_camera_match=False),indent=2),encoding='utf8')
