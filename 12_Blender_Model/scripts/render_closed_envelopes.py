from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R44_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R04_build_report.json').read_text())['upper_level'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R44_exterior.png');bpy.ops.render.render(write_still=True)
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R44_ENVELOPE_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
for name,pos,power,size in [('STAIR',(533,510,7.3),350,5),('PASSAGE',(575,579,4.1),200,4)]:
 ld=bpy.data.lights.new('R44_INSPECTION_'+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=pt(*pos)
steps=json.loads((B/'reports/R04_build_report.json').read_text())['steps'];st=steps[18];eye=tuple(sum(st[k][i] for k in ['outer0','outer1','inner0','inner1'])/4 for i in range(2))+(st['z']+1.6,)
for key,eye,target,lens in [('upper_stair',(575,485,1.65),(520,535,3.2),23),('landing_back',(575,580,UP+1.65),(530,545,UP-.8),20),('ceiling_junction',eye,(565,575,UP+1.3),20)]:
 cam.location=pt(*eye);cam.rotation_euler=(pt(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R44_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R44_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_lights_only=True,metric_camera_match=False),indent=2),encoding='utf8')
