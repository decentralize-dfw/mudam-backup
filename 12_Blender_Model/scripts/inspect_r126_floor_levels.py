from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R125_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));trees={};points=set();deps=bpy.context.evaluated_depsgraph_get();bounds={};levels={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get() or not any(s in o.name for s in ['FLOOR','THRESHOLD']):continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices]
 if not vs or max(v.z for v in vs)-min(v.z for v in vs)>.5:eo.to_mesh_clear();continue
 levels[o.name]=round(max(v.z for v in vs),3);trees[o.name]=BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in me.polygons]);bounds[o.name]=[min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs)];eo.to_mesh_clear()
for name,t in trees.items():
 x0,x1,y0,y1=bounds[name]
 for i in range(math.floor(x0/.25),math.ceil(x1/.25)):
  for j in range(math.floor(y0/.25),math.ceil(y1/.25)):
   p=Vector(((i+.37)*.25,(j+.43)*.25,levels[name]+.02))
   if t.ray_cast(p,Vector((0,0,-1)),.05)[0] is not None:points.add((p.x,p.y,levels[name]))
pairs={}
for x,y,z in points:
 names=sorted(n for n,t in trees.items() if abs(levels[n]-z)<.002 and t.ray_cast(Vector((x,y,z+.02)),Vector((0,0,-1)),.05)[0] is not None)
 if len(names)<2:continue
 key=' | '.join(names);row=pairs.setdefault(key,dict(names=names,count=0,samples=[]));row['count']+=1
 if len(row['samples'])<8:row['samples'].append([x,y,z])
q=dict(file=r['file'],floor_names=list(trees),samples=len(points),overlaps=list(pairs.values()));(B/'reports/R126_floor_levels_diagnostic.json').write_text(json.dumps(q,indent=2));print(q['samples'],q['overlaps'])
