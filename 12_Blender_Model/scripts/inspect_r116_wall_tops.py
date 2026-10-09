"""Full-scene 2.1m review headroom across tread interiors; not statutory acceptance."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R116_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);up=Vector((0,0,1));rows=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name]
 if o.hide_render or 'FLOOR' in name or 'BACKING' in name or 'LEAF' in name:continue
 p=[o.matrix_world@v.co for v in o.data.vertices];z=max(v.z for v in p);top=[v for v in p if abs(v.z-z)<1e-4];a=sum(top,Vector())/len(top);h=tree.ray_cast(a+up*.01,up,25);rows.append(dict(name=name,top=z,hit=None if h[0] is None else [owners[h[2]],h[0].z]))
(B/'reports/R116_wall_tops.json').write_text(json.dumps(rows,indent=2));print(rows)
