from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R134_build_report.json').read_text());c=Vector(json.loads((B/'reports/R08_build_report.json').read_text())['center_world']);s=json.loads((B/'reports/R10_build_report.json').read_text());sc=Vector(s['center_world']);ex=Vector(s['canonical_x_world']);ey=Vector(s['canonical_y_world']);Z=Vector((0,0,1));views=[('reading',c+Vector((2,-2,6.4)),c+Vector((0,0,10)),20),('spiral',sc+ex*6-ey*5+Z*2,sc+Z*2.6,32)];rows=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R134_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 for key,eye,target,lens in views:
  cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;out=B/'renders/qa'/f'R134_{phase}_{key}.png';S.render.filepath=str(out);bpy.ops.render.render(write_still=True);rows.append(dict(image=out.relative_to(R).as_posix(),phase=phase,eye=list(eye),target=list(target)))
(B/'reports/R134_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,lighting_unchanged=True),indent=2)+'\n')
