from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'));q=np.array(json.loads((R/'.local_source_cache/r169/facade_planes_v062.json').read_text())['q'])
vs=[];fs=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in me.vertices);fs.extend([off+i for i in tri.vertices] for tri in me.loop_triangles);ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);miss=[];rays=0
for u in [.08,.15,.25,.35,.45,.55,.65,.75,.85,.92]:
 xy=(q[0]*(1-u)+q[1]*u+q[3]*(1-u)+q[2]*u)/2
 for z in [-74,-72,-70,-68,-66,-64.5]:
  p=Vector((*xy,z))
  for elev in [-90,-75,-60,-45,-30,-15,0,15,30,45,60,75,90]:
   for az in range(0,360,2 if abs(elev)<90 else 360):
    th=math.radians(az);el=math.radians(elev);direction=Vector((math.cos(el)*math.cos(th),math.cos(el)*math.sin(th),math.sin(el)));hit,*_=tree.ray_cast(p,direction,120);rays+=1
    if hit is None:miss.append(dict(origin=list(p),direction=list(direction),elevation=elev,azimuth=az))
report=dict(accepted=False,reopened=True,coverage_rays=rays,misses=len(miss),worst=miss,scope='Finite interior directional sampling detects gaps; not proof of complete watertight manifold or source fidelity. No scan geometry imported.');(R/'reports/R169_SHELL_COVERAGE_v088.json').write_text(json.dumps(report,indent=2));print('COVERAGE',rays,'MISSES',len(miss))
