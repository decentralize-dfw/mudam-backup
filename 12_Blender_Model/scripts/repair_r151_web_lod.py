from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'reports/R151_WEB_LOD_build.json').read_text());v=json.loads((R/'reports/R151_WEB_LOD_verification.json').read_text());names={x['name'] for x in v['failures']};assert len(names)==38
(R/'reports/R151_WEB_LOD_v001_build.json').write_text(json.dumps(r,indent=2));(R/'reports/R151_WEB_LOD_v001_verification.json').write_text(json.dumps(v,indent=2))
bpy.ops.wm.open_mainfile(filepath=r['file']);targets={n:bpy.data.objects[n] for n in names};mats={n:list(o.data.materials) for n,o in targets.items()}
with bpy.data.libraries.load(r['source'],link=False) as (a,b):b.objects=sorted(names)
for n,source in zip(sorted(names),b.objects):
 target=targets[n];target.data=source.data.copy();target.data.materials.clear()
 for m in mats[n]:target.data.materials.append(m)
 bpy.data.objects.remove(source,do_unlink=True)
bpy.ops.outliner.orphans_purge(do_recursive=True)
out=R/'scenes/MUDAM_R151_WEB_LOD_v002.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r['file']=str(out);r['restored_original_tiles']=sorted(names);r['changes']=[x for x in r['changes'] if x['name'] not in names]
r['after_triangles']=0;r['context_after']=0
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render:
  o.data.calc_loop_triangles();t=len(o.data.loop_triangles);r['after_triangles']+=t
  if o.name.startswith('R151_ACT_'):r['context_after']+=t
r['architecture_after']=r['after_triangles']-r['context_after'];r['bytes']=out.stat().st_size
(R/'reports/R151_WEB_LOD_build.json').write_text(json.dumps(r,indent=2));print('REPAIR_DONE',r['after_triangles'],r['bytes'],flush=True)
