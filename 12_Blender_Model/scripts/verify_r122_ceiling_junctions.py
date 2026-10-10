from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R122_build_report.json').read_text());names=['R85_RETURN_CEILING_0','R85_RETURN_CEILING_1','R39_PUBLIC_CEILING_19','R28_W_FLAT_CEILING'];targets=names;points=set();summaries=[];fail=[];UP=0.0
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));trees={};bounds={};levels={};dep=bpy.context.evaluated_depsgraph_get()
 for name in names:
  o=bpy.data.objects[name]
  if o.hide_render or not o.visible_get():continue
  eo=o.evaluated_get(dep);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];levels[name]=max(v.z for v in vs);trees[name]=BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in me.polygons]);bounds[name]=[min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs)];eo.to_mesh_clear()
 if phase=='before':
  for name in targets:
   x0,x1,y0,y1=bounds[name]
   for ix in range(math.ceil((x1-x0)/.25)):
    for iy in range(math.ceil((y1-y0)/.25)):
     x=x0+(ix+.371)*.25;y=y0+(iy+.437)*.25
     if trees[name].ray_cast(Vector((x,y,levels[name]+.02)),Vector((0,0,-1)),.06)[0] is not None:points.add((x,y,levels[name]))
 counts={};dups=0
 for x,y,z in points:
  owners=[n for n,t in trees.items() if t.ray_cast(Vector((x,y,z+.02)),Vector((0,0,-1)),.06)[0] is not None];counts[len(owners)]=counts.get(len(owners),0)+1;dups+=len(owners)>1
  if phase=='after' and len(owners)!=1:fail.append(dict(x=x,y=y,owners=owners))
 summaries.append(dict(phase=phase,samples=len(points),coverage_counts=counts,duplicate_samples=dups))
q=dict(file=r['file'],summaries=summaries,failures=fail,construction_acceptance=False,scope='Original ceiling footprints sampled at 0.25m spacing; preserve coverage with one finished surface.');(B/'reports/R122_verification.json').write_text(json.dumps(q,indent=2));print(summaries,fail[:5])
