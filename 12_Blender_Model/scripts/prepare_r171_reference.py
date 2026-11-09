from pathlib import Path
import bpy,json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r171';D.mkdir(exist_ok=True);src=R/'.local_source_cache/act_context/local_glb';bpy.ops.wm.read_factory_settings(use_empty=True);points=[];count=0
for tile in json.loads((src/'manifest.json').read_text())['tiles']:
 bounds=np.array(tile['bounds_local']);lo=bounds.min(0);hi=bounds.max(0)
 if hi[0]<-510 or lo[0]>610 or hi[1]<-560 or lo[1]>-100:continue
 bpy.ops.import_scene.gltf(filepath=str(src/tile['file']))
 for obj in list(bpy.context.scene.objects):
  if obj.type=='MESH':
   points.extend(tuple(obj.matrix_world@v.co) for v in obj.data.vertices)
  bpy.data.objects.remove(obj,do_unlink=True)
 count+=1
np.savez_compressed(D/'lower_reference.npz',xyz=np.array(points,dtype=np.float32));print('SOURCE_SCALARS_REFERENCE',count,len(points))

