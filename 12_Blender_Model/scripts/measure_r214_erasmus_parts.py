from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);origin=np.array([68.97819172183517,386.2917855717242]);u=np.array([.756,.654]);u/=np.linalg.norm(u);v=np.array([u[1],-u[0]])
def sample(a,b):
 p=origin+u*a+v*b;h,n,*_=g.ray_cast(Vector((p[0],p[1],80)),Vector((0,0,-1)),120);return float(h.z) if h and n.z>.7 else None
profile=[]
for a in np.arange(0,185,.25):
 zs=[sample(a,b) for b in [10,16,22]];valid=[z for z in zs if z is not None];profile.append(dict(u=float(a),heights=zs,mainRoof=len(valid)==3 and all(13<z<16.5 for z in valid)))
groups=[];current=[]
for r in profile+[dict(mainRoof=False)]:
 if r['mainRoof']:current.append(r)
 elif current:
  if len(current)>=12:groups.append(current)
  current=[]
parts=[]
for group in groups:
 a0=group[0]['u']-.125;a1=group[-1]['u']+.125;mid=(a0+a1)/2;cross=[dict(v=float(b),z=sample(mid,b)) for b in np.arange(-1,38,.25)]
 good=[r for r in cross if r['z'] is not None and 13<r['z']<16.5];parts.append(dict(u0=a0,u1=a1,v0=min(r['v'] for r in good),v1=max(r['v'] for r in good),roof=float(np.median([z for r in group for z in r['heights']])),cross=cross))
(R/'config/r214_erasmus_parts_measured.json').write_text(json.dumps(dict(origin=origin.tolist(),u=u.tolist(),v=v.tolist(),parts=parts,profile=profile),indent=2));print([(p['u0'],p['u1'],p['v0'],p['v1'],p['roof']) for p in parts])
