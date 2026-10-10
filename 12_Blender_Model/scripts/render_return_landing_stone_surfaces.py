from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R147_build_report.json').read_text())
C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
views=[('return',pt(813,373,6.3),pt(839,363,7.4),20),('blade',Vector((0,16,-3.4)),Vector((-3.95,15.5,-2.7)),22)]
rows=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R147_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 ld=bpy.data.lights.new('R147_REVIEW_FILL','AREA');ld.energy=900;ld.size=4;lamp=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(lamp);lamp.parent=cam
 for key,eye,target,lens in views:
  cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;out=B/'renders/qa'/f'R147_{phase}_{key}.png';S.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append(dict(image=out.relative_to(R).as_posix(),phase=phase,eye=list(eye),target=list(target)))
(B/'reports/R147_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,temporary_review_light=True,light_not_saved=True),indent=2)+'\n')
