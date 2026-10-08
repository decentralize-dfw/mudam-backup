"""Internal roof detail QA, with a saved source scene kept untouched."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P11_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene
C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def pt(p,z):
 u=k*p[0]+off[0];v=k*p[1]+off[1];return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('QA_P11_INTERNAL_ROOF');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);cam.location=pt((406,351),1.65);target=pt((364,275),6);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=22;cd.clip_end=500;S.camera=cam;S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True;S.cycles.max_bounces=12;S.cycles.transmission_bounces=8
preferences=bpy.context.preferences.addons['cycles'].preferences;preferences.compute_device_type='OPTIX';preferences.get_devices()
for device in preferences.devices:device.use=device.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/P11_internal_east.png');bpy.ops.render.render(write_still=True)
