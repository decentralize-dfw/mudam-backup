from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R103_build_report.json').read_text());phase=sys.argv[sys.argv.index('--')+1];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));C=json.loads((B/'config/foundation.json').read_text())['calibration'];S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100;S.view_settings.exposure=2
def pt(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R103_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
for name,eye,target,lens in [('gallery_stair_portal',(802,448,7.0),(805,383,6.7),42),('gallery_service_join',(795,570,7.0),(713,620,6.5),42)]:
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R103_{phase}_{name}.png');bpy.ops.render.render(write_still=True)
