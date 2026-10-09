from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R115_build_report.json').read_text())
phase=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'after'
file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene']
bpy.ops.wm.open_mainfile(filepath=str(R/file));S=bpy.context.scene
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R115_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
g=bpy.data.objects['R18_LEAF_LEFT_GLASS'];v=[g.matrix_world@q.co for q in g.data.vertices];x=(v[1]-v[0]).normalized();y=(v[3]-v[0]).normalized();up=Vector((0,0,1));target=(v[0]+v[3])/2+x*.15+up*.35
cam.location=target+y*1.35+x*.3+up*.12;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=48
ld=bpy.data.lights.new('R115_REVIEW_LIGHT','AREA');ld.energy=100;ld.size=2;ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=target+y*1+up*1.5;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
S.render.filepath=str(B/'renders/qa'/f'R115_{phase}_door_corner.png');bpy.ops.render.render(write_still=True)
(B/'reports'/f'R115_render_{phase}.json').write_text(json.dumps(dict(file=file,image=Path(S.render.filepath).name,all_active_surroundings=True,diagnostic_light_only=True,source='067',metric_camera_match=False),indent=2),encoding='utf8')
