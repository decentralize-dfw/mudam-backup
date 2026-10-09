from pathlib import Path
import bpy,json,re
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';import sys;sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene;r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=24;S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R24_ROOM_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
revision='R'+re.search(r'_R(\d+)_',r['file']).group(1);images=[]
for name,pos,target,lens in [('east_gallery',(375,580,6.5),(377,420,8.0),20),('west_gallery',(773,580,6.5),(778,430,8.0),20),('east_clerestory',(345,420,6.5),(399,565,10),22),('west_clerestory',(800,424,6.5),(757,567,10),22)]:
 name=revision+'_'+name;cam.location=point(*pos);cam.rotation_euler=(point(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=name+'.png',eye_canonical=pos,target_canonical=target,lens=lens))
(B/'reports'/f'{revision}_gallery_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=images,all_active_surroundings=True,metric_camera_match=False,roof_geometry_still_draft=True),indent=2),encoding='utf8')
