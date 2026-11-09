from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v002.blend'));s=bpy.context.scene;vs=[];fs=[]
for o in s.objects:
 if o.type=='MESH' and (o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND','R154_FAR_ROADS') or o.name.startswith(('R152_PATH_','R152_FORECOURT_'))):
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in t.vertices) for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);changes=[];missing=[]
for o in s.objects:
 if o.name.startswith('R157_TREE_'):
  p,n,i,dist=bvh.ray_cast(Vector((o.location.x,o.location.y,150)),Vector((0,0,-1)),400)
  if p is None:missing.append(o.name);continue
  old=o.location.z;o.location.z=p.z-.12;changes.append(abs(old-o.location.z))
assert not missing,missing
for name in ['R157_COMPACTED_MINERAL_PATH','R157_MATTE_ASPHALT','R157_PALE_PAVING']:
 m=bpy.data.materials[name];nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images['R157_ground_micro_normal.png'];normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.15;nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
out=R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for file,select in [('near_site',lambda o:o.name.startswith(('R152_','R154_')) or o.get('level_id')=='L00_APPROACH'),('vegetation',lambda o:o.name.startswith('R157_TREE_'))]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type=='MESH' and not o.hide_render and select(o):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean'/f'{file}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
r=json.loads((R/'reports/R157_BUILD.json').read_text());r.update(scene=out.name,tree_root_samples=len(changes),tree_roots_without_ground=missing,max_root_correction_m=max(changes));(R/'reports/R157_BUILD.json').write_text(json.dumps(r,indent=2));print('R157_GROUNDED',len(changes),max(changes),flush=True)
