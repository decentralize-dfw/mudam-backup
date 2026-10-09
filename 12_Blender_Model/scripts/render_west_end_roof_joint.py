from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R91_build_report.json').read_text());images=[]
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1400;S.render.resolution_y=1000;S.render.resolution_percentage=100
 a,b=map(Vector,r['roof_endpoints']);edge=b-a;n=Vector((-edge.y,edge.x,0)).normalized();target=(a+b)/2;eye=target+n*25+Vector((0,0,9))
 cd=bpy.data.cameras.new('R91_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);cam.location=eye;cam.rotation_euler=(target-eye).to_track_quat('-Z','Y').to_euler();cd.lens=35;S.camera=cam;S.render.filepath=str(B/'renders/qa'/f'R91_{phase}_west_end.png');bpy.ops.render.render(write_still=True);images.append(dict(phase=phase,file=file,image=Path(S.render.filepath).name))
(B/'reports/R91_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=images,all_active_surroundings=True,metric_camera_match=False),indent=2))
