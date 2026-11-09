"""Standalone full-detail source review; does not replace the accepted Mudam scene."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'.local_source_cache/act_context/local_glb'
m=json.loads((SRC/'manifest.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
selected=[]
for row in m['tiles']:
 bounds=row['bounds_local'];cx=sum(v[0] for v in bounds)/len(bounds);cy=sum(v[1] for v in bounds)/len(bounds)
 if '--full' in sys.argv or (-230<=cx<=230 and -220<=cy<=350):
  bpy.ops.import_scene.gltf(filepath=str(SRC/row['file']))
  for obj in bpy.context.selected_objects:
   obj.name='ACT2020_'+Path(row['file']).stem
  selected.append(row)
  if len(selected)%25==0:print('Imported',len(selected),flush=True)
# Use photo colour without a second baked-shadow contribution.
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 tree=mat.node_tree;tex=next((n for n in tree.nodes if n.type=='TEX_IMAGE'),None)
 out=next(n for n in tree.nodes if n.type=='OUTPUT_MATERIAL')
 if tex:
  em=tree.nodes.new('ShaderNodeEmission');tree.links.new(tex.outputs['Color'],em.inputs['Color']);tree.links.new(em.outputs[0],out.inputs['Surface'])
S.render.engine='CYCLES';S.cycles.samples=8
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU'
if '--full' in sys.argv:S.cycles.device='CPU'
S.world=bpy.data.worlds.new('Neutral background');S.world.color=(.08,.08,.08)
S.view_settings.view_transform='Standard'
S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('Source review');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.clip_end=3000
for key,eye,target,lens in [('overview',(460,-700,600) if '--full' in sys.argv else (310,-460,420),(0,70,0),44),('facades',(140,-50,130),(30,180,20),42)]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens
 suffix='full_' if '--full' in sys.argv else ''
 S.render.filepath=str(ROOT/'renders/qa'/f'ACT2020_source_{suffix}{key}.png');bpy.ops.render.render(write_still=True)
version='v002' if '--full' in sys.argv else 'v001'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scenes'/f'MUDAM_ACT2020_SOURCE_REVIEW_{version}.blend'))
(ROOT/'reports/ACT2020_source_preview.json').write_text(json.dumps({'accepted':False,'tiles':len(selected),'triangles':sum(r['triangles'] for r in selected),'full_detail_geometry':True,'render_material':'unlit phototexture for source review','datum':m['datum_ellipsoid_candidate'],'google_parity_verified':False},indent=2))
