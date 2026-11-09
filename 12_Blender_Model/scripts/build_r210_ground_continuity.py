from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R209_NOVOTEL_CATILAR_v001.blend'))
coverage=json.loads((R/'config/r210_ground_coverage.json').read_text());vs=[];fs=[]
for r in coverage:
 for t in r['triangles']:
  k=len(vs);vs.extend(t);fs.append((k,k+1,k+2))
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for r in raw['meshes']:
 k=len(vs);vs.extend(r['vertices']);fs.extend([k+i for i in f] for f in r['faces'])
original=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r210_ground_missing.json').read_text());records=[]
for r in rows:
 vs=[];fs=[];distances=[]
 for t in r['triangles']:
  k=len(vs)
  for x,y in t:
   h=original.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)[0]
   if h is None:raise RuntimeError('No original terrain datum')
   # Match reconstructed boundary height, not an arbitrary horizontal patch.
   near=g.find_nearest(h,3)
   z=near[0].z if near[0] is not None and (near[0].xy-Vector((x,y))).length<.002 else h.z
   distances.append(abs(z-h.z));vs.append((x,y,z))
  fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new('R210_GROUND_CONTINUITY_%02d'%r['id']);me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['R157_CONTINUOUS_LANDCOVER']);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001)
 for f in bm.faces:
  if f.normal.z<0:f.normal_flip()
 bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.new(name='UVMap');micro=me.uv_layers.new(name='MicroUV')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+500)/1150,(v.y+450)/1100);micro.data[li].uv=(v.x/6,v.y/6)
 me.uv_layers.active_index=0;o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
 records.append(dict(name=o.name,area=r['area'],maximum_boundary_adjustment=max(distances),triangles=len(me.polygons)))
s=bpy.context.scene;bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R210_KUZEY_ZEMIN_SUREKLILIGI_v001.blend'),compress=True)
(R/'reports/R210_GROUND_CONTINUITY.json').write_text(json.dumps(dict(accepted=False,missing_domains=records,area=sum(r['area'] for r in records),scope='Only bounded accidental terrain coverage gaps outside mapped building footprints; original DEM and adjoining boundary heights',full11RegionsAccepted=False),indent=2))
s.render.filepath=str(R/'renders/qa/R210_ground_continuity_v001.png');bpy.ops.render.render(write_still=True)
