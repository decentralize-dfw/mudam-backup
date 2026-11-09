from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'];b=rows[0];p=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]]
for edge in [3,0,1,2]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'))
 a=p[edge];z=p[(edge+1)%4];t=(z-a).normalized();inside=Vector((t.y,-t.x,0));out=-inside;center=(a+z)*.5;length=(z-a).length
 offsets={0:-.35,1:1.8,2:1.15,3:-.45};plane=center+inside*offsets[edge]
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data);drop=[]
  for f in bm.faces:
   q=o.matrix_world@f.calc_center_median();d=q-plane;along=(q-a).dot(t)
   if abs(d.dot(inside))>1.1 or along<-.5 or along>length+.5 or q.z<b['base']+.5 or q.z>b['base']+15:drop.append(f)
  bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free()
  for m in o.data.materials:
   if not m or not m.use_nodes:continue
   nt=m.node_tree;tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE'),None)
   if tex:
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('REF');s.world.color=(.12,.12,.12)
 bpy.ops.object.camera_add();s.camera=bpy.context.object;target=plane+Vector((0,0,b['base']+7.5));s.camera.location=target+out*35;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=max(length+3,26);s.view_settings.view_transform='Standard';s.render.filepath=str(R/f'renders/qa/R169_33_facade_{edge}_source.png');bpy.ops.render.render(write_still=True)
print('FACADE_REFERENCES_SAVED')
