"""R95 review with the same three cameras as R92; no review-only hiding."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R111_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['after'];phase=args[0];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(R/file));S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=20;S.render.resolution_x=1400;S.render.resolution_y=1050;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R73_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;images=[]
for name,eye,target,lens in [('east_junction',(430,150,34),(400,435,10),45),('east_end',(130,230,23),(325,390,10),45),('west_junction',(780,180,34),(750,420,10),45),('east_seam',(520,180,23),(462,410,9),45),('east_ground',(310,310,1.7),(400,420,3.4),20),('cafe_ground',(810,245,1.7),(755,340,4),20)]:
 if len(args)>1 and name!=args[1]:continue
 if name=='east_ground':eye=(350,230,1.7);target=(410,400,4.5);lens=24
 cam.location=point(eye);t=point(target);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R111_marked_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=Path(S.render.filepath).name,eye_canonical=eye,target_canonical=target,lens=lens))
receipt=B/'reports'/'R111_marked_render.json'
if len(args)>1 and receipt.exists():
 previous=json.loads(receipt.read_text());images=[x for x in previous['images'] if x['image'] not in {n['image'] for n in images}]+images if previous['file']==file else images
receipt.write_text(json.dumps(dict(file=file,images=images,all_active_surroundings=True,metric_camera_match=False),indent=2),encoding='utf8')
