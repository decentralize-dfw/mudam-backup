from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];p=B/'reports/R116_build_report.json';r=json.loads(p.read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));o=bpy.data.objects['R73_E_CONTINUOUS_GALLERY_WALL'];inv=o.matrix_world.inverted()
for v in o.data.vertices:
 w=o.matrix_world@v.co
 if abs(w.z-4.12)<.0001:w.z=3.8;v.co=inv@w
out=B/'scenes/MUDAM_R116_SEKIZ_ISARET_KABUK_v007.blend';assert not out.exists();r['file']=out.relative_to(B.parent).as_posix();r['operations'].append(dict(name=o.name,operation='align backing down to portal beam soffit, preserving passage plane',issue='SS7'));r['changed_inherited_objects']=[n for n in r['changed_inherited_objects'] if n not in r['closed_objects']];bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);p.write_text(json.dumps(r,indent=2))
