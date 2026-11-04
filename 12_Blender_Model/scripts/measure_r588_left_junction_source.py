import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
a=Vector((-23.6686000824,9.9090995789));b=Vector((-14.7164554596,8.8859462738));d=b-a;n=Vector((-d.y,d.x)).normalized();out={}
for tag,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('v019',R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v019.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();trees=[]
 if tag=='v019':
  for name in ['R549_WEST_GLASS_EXTERNAL_GROUND_1','R322_WEST_MUSEUM_TERRACE']:
   o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices];trees.append((name,BVHTree.FromPolygons(vs,[list(p.vertices)for p in o.data.polygons])))
 profiles=[]
 for xx in [-23,-21,-19,-17,-15]:
  p=a+d*((xx-a.x)/d.x);rows=[]
  for off in [-3,-2,-1,-.5,-.1,0,.1,.5,1]:
   q=p+n*off;hits=[]
   if tag=='source':
    h,co,no,idx,o,m=s.ray_cast(dg,Vector((q.x,q.y,15)),Vector((0,0,-1)),distance=40)
    if h:hits.append(dict(z=co.z,normal=list(no),object=o.name))
   else:
    for name,tree in trees:
     co,no,idx,dist=tree.ray_cast(Vector((q.x,q.y,15)),Vector((0,0,-1)),40)
     if co is not None:hits.append(dict(z=co.z,normal=list(no),object=name,face=idx))
   rows.append(dict(offset=off,xy=list(q),hits=hits))
  profiles.append(dict(x=xx,edgeXY=list(p),rows=rows));print('LEFT',tag,xx,[(v['offset'],[(round(h['z'],3),round(h['normal'][2],3),h['object']if tag!='source'else'')for h in v['hits']])for v in rows],flush=True)
 out[tag]=profiles
(W/'R588_R549_LEFT_SOURCE_PROFILES.json').write_text(json.dumps(out,indent=2))
