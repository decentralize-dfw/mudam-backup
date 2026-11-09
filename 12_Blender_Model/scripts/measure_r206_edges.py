from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r176_authored_parts.json').read_text());out=[]
for row in rows:
 if row['name'] not in ['NOVOTEL_HIGH','NOVOTEL_LOW']:continue
 row['top']=29.616134142344144 if row['name']=='NOVOTEL_HIGH' else 16.149557473219293
 p=row['outer'];records=[]
 for aa,bb in zip(p,p[1:]+p[:1]):
  a,b=Vector(aa),Vector(bb);u=(b-a).normalized();normal=Vector((-u.y,u.x));hits=[]
  for t in np.linspace(.1,.9,max(3,int((b-a).length/2))):
   for off in [-.5,-.25,0,.25,.5]:
    v=a.lerp(b,float(t))+normal*off;h,n,*_=g.ray_cast(Vector((v.x,v.y,100)),Vector((0,0,-1)),200)
    if h and row['top']+.05<h.z<row['top']+2:hits.append(float(h.z))
  records.append(dict(a=aa,b=bb,samples=hits,top=float(np.quantile(hits,.7)) if hits else None))
 good=[r['top'] for r in records if r['top'] is not None];out.append(dict(name=row['name'],roof=row['top'],edge_measurements=records,parapet_top=float(np.median(good)) if good else None,measured_edges=len(good),total_edges=len(records)))
(R/'reports/R206_ROOF_EDGE_MEASUREMENTS.json').write_text(json.dumps(out,indent=2));print([(r['name'],r['parapet_top'],r['measured_edges'],r['total_edges']) for r in out])

