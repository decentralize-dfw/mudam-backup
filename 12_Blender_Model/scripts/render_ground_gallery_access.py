from pathlib import Path
import bpy,json,sys,re
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R28_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
if '--' in sys.argv:
 sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene;r['file']=verified_current_scene()['file']
revision='R'+re.search(r'_R(\d+)_',r['file'])[1]
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_x=1400;S.render.resolution_y=1000;S.render.resolution_percentage=100
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R28_ACCESS_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=20
# Inspection-only fill lighting; no architectural lighting claim and no saved scene modification.
lights=[]
for side,coord in [('E',(382,460)),('W',(760,470))]:
 ld=bpy.data.lights.new('R28_INSPECTION_'+side,'AREA');ld.energy=500;ld.shape='DISK';ld.size=8;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=pt(*coord,4.15);lights.append(ob.name)
for key,eye,target in [('east_entry',(450,442,1.65),(450,505,1.8)),('west_entry',(700,440,1.65),(700,505,1.8)),('east_reverse',(350,505,1.65),(423,427,1.7))]:
 cam.location=pt(*eye);cam.rotation_euler=(pt(*target)-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'{revision}_{key}.png');bpy.ops.render.render(write_still=True)
(B/'reports'/f'{revision}_ground_render_receipt.json').write_text(json.dumps(dict(file=r['file'],all_active_surroundings=True,inspection_only_lights=lights,lighting_calibration=False,metric_pose=False),indent=2),encoding='utf8')
