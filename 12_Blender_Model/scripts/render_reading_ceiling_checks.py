"""Render R08 again from its reopened verified file."""
from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R08_build_report.json').read_text());q=json.loads((B/'reports/R08_verification.json').read_text());assert r['file']==q['file'] and not q['failures'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;keep=set(r['closed_objects']);keep.update(o.name for o in S.objects if o.name.startswith(('P15_READING_','P17_READING_FLOOR')))
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R08_reading_upward.png');bpy.ops.render.render(write_still=True)
cam=S.camera;center=Vector(r['center_world']);cam.location=center+Vector((3,-3,r['floor_z']+1.55));target=center+Vector((0,0,9.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20;S.render.filepath=str(B/'renders/qa/R08_reading_oblique.png');bpy.ops.render.render(write_still=True)
