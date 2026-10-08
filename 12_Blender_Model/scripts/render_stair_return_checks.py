"""Reopened R03 geometry, isolated overview of podium and guard placement."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R03_build_report.json').read_text());q=json.loads((B/'reports/R03_verification.json').read_text());assert r['file']==q['file'] and not q['failures']
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;center=Vector(r['center_world']);axis=Vector(r['axis_world']);normal=Vector(r['normal_world'])
keep=set(r['closed_objects']+['P05_FLOOR_L00_GH'])
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
cam=bpy.data.objects['R03_RETURN_REVIEW'];target=center-axis*.75+Vector((0,0,.35));cam.location=target-axis*4+normal*5+Vector((0,0,7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=9
S.camera=cam;S.render.resolution_x=1400;S.render.resolution_y=1100;S.render.resolution_percentage=100;S.render.filepath=str(B/'renders/qa/R03_podium_overview.png');S.cycles.samples=48
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';bpy.ops.render.render(write_still=True)
print('R03_REOPENED_OVERVIEW',r['file'])
