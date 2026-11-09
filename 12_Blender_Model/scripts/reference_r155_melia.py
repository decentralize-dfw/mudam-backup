from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/act_context/local_glb';out=R/'.local_source_cache/r155';out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rows=json.loads((D/'manifest.json').read_text())['tiles'];points=[];count=0
for r in rows:
 bounds=np.array(r['bounds_local']);lo=bounds.min(0);hi=bounds.max(0)
 if hi[0]<95 or lo[0]>160 or hi[1]<15 or lo[1]>82:continue
 bpy.ops.import_scene.gltf(filepath=str(D/r['file']));count+=1
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  p=np.array([o.matrix_world@v.co for v in o.data.vertices]);p=p[(p[:,0]>95)&(p[:,0]<160)&(p[:,1]>15)&(p[:,1]<82)];points.append(p)
np.savez_compressed(out/'melia_reference_points.npz',xyz=np.concatenate(points))
# Reference only.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75
for label,eye in [('melia_front',(205,-60,55)),('melia_top',(127,49,220)),('melia_back',(50,135,50))]:
 s.camera.location=eye;s.camera.rotation_euler=(Vector((127,49,20))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R155_source_{label}.png');bpy.ops.render.render(write_still=True)
print('MELIA_REFERENCE_READY',count,flush=True)


