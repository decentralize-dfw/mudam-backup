"""Reopen verified R05 and inspect its actual source-shaped ground opening."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R05_build_report.json').read_text());q=json.loads((B/'reports/R05_verification.json').read_text());assert r['file']==q['file'] and not q['failures'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene
keep=set(r['closed_objects']+[r['changed_floor'],'P05_ZONE_LM1_GALLERIES_FOYER'])
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
center=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);up=Vector((0,0,1));cam=bpy.data.objects['R05_LOWER_REVIEW'];target=center+up*(-1.7);cam.location=center-ex*7+ey*7+up*11;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=13;S.camera=cam
S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100;S.render.filepath=str(B/'renders/qa/R05_ground_opening.png');S.cycles.samples=64;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';bpy.ops.render.render(write_still=True)
