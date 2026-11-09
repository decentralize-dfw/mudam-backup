from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1]
def snapshot(name):
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/name));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.name.startswith(('R157_TREE_','R158_TREE_')):continue
  data=(tuple(tuple(row) for row in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),o.hide_render)
  out[o.name]=hashlib.sha256(repr(data).encode()).hexdigest()
 return out
a=snapshot('MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v004.blend');b=snapshot('MUDAM_R158_ACT_ORMAN_ORTUSU_v003.blend');assert a==b
trees=[o for o in bpy.context.scene.objects if o.name.startswith('R158_TREE_')];source=json.loads((R/'.local_source_cache/r158/trees.json').read_text())['trees'];assert len(trees)==len(source)==6335
assert not any(o.name.startswith('R157_TREE_') for o in bpy.context.scene.objects)
r={'reopened':True,'non_vegetation_geometry_unchanged':True,'source_placements':len(source),'scene_trees':len(trees),'old_trees_removed':True,'exact_tree_species_and_stems':False,'whole_source_model_reproduced':False}
(R/'reports/R158_QA.json').write_text(json.dumps(r,indent=2));print('R158_QA_PASSED',flush=True)
