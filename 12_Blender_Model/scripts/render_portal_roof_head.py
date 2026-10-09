from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R37_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
S.camera=bpy.data.objects['P07_GH_PORTAL_REVIEW'];S.render.resolution_x=1200;S.render.resolution_y=1400;S.render.filepath=str(B/'renders/qa/R37_portal_from_hall.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('R37_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=22;a,b=map(Vector,r['portal_endpoints']);normal=Vector(r['normal']);center=(a+b)/2
def point(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for key,x,y,z,target_z in [('portal_from_garden',420,406,1.65,5.5),('portal_head_close',437,429,7.5,9.1)]:
 cam.location=point(x,y,z);target=center+Vector((0,0,target_z));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R37_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R37_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_pose=False),indent=2),encoding='utf8')
