from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r164';D.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rows=json.loads((R/'config/r164_building_targets.json').read_text())['buildings'];allxy=np.concatenate([b['rings'][0] for b in rows]);bboxlo=allxy.min(0)-5;bboxhi=allxy.max(0)+5
source=R/'.local_source_cache/act_context/local_glb'
for row in json.loads((source/'manifest.json').read_text())['tiles']:
 b=np.array(row['bounds_local']);lo=b.min(0);hi=b.max(0)
 if hi[0]<bboxlo[0] or lo[0]>bboxhi[0] or hi[1]<bboxlo[1] or lo[1]>bboxhi[1]:continue
 bpy.ops.import_scene.gltf(filepath=str(source/row['file']))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'source.blend'),compress=True)
dg=bpy.context.evaluated_depsgraph_get()
rows=json.loads((R/'config/r164_building_targets.json').read_text())['buildings']
for b in rows:
 p=np.array(b['rings'][0]);segments=np.roll(p,-1,axis=0)-p;v=segments[np.linalg.norm(segments,axis=1).argmax()];angle=np.arctan2(v[1],v[0]);rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);local=p@rot;lo=local.min(0)-3;hi=local.max(0)+3;step=.4
 xs=np.arange(lo[0],hi[0],step);ys=np.arange(lo[1],hi[1],step);z=np.full((len(ys),len(xs)),np.nan);norm=np.zeros_like(z)
 for j,y in enumerate(ys):
  for i,x in enumerate(xs):
   world=rot@np.array([x,y]);hit,q,n,*_=bpy.context.scene.ray_cast(dg,Vector((world[0],world[1],150)),Vector((0,0,-1)),distance=250)
   if hit:z[j,i]=q.z;norm[j,i]=n.z
 np.savez_compressed(D/(b['id']+'.npz'),x=xs,y=ys,z=z,normal=norm,angle=angle)
 print('SAMPLED',b['id'],z.shape,flush=True)
