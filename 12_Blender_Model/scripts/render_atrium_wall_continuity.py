"""Identical full-scene review cameras before/after R72; no occluding walls hidden."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R72_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['after'];phase=args[0];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(R/file));S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1400;S.render.resolution_y=1050;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R72_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;images=[]
for name,eye,target,lens in [('north',(370,-120,8),(565,334,2.5),45),('high_walls',(210,810,37),(560,485,13.5),55),('east_junction',(355,370,24),(466,464,9),50)]:
 if len(args)>1 and name!=args[1]:continue
 cam.location=point(eye);t=point(target);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R72_{phase}_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=Path(S.render.filepath).name,eye_canonical=eye,target_canonical=target,lens=lens))
(B/'reports'/f'R72_render_{phase}.json').write_text(json.dumps(dict(file=file,images=images,all_active_surroundings=True,metric_camera_match=False),indent=2),encoding='utf8')
