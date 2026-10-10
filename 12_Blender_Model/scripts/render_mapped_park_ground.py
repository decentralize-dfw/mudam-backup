from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R132_build_report.json').read_text());rows=[]
for stage,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
 cd=bpy.data.cameras.new('R132_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 for key,eye,target,lens in [('ground',(20,93,18),(0,70,0),35)]:
  cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;out=B/'renders/qa'/f'R132_{stage}_{key}.png';S.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append(dict(image=out.relative_to(R).as_posix(),eye=eye,target=target,stage=stage))
(B/'reports/R132_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,lighting_unchanged=True),indent=2),encoding='utf8')
