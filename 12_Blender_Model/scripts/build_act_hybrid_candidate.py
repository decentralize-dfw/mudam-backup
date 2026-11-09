"""R151 candidate: accepted architecture with full-detail CC0 ACT environment."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'.local_source_cache/act_context';m=json.loads((SRC/'local_glb/manifest.json').read_text());cut=json.loads((ROOT/'reports/ACT2020_museum_cut_candidate.json').read_text());changed={r['file']:r for r in cut['changes']}
base=ROOT/'scenes/MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001.blend';version='v002' if '--v002' in sys.argv else 'v001';out=ROOT/'scenes'/f'MUDAM_R151_ACT_CEVRE_ADAY_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'scenes/MUDAM_ACT2020_SOURCE_REVIEW_v002.blend'))
for filename,c in changed.items():
 old=bpy.data.objects.get('ACT2020_'+Path(filename).stem);assert old,filename;bpy.data.objects.remove(old,do_unlink=True)
 if not c['empty']:
  bpy.ops.import_scene.gltf(filepath=str(SRC/cut.get('clipped_directory','clipped_glb')/filename))
  for o in bpy.context.selected_objects:
   if o.type=='MESH':o.name='ACT2020_'+Path(filename).stem
collection=bpy.data.collections.new('R151_ACT2020_PHOTOGRAMMETRY_CANDIDATE');bpy.context.scene.collection.children.link(collection);new=[]
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('ACT2020_') or o.type!='MESH':continue
 filename=o.name.removeprefix('ACT2020_')+'.glb';o.name='R151_ACT_'+Path(filename).stem
 for col in list(o.users_collection):col.objects.unlink(o)
 collection.objects.link(o);o['source_ids']='ACT_MESH3D_2020_CC0';o['status']='candidate_context_unaccepted';o['source_tile']=filename;new.append(o.name)
 for mat in o.data.materials:
  if hasattr(mat.cycles,'emission_sampling'):mat.cycles.emission_sampling='NONE'
S=bpy.context.scene
with bpy.data.libraries.load(str(base),link=False) as (data_from,data_to):data_to.scenes=[data_from.scenes[0]]
base_scene=data_to.scenes[0]
for col in base_scene.collection.children:S.collection.children.link(col)
for o in base_scene.collection.objects:S.collection.objects.link(o)
S.world=base_scene.world;hidden=[]
S.view_settings.view_transform=base_scene.view_settings.view_transform;S.view_settings.look=base_scene.view_settings.look;S.view_settings.exposure=base_scene.view_settings.exposure;S.view_settings.gamma=base_scene.view_settings.gamma
exported=set(json.loads((ROOT/'reports/P21_export_report.json').read_text())['selected_names'])
for o in base_scene.objects:
 if o.type=='MESH' and o.name not in exported:o.hide_render=True
 if o.type!='MESH' or o.hide_render:continue
 if '_TREE_' in o.name or o.name in ['R38_PARK_APPROACH_GROUND','R132_MAPPED_WOODLAND_GROUND','R35_MOAT_GROUND','R68_MOAT_GROUND'] or o.name.startswith('R68_WALL_') or (o.name.startswith('R35_WALL_') and not o.name.startswith('R35_WALL_51946353_')):
  hidden.append(o.name);o.hide_render=True;o['ACT2020_candidate_visibility']='Proxy context superseded for hybrid trial; data retained'
print('Context and architecture linked',len(new),len(hidden),flush=True)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=12;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R151 review');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;cd.clip_end=3000
for name,eye,target,lens in [('overview',(185,-285,295),(5,55,0),48),('museum',(92,-130,120),(0,5,0),48),('entry',(60,110,38),(10,35,-2),42)]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(ROOT/'renders/qa'/f'R151_{version}_candidate_{name}.png');bpy.ops.render.render(write_still=True)
recovery=False
try:bpy.ops.wm.save_as_mainfile(filepath=str(out))
except RuntimeError:
 temp=Path(str(out)+'@')
 if not out.exists() and temp.exists():temp.rename(out);recovery=True
 else:raise
r={'accepted':False,'file':str(out),'base_scene':base.name,'new_context_objects':new,'hidden_proxy_objects':hidden,'context_triangles':sum(len(bpy.data.objects[n].data.polygons) for n in new),'source_capture':2020,'datum_candidate':m['datum_ellipsoid_candidate'],'save_rename_recovery':recovery,'remaining':['Independent reopen','Museum-footprint seam and source facade removal inspection','Historic inner wall overlap check','Google Earth equivalent-detail comparison','Viewer integration and performance','Acceptance pipeline before release']}
(ROOT/'reports/R151_build_report.json').write_text(json.dumps(r,indent=2));print('R151_CANDIDATE_SAVED',flush=True)
