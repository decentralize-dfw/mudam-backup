from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R30_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1400;S.render.resolution_y=1000;S.render.resolution_percentage=100
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R30_ACCESS_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=20
# Inspection-only fill lighting; no architectural lighting claim and no saved scene modification.
lights=[]
for side,coord in [('LIFT',(665,548))]:
 ld=bpy.data.lights.new('R30_INSPECTION_'+side,'AREA');ld.energy=100;ld.shape='DISK';ld.size=2;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=pt(*coord,r['landing_top']-.1);lights.append(ob.name)
for key,eye,target in [('door_detail',(673,553,r['upper_z']+1.65),(663,533,r['upper_z']+1.5)),('bridge_approach',(671,577,r['upper_z']+1.65),(665,538,r['upper_z']+1.65))]:
 cam.location=pt(*eye);cam.rotation_euler=(pt(*target)-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R30_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports/R30_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_only_lights=lights,lighting_calibration=False,metric_pose=False),indent=2),encoding='utf8')
