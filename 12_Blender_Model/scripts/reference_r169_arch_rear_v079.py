from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r169/facade_planes_v062.json').read_text());q=d['q'];side=d['sides'][0];a=Vector((*q[0],0));b=Vector((*q[1],0));n=Vector((*side['normal'],0));t=(b-a).normalized();plane=(a+b)/2+n*side['offset']
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'))
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);drop=[]
 for f in bm.faces:
  p=o.matrix_world@f.calc_center_median();along=(p-a).dot(t);dep=(p-plane).dot(n)
  if dep < -1.5 or dep>2.4 or along<-.5 or along>(b-a).length+.5 or p.z< -75 or p.z> -63:drop.append(f)
 bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free()
 for m in o.data.materials:
  if not m or not m.use_nodes:continue
  tex=next((x for x in m.node_tree.nodes if x.type=='TEX_IMAGE'),None)
  if tex:
   em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],m.node_tree.nodes.get('Material Output').inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.resolution_x=2200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('Reference');s.world.color=(0,0,0);s.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();s.camera=bpy.context.object;target=Vector((plane.x,plane.y,-69));s.camera.location=target+n*40;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=36;s.render.filepath=str(R/'renders/qa/R169_arch_rear_reference_v079.png');bpy.ops.render.render(write_still=True)
print('FRONT_REFERENCE',list(target),list(t),list(n))
