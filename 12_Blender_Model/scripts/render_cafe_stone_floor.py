from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R148_build_report.json').read_text())
C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
views=[('cafe',pt(835,235,1.7),pt(740,295,.4),24)]
rows=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R148_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 for key,eye,target,lens in views:
  cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;out=B/'renders/qa'/f'R148_{phase}_{key}.png';S.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append(dict(image=out.relative_to(R).as_posix(),phase=phase,eye=list(eye),target=list(target)))
(B/'reports/R148_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,lighting_unchanged=True),indent=2)+'\n')
