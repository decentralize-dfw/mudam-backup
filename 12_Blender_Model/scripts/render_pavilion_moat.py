from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R68_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=48;S.render.resolution_percentage=100;S.render.resolution_x=1600;S.render.resolution_y=1100;cd=bpy.data.cameras.new('R68_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;rows=[];P=json.loads((B/'reports/R18_build_report.json').read_text())['portals'];center=lambda i:(Vector(P[i]['left'])+Vector(P[i]['right']))/2;Z=Vector((0,0,1));along=(center(7)-center(6)).normalized()
for name,eye,target,lens in [('context',Vector((58,-74,23)),Vector((17,-36,-2)),43),('link_edge',center(5)+Z*1.65,Vector((16,-41,-2)),26)]:
 cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R68_{name}.png');bpy.ops.render.render(write_still=True);rows.append(dict(image=f'R68_{name}.png',eye=list(eye),target=list(target)))
(B/'reports/R68_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=rows,all_active_surroundings=True,metric_camera=False),indent=2),encoding='utf8')
