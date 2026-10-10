from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R129_build_report.json').read_text());poses=json.loads((B/'reports/R55_render_receipt.json').read_text())['images'];rows=[]
for stage,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
 cd=bpy.data.cameras.new('R129_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 for pose in poses:
  name='context' if 'context' in pose['image'] else 'detail';cam.location=pose['eye'];cam.rotation_euler=(Vector(pose['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=25 if name=='context' else 30
  out=B/'renders/qa'/f'R129_{stage}_{name}.png';S.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append(dict(image=out.relative_to(R).as_posix(),stage=stage,eye=pose['eye'],target=pose['target']))
(B/'reports/R129_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,lighting_unchanged=True,metric_camera=False),indent=2))
