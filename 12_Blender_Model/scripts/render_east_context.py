"""Reopen the saved R10 candidate and render it with all active surroundings."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['R10_build_report.json','R10'];prefix=args[1]
r=json.loads((B/'reports'/args[0]).read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
S=bpy.context.scene;C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy
 return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1100;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R10_CONTEXT_AUDIT');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
views=[('R10_garden_context',[429,378],1.65,[315,326],5,24),('R10_garden_reverse',[315,290],1.65,[429,390],5,24),('R10_whole_exterior',[135,110],43,[550,420],5,35)]
for name,pos,z,target,tz,lens in views:
 cam.location=point(pos,z);cam.rotation_euler=(point(target,tz)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'{name.replace("R10",prefix)}.png');bpy.ops.render.render(write_still=True)
(B/'reports'/f'{prefix}_context_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_saved_active_surroundings=True,camera_metric_match=False,views=views),indent=2),encoding='utf8')
