from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r165';D.mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);source=R/'.local_source_cache/act_context/local_glb'
for row in json.loads((source/'manifest.json').read_text())['tiles']:
 b=np.array(row['bounds_local']);lo=b.min(0);hi=b.max(0)
 if hi[0]<200 or lo[0]>280 or hi[1]<295 or lo[1]>445:continue
 bpy.ops.import_scene.gltf(filepath=str(source/row['file']))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'source.blend'),compress=True);dg=bpy.context.evaluated_depsgraph_get()
for ident,bounds in [('north_tower_a',[210,304,250,358]),('north_tower_b',[218,376,274,440])]:
 x=np.arange(bounds[0],bounds[2],.4);y=np.arange(bounds[1],bounds[3],.4);z=np.full((len(y),len(x)),np.nan);normal=np.zeros_like(z)
 for j,yy in enumerate(y):
  for i,xx in enumerate(x):
   hit,p,n,*_=bpy.context.scene.ray_cast(dg,Vector((xx,yy,200)),Vector((0,0,-1)),distance=300)
   if hit:z[j,i]=p.z;normal[j,i]=n.z
 np.savez_compressed(D/(ident+'.npz'),x=x,y=y,z=z,normal=normal,angle=0.)
 print('TOWER_SAMPLED',ident,flush=True)
