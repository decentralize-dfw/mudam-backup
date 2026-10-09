from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R41_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.camera=bpy.data.objects['P07_PHOTO_116_CONDITIONAL'];S.render.filepath=str(B/'renders/qa/R41_exterior.png');bpy.ops.render.render(write_still=True)
# Use stored auditorium camera if available; no geometry hidden for inspection.
q=json.loads((B/'reports/R19_build_report.json').read_text());coords=q.get('canonical_polygon');C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
# Roof overview provides many repeated profile instances at once.
cd=bpy.data.cameras.new('R41_REUSE_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=32;cam.location=Vector((65,-40,42));target=Vector((8,0,10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa/R41_roof_overview.png');bpy.ops.render.render(write_still=True)
(B/'reports/R41_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,geometry_change=False),indent=2),encoding='utf8')
