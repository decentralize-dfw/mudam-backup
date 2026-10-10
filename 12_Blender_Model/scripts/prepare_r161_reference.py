from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r161';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R159_KAYNAK_ORTU_OLCEGI_v001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('R154_FAR_GROUND','R154_FAR_ROADS','R152_CLASS2_TERRAIN','R152_PATH_','R152_FORECOURT_')):
  o.data.calc_loop_triangles();rows.append(dict(name=o.name,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],faces=[list(t.vertices) for t in o.data.loop_triangles]))
(D/'surfaces.json').write_text(json.dumps(rows))
bpy.ops.wm.read_factory_settings(use_empty=True)
source=R/'.local_source_cache/act_context/local_glb';pts=[]
for row in json.loads((source/'manifest.json').read_text())['tiles']:
 b=np.array(row['bounds_local']);lo=b.min(0);hi=b.max(0)
 if hi[0]<-300 or lo[0]>140 or hi[1]<290 or lo[1]>460:continue
 bpy.ops.import_scene.gltf(filepath=str(source/row['file']))
for o in bpy.context.scene.objects:
 if o.type=='MESH':pts.append(np.array([o.matrix_world@v.co for v in o.data.vertices]))
np.savez_compressed(D/'reference.npz',xyz=np.concatenate(pts))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=440
for label,eye in [('top',(-90,375,400)),('front',(-10,60,140))]:
 s.camera.location=eye;s.camera.rotation_euler=(Vector((-90,375,20))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R161_reference_{label}.png');bpy.ops.render.render(write_still=True)
print('R161_REFERENCE_READY',flush=True)
