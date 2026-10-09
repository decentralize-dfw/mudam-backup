from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R92_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];images=[]
def point(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100
 cd=bpy.data.cameras.new('R92_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);cam.location=point(750,500,1.65);target=point(750,405,1.65);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=22;S.camera=cam
 ld=bpy.data.lights.new('R92_REVIEW_ONLY_FILL','AREA');ld.energy=350;ld.size=4;lamp=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(lamp);lamp.parent=cam
 S.render.filepath=str(B/'renders/qa'/f'R92_{phase}_west_gallery.png');bpy.ops.render.render(write_still=True);images.append(dict(phase=phase,file=file,image=Path(S.render.filepath).name))
(B/'reports/R92_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=images,all_active_surroundings=True,temporary_review_light=True,metric_camera_match=False),indent=2))
