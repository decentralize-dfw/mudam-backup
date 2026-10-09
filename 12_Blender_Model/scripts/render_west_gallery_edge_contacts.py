from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R105_build_report.json').read_text());phase=sys.argv[sys.argv.index('--')+1];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));C=json.loads((B/'config/foundation.json').read_text())['calibration'];S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100
def pt(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R105_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.lens=28
ld=bpy.data.lights.new('R105_INSPECTION_FILL','AREA');ld.energy=500;ld.size=6;light=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(light);light.location=pt((713,495,4.1))
for label,eye,target in [('floor_contact',(710,480,1.3),(685,515,.45)),('ceiling_contact',(710,480,1.9),(685,515,4.1))]:
 cam.location=pt(eye);cam.rotation_euler=(pt(target)-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/'renders/qa'/f'R105_{phase}_{label}.png');bpy.ops.render.render(write_still=True)
(B/'reports'/f'R105_{phase}_render_receipt.json').write_text(json.dumps(dict(file=file,inspection_light_only=True,saved_scene_changes=False,cameras=['floor_contact','ceiling_contact']),indent=2))
