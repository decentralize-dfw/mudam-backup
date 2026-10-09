from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R16_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1300;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R16_PAVILION_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
for name,pos,z,target,tz,lens in [('R16_pavilion',[0,455],3,[106.5,279.5],8,40),('R16_lantern',[0,380],11,[106.5,279.5],10.7,55),('R16_roof_inside',[106.5,279.5],1.65,[110,279],11,20)]:
 cam.location=point(pos,z);cam.rotation_euler=(point(target,tz)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R16_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_camera_match=False),indent=2),encoding='utf8')
