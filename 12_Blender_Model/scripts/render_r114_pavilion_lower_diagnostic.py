from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R114_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1400;S.render.resolution_y=1100;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R114_R25_ROOM_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
lampdata=bpy.data.lights.new('DIAGNOSTIC_ONLY_PAV_LIGHT','AREA');lampdata.energy=1300;lampdata.shape='DISK';lampdata.size=5;lamp=bpy.data.objects.new(lampdata.name,lampdata);S.collection.objects.link(lamp);lamp.location=point(110,275,-.5)
for name,pos,target,lens in [('R114_pav_lower_lit',(107,288,-2.2),(72.5,269,-1.6),24),('R114_pav_lower_reverse',(72,285,-2.2),(152,280,-1.8),20)]:
 cam.location=point(*pos);cam.rotation_euler=(point(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R114_pav_diagnostic_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,diagnostic_light_only_not_saved=True,metric_camera_match=False,stair_and_guard_representative=True),indent=2),encoding='utf8')
