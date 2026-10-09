from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R42_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R42_SHADING_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
for key,eye,target,lens in [('hall_context',(565,454,1.65),(638,383,5.0),24),('roof_detail',(604,429,3.5),(648,368,6.4),30),('hall_oblique',(620,475,1.65),(634,382,5.2),24)]:
 cam.location=pt(*eye);cam.rotation_euler=(pt(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R42_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R42_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,photo_pose_not_calibrated=True,permanent_shading_dimensions_not_verified=True),indent=2),encoding='utf8')
