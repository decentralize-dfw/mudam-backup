from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r159/scaled_trees.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R158_ACT_ORMAN_ORTUSU_v003.blend'));checked=[];removed=[]
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and (o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND','R154_FAR_ROADS') or o.name.startswith(('R152_PATH_','R152_FORECOURT_'))):
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+k for k in tri.vertices) for tri in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
for i,t in enumerate(d['trees']):
 o=bpy.data.objects[f'R158_TREE_{i:05d}'];low,high=t['canopy_patch_bounds_xy'];root=o.location.z;target_top=t['source_top_z']
 local=[Vector(c) for c in o.bound_box];mins=[min(v[k] for v in local) for k in range(3)];maxs=[max(v[k] for v in local) for k in range(3)];o.rotation_euler=(0,0,0);o.scale=((high[0]-low[0])/(maxs[0]-mins[0]),(high[1]-low[1])/(maxs[1]-mins[1]),(target_top-root)/(maxs[2]-mins[2]));o.location=(low[0]-mins[0]*o.scale.x,low[1]-mins[1]*o.scale.y,root-mins[2]*o.scale.z)
 hit,_,_,_=bvh.ray_cast(Vector((o.location.x,o.location.y,150)),Vector((0,0,-1)),450);assert hit is not None
 root=hit.z-.12
 if target_top<=root+1:
  removed.append({'name':o.name,'source_top':target_top,'ground':root+.12});bpy.data.objects.remove(o,do_unlink=True);continue
 o.scale.z=(target_top-root)/(maxs[2]-mins[2]);o.location.z=root-mins[2]*o.scale.z
 o['source']=t['source'];o['source_top_z']=target_top;o['source_patch_xy']=json.dumps([low,high]);checked.append(o.name)
bpy.context.view_layer.update();errors=[]
for i,t in enumerate(d['trees']):
 o=bpy.data.objects.get(f'R158_TREE_{i:05d}');
 if o is None:continue
 world=[o.matrix_world@Vector(c) for c in o.bound_box];actual=[min(v.x for v in world),min(v.y for v in world),max(v.x for v in world),max(v.y for v in world),max(v.z for v in world)];low,high=t['canopy_patch_bounds_xy'];expected=[*low,*high,t['source_top_z']];errors.append(max(abs(x-y) for x,y in zip(actual,expected)))
assert max(errors)<.001,max(errors)
out=R/'scenes/MUDAM_R159_KAYNAK_ORTU_OLCEGI_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out))
for name in checked:
 o=bpy.data.objects[name];top=max((o.matrix_world@Vector(c)).z for c in o.bound_box);assert abs(top-o['source_top_z'])<.001
bpy.ops.object.select_all(action='DESELECT')
for n in checked:bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/vegetation.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
(R/'reports/R159_SCALE_QA.json').write_text(json.dumps({'scene':out.name,'removed_low_surface_false_positives':removed,'source_patch_count':len(checked),'max_source_patch_envelope_error_m':max(errors),'source_raster_resolution_m':2,'individual_tree_identity_verified':False,'roads_buildings_modified':False,'whole_context_complete':False},indent=2));print('R159_SCALED',len(checked),max(errors),flush=True)
