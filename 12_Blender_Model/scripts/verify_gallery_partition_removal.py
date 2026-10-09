from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R92_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));fail=[];rows=[];verts=[];faces=[];owners=[];names=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();start=len(verts);verts.extend(eo.matrix_world@v.co for v in me.vertices);names.append(ob.name)
 for f in me.polygons:faces.append(tuple(start+i for i in f.vertices));owners.append(len(names)-1)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces)
for old in r['removed_objects']:
 if bpy.data.objects.get(old['name']) is not None:fail.append(old['name']+' remains')
 side=old['name'].split('_')[1]
 for name in [f'R28_{side}_CIRCULATION_FLOOR',f'R28_{side}_FLAT_CEILING']:
  o=bpy.data.objects.get(name)
  if o is None or o.hide_render:fail.append(name+' lost')
 # A removal check across the old diagonal footprint, not an exterior-closure claim.
 ps=list(map(Vector,old['world_vertices']));z0=min(p.z for p in ps);base=ps[:len(ps)//2];a,b=max(((a,b) for a,b in zip(base,base[1:]+base[:1])),key=lambda pair:(pair[1]-pair[0]).length);edge=b-a;n=Vector((-edge.y,edge.x,0)).normalized()
 for i in range(1,10):
  for h in [.3,1.2,2.1]:
   p=a.lerp(b,i/10)+Vector((0,0,h));hit=tree.ray_cast(p-n*.8,n,1.6);row=dict(removed_wall=old['name'],point=list(p),height=h,obstruction=None if hit[0] is None else names[owners[hit[2]]]);rows.append(row)
   if hit[0] is not None:fail.append(row)
q=dict(file=r['file'],removed=[x['name'] for x in r['removed_objects']],retained_floor_and_ceiling=True,former_partition_samples=rows,failures=fail,construction_acceptance=False);(B/'reports/R92_verification.json').write_text(json.dumps(q,indent=2));assert not fail,fail
