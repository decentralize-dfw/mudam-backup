from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_BIRLESIM_v083.blend'));slate=bpy.data.materials['Authored slate - neutral unlit source color not copied'];plaster=bpy.data.materials['Mineral plaster provisional palette']
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);return o
# Close the bottom on the existing buried foundation plane; no aboveground doorway is filled.
f=json.loads((R/'.local_source_cache/r169/facade_planes_v062.json').read_text());import numpy as np
q=np.array(f['q']);walls=[]
for k in range(4):
 a=f['sides'][(k-1)%4];b=f['sides'][k];na=np.array(a['normal']);nb=np.array(b['normal']);walls.append(np.linalg.solve(np.array([na,nb]),[na@q[(k-1)%4]+a['offset'],nb@q[k]+b['offset']]))
mesh('ARCH_BURIED_BASE_SLAB',[(*p,-75) for p in walls],[(0,1,2,3)],plaster)
projection=[]
for name in ['ARCH_REAR_PROJECTION_WALL_0','ARCH_REAR_PROJECTION_WALL_1','ARCH_REAR_PROJECTION_WALL_3']:
 for v in bpy.data.objects[name].data.vertices:
  if v.co.z< -74.9 and not any((v.co-p).length<.001 for p in projection):projection.append(v.co.copy())
mid=sum(projection,Vector())/len(projection);projection.sort(key=lambda v:math.atan2(v.y-mid.y,v.x-mid.x));mesh('ARCH_REAR_PROJECTION_BASE',projection,[list(range(len(projection)))],plaster)
# Exact front band-foot return, including the horizontal offset to the wall.
band=bpy.data.objects['ARCH_FRONT_MANSARD_BAND'];low=min(v.co.z for v in band.data.vertices);pts=[v.co.copy() for v in band.data.vertices if abs(v.co.z-low)<.001];t=Vector((.9779602885,.2087912709,0));n=Vector((.208791494,-.977960169,0));a=min(pts,key=lambda p:p.dot(t));b=max(pts,key=lambda p:p.dot(t));plane=Vector((-78.6563873,-306.0042725,-69));outer=[]
for p in [a,b]:
 w=p-n*(p-plane).dot(n);w.z=-65.5;outer.append(w)
mesh('ARCH_FRONT_BAND_EXACT_RETURN',[a,b,outer[1],outer[0]],[(0,1,2,3)],slate)
# Front corner closures use the actual end-wall top and band end, not arbitrary fill.
for idx,p in enumerate([a,b]):
 corner=min(walls[2:],key=lambda v:(Vector((*v,-65.5))-p).length);foot=Vector((*corner,-65.5));endwall=bpy.data.objects['ARCH_WALL_MASS_'+('3' if idx==0 else '1')];tops=[v.co for v in endwall.data.vertices if v.co.z>-70];top=min(tops,key=lambda v:(v.xy-foot.xy).length);roofverts=[v.co for o in bpy.context.scene.objects if o.name.startswith('ARCH_MAIN_ROOF') for v in o.data.vertices];rp=min(roofverts,key=lambda v:(v.xy-p.xy).length);mesh('ARCH_FRONT_CORNER_CLOSURE_'+str(idx),[foot,top.copy(),rp.copy(),p],[(0,1,2,3)],slate)
# Save/reopen before coverage testing.
path=R/'scenes/MUDAM_R169_MIMARI_KAPALI_KABUK_ADAY_v084.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in me.vertices);fs.extend([off+i for i in tri.vertices] for tri in me.loop_triangles);ev.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);miss=[];rays=0
for u in [.15,.35,.55,.75,.9]:
 xy=(q[0]*(1-u)+q[1]*u+q[3]*(1-u)+q[2]*u)/2
 for z in [-74,-72,-70,-68,-66,-64.5]:
  p=Vector((*xy,z))
  for elev in [-90,-60,-30,0,30,60,90]:
   for az in range(0,360,5 if abs(elev)<90 else 360):
    th=math.radians(az);el=math.radians(elev);direction=Vector((math.cos(el)*math.cos(th),math.cos(el)*math.sin(th),math.sin(el)));hit,*_=tree.ray_cast(p,direction,120);rays+=1
    if hit is None:miss.append(dict(origin=list(p),direction=list(direction),elevation=elev,azimuth=az))
report=dict(accepted=False,reopened=True,coverage_rays=rays,misses=len(miss),worst=miss,scope='Finite interior directional sampling detects gaps; not proof of complete watertight manifold or source fidelity. No scan geometry imported.');(R/'reports/R169_SHELL_COVERAGE_v084.json').write_text(json.dumps(report,indent=2));print('COVERAGE',rays,'MISSES',len(miss))
