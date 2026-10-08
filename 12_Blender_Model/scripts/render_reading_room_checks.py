"""Reopen verified R09 and render its room review camera."""
from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R09_build_report.json').read_text());q=json.loads((B/'reports/R09_verification.json').read_text());assert r['file']==q['file'] and not q['failures'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;old=json.loads((B/'reports/R08_build_report.json').read_text());keep=(set(old['closed_objects'])|set(r['closed_objects'])|{r['changed_floor']})-set(r['cutters']);keep.update(o.name for o in S.objects if o.name.startswith('P15_READING_'))
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.render.filepath=str(B/'renders/qa/R09_reading_room.png');bpy.ops.render.render(write_still=True)
