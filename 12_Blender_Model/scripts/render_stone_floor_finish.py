from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R43_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];LOW=json.loads((B/'reports/R05_build_report.json').read_text())['lower_z'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name,where,power,size in [('FOYER',(575,390,LOW+4.2),600,12),('LIFT',(665,548,UP+3.1),120,2)]:
 ld=bpy.data.lights.new('R43_REVIEW_'+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=pt(*where)
cd=bpy.data.cameras.new('R43_FLOOR_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
for key,eye,target,lens in [('hall_floor',(570,482,1.65),(603,425,.45),24),('foyer_floor',(569,433,LOW+1.65),(630,383,LOW+.9),22),('lift_floor',(673,553,UP+1.65),(661,533,UP+.5),24)]:
 cam.location=pt(*eye);cam.rotation_euler=(pt(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R43_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R43_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_lights_only=True,colour_and_lighting_calibrated=False),indent=2),encoding='utf8')
