from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];domains=json.loads((R/'config/r176_architectural_domains.json').read_text())[:2];more=json.loads((R/'config/r176_north_footprints.json').read_text())
for row in more:
 if row['id'] in ['51768388','788248912','788248913','205062453']:
  domains.append(dict(name=row['tags'].get('name') or row['id'],outer=row['ring'][:-1],holes=[],source='OSM '+row['id'],height_tag=float(row['tags']['height'])))
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
for row in domains:
 p=np.array(row['outer']);samples=[]
 for x in np.arange(p[:,0].min()+1,p[:,0].max(),3):
  for y in np.arange(p[:,1].min()+1,p[:,1].max(),3):
   if not inside((x,y),row['outer']) or any(inside((x,y),h) for h in row['holes']):continue
   hit,n,*_=bvh.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),250)
   if hit and n.z>.85:samples.append([float(x),float(y),float(hit.z)])
 row['reference_samples']=samples;print(row['name'],len(samples),np.quantile(np.array(samples)[:,2],[.1,.5,.9]).tolist() if samples else None)
(R/'config/r176_measured_domains.json').write_text(json.dumps(domains,indent=2))
