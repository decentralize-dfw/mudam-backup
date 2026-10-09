from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R109_build_report.json').read_text());phase=sys.argv[sys.argv.index('--')+1];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));C=json.loads((B/'config/foundation.json').read_text())['calibration'];S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for ob in bpy.context.scene.objects:
 if ob.type in ['MESH','CURVE'] and ob.name not in ['R33_WALL_SERVICE_W_N','R33_WALL_SERVICE_W_W']:ob.hide_render=True
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1000;S.render.resolution_y=900;S.render.resolution_percentage=100
def pt(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R109_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cam.location=pt((611,651,2.2));cam.rotation_euler=(pt((617.76,657.58,2.2))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=38
ld=bpy.data.lights.new('R109_INSPECTION_FILL','AREA');ld.energy=400;ld.size=3;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light);light.location=pt((611,651,3.3));S.render.filepath=str(B/'renders/qa'/f'R109_{phase}_service_stair_wall_corner.png');bpy.ops.render.render(write_still=True)
