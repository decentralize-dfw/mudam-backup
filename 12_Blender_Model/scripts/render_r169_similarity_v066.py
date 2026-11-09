from pathlib import Path
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[1];views=[('rear',(-100,-270,-36)),('front',(-55,-335,-35)),('top',(-80,-301,-15))]
def setup():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=900;s.render.resolution_y=750;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1;s.world=bpy.data.worlds.new('BLACK');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=0
 for o in list(s.objects):
  if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48
 return s
def render(s,tag):
 for name,pos in views:
  s.camera.location=pos;s.camera.rotation_euler=(Vector((-80,-301,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('renders/qa/R169_similarity_v066_'+tag+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
def unlit():
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  nt=m.node_tree;t=next((n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image),None);out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
  if not out:continue
  em=nt.nodes.new('ShaderNodeEmission')
  vc=next((n for n in nt.nodes if n.type=='VERTEX_COLOR'),None)
  if vc:nt.links.new(vc.outputs['Color'],em.inputs['Color'])
  elif t:nt.links.new(t.outputs['Color'],em.inputs['Color'])
  else:em.inputs['Color'].default_value=m.diffuse_color
  nt.links.new(em.outputs[0],out.inputs['Surface'])
for tag,path in [('source',R/'.local_source_cache/r169/source.blend'),('model',R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v066.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=setup();unlit();render(s,tag)
 if tag=='model':
  mats=[]
  for color in [(0,0,0,1),(1,1,1,1)]:
   m=bpy.data.materials.new('MASK');m.use_nodes=True;nt=m.node_tree;em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=color;nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface']);mats.append(m)
  for o in s.objects:
   if o.type!='MESH':continue
   o.data.materials.clear();o.data.materials.append(mats[int(o.name=='R169_WHOLE_SOURCE_ROOF')])
  render(s,'mask')
print('COMPARISON_RENDERED')



