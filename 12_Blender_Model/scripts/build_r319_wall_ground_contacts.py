import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R318_KUZEY_HENDEK_TERAS_ADAY_v002.blend'))
t=bpy.data.objects['R152_CLASS2_TERRAIN'];t.data.calc_loop_triangles();bvh=BVHTree.FromPolygons([t.matrix_world@v.co for v in t.data.vertices],[list(f.vertices) for f in t.data.loop_triangles],all_triangles=True)
records=[];unresolved=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.name.startswith(('R152_HISTORIC_WALL_','R152_RUIN_PARTITION_')):continue
 bounds=[o.matrix_world@Vector(p) for p in o.bound_box]
 if any(p.x< -100 or p.x>85 or p.y< -105 or p.y>85 for p in bounds):continue
 groups={}
 for v in o.data.vertices:
  q=o.matrix_world@v.co;groups.setdefault((round(q.x,4),round(q.y,4)),[]).append((v,q))
 edits=[]
 for group in groups.values():
  lo=min(q.z for v,q in group);hi=max(q.z for v,q in group)
  if hi-lo<.2:continue
  for v,q in group:
   if abs(q.z-lo)>1e-5:continue
   hits=[]
   for dx,dy in [(0,0),(.45,0),(-.45,0),(0,.45),(0,-.45)]:
    h=bvh.ray_cast(Vector((q.x+dx,q.y+dy,100)),Vector((0,0,-1)),250)[0]
    if h:hits.append(h.z)
   if not hits:unresolved.append(dict(object=o.name,vertex=v.index,reason='No ground coverage'));continue
   ground=min(hits);gap=q.z-ground
   if gap<=.03:continue
   if gap>2:unresolved.append(dict(object=o.name,vertex=v.index,gap=gap,reason='Large discrepancy requires source section before extension'));continue
   old=q.z;q.z=ground-.15;v.co=o.matrix_world.inverted()@q;edits.append(dict(vertex=v.index,before=old,after=q.z,visibleGapBefore=gap))
 if edits:
  o.data.update();o['R319']='Lower wall edge extended to adjacent modeled ground; wall crests, widths, museum and terrain preserved. Not surveyed foundation depth.'
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);check=dict(boundary=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();records.append(dict(name=o.name,edits=edits,geometry=check))
assert records
out=R/'scenes/MUDAM_R319_SUR_ZEMIN_TEMAS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
bpy.ops.object.select_all(action='DESELECT')
for row in records:bpy.data.objects[row['name']].select_set(True)
glb=R/'exports/r152_clean/r319_wall_contacts_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R319_WALL_GROUND_CONTACTS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=records,unresolved=unresolved,glb=checks,limits=['Local model-contact correction, not surveyed heights','Large gaps excluded pending source validation','Entire marked museum ring still requires silhouette and level acceptance']),indent=2));print('R319_READY',len(records),'walls',sum(len(r['edits']) for r in records),'vertices',len(unresolved),'unresolved')
