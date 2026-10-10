from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R136_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];s,dx,dy=C['basement_registration']['source_to_canonical']
def point(x,y,z):
 x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
images=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',R/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1200;S.render.resolution_y=1000;S.render.resolution_percentage=100;cd=bpy.data.cameras.new('R136_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
 for i,(x,y) in enumerate([(478,436),(567,436),(482,480),(565,480),(523,516)]):
  ld=bpy.data.lights.new(f'R136_REVIEW_LIGHT_{i}','AREA');ld.energy=450;ld.shape='DISK';ld.size=4;ld.color=(1,.94,.84);ob=bpy.data.objects.new(ld.name,ld);S.collection.objects.link(ob);ob.location=point(x,y,-1.05)
 for view,pos,target,lens in [('room',(478,504,-1.95),(525,419,-2.6),18),('panel',(484,498,-1.6),(500,505,-1.65),30)]:
  cam.location=point(*pos);cam.rotation_euler=(point(*target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;p=B/'renders/qa'/f'R136_{phase}_{view}.png';S.render.filepath=str(p);bpy.ops.render.render(write_still=True);images.append(str(p.relative_to(R)))
(B/'reports/R136_render_receipt.json').write_text(json.dumps(dict(file=r['file'],images=images,review_lights_not_architectural_fixtures=True,all_active_surroundings=True),indent=2)+'\n')
