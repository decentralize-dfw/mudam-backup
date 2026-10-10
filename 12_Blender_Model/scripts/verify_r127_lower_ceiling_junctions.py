from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R127_build_report.json').read_text());rays=[];before=[];fail=[];dups={};trees={}
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));dep=bpy.context.evaluated_depsgraph_get();trees={};bounds={}
 for name in set(n for p in r['checked_pairs'] for n in p):
  o=bpy.data.objects[name];eo=o.evaluated_get(dep);m=eo.to_mesh();vs=[eo.matrix_world@v.co for v in m.vertices];trees[name]=BVHTree.FromPolygons(vs,[tuple(f.vertices) for f in m.polygons]);bounds[name]=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)];eo.to_mesh_clear()
 if phase=='before':
  for pair in r['checked_pairs']:
   bb=[[min(bounds[n][i][0] for n in pair),max(bounds[n][i][1] for n in pair)] for i in range(3)]
   for axis in range(3):
    u,v=[i for i in range(3) if i!=axis]
    for j in range(math.ceil((bb[u][1]-bb[u][0])/.2)):
     for k in range(math.ceil((bb[v][1]-bb[v][0])/.2)):
      for sign in [-1,1]:
       p=Vector((0,0,0));p[u]=bb[u][0]+(j+.371)*.2;p[v]=bb[v][0]+(k+.437)*.2;p[axis]=bb[axis][0]-.1 if sign==1 else bb[axis][1]+.1;d=Vector((0,0,0));d[axis]=sign;rays.append((pair,p,d,bb[axis][1]-bb[axis][0]+.2))
 vals=[];duplicate=0
 for idx,(pair,p,d,limit) in enumerate(rays):
  hits=[h[3] for n in pair if (h:=trees[n].ray_cast(p,d,limit))[0] is not None];dist=min(hits) if hits else None;vals.append(dist);duplicate+=len(hits)>1 and max(hits)-min(hits)<1e-4
  if phase=='after':
   old=before[idx]
   if (old is None)!=(dist is None) or old is not None and abs(old-dist)>1e-4:fail.append(dict(pair=pair,origin=list(p),direction=list(d),before=old,after=dist))
 if phase=='before':before=vals
 dups[phase]=duplicate
q=dict(file=r['file'],ray_count=len(rays),coincident_front_hits=dups,failures=fail,construction_acceptance=False,scope='Six-direction sampled silhouette/depth preservation of each wall pair, 0.2m spacing.');(B/'reports/R127_verification.json').write_text(json.dumps(q,indent=2));print(len(rays),dups,'failures',len(fail),fail[:3])
