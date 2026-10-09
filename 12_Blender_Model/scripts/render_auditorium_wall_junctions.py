from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R75_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;C=json.loads((B/'config/foundation.json').read_text())['calibration']
s,dx,dy=C['basement_registration']['source_to_canonical']
def point(x,y,z=0):
 x=s*x+dx;y=s*y+dy
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1400;S.render.resolution_y=1100;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R75_ROOM_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
# Review lighting is separate from unverified permanent fixture layout.
for i,(x,y) in enumerate([(478,436),(567,436),(482,480),(565,480),(523,516)]):
 ld=bpy.data.lights.new(f'R75_REVIEW_LIGHT_{i}','AREA');ld.energy=450;ld.shape='DISK';ld.size=4;ld.color=(1,.94,.84);ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=point(x,y,-1.05)
for name,pos,target,lens in [('R75_room_to_stage',(478,504,-1.95),(525,419,-2.6),18),('R75_stage_corner',(489,432,-2.2),(504,399,-2.4),30)]:
 cam.location=point(*pos);cam.rotation_euler=(point(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R75_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,metric_camera_match=False,review_lights_not_architectural_fixtures=True),indent=2),encoding='utf8')
