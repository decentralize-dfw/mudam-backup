from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
parent=R/'scenes/MUDAM_R168_DOGU_KAVSAK_ADAY_v002.blend'
scene=R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'

def signature(o):
 m=o.data
 d=[list(sum((list(row) for row in o.matrix_world),[])),[list(v.co) for v in m.vertices],[(list(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],[[list(v.uv) for v in layer.data] for layer in m.uv_layers],[v.name if v else None for v in m.materials],o.hide_render]
 return hashlib.sha256(json.dumps(d).encode()).hexdigest()
def meshstats(objects):
 points=[];n=0;bad=0
 for o in objects:
  o.data.calc_loop_triangles();n+=len(o.data.loop_triangles);bad+=sum(t.area<1e-9 for t in o.data.loop_triangles)
  points.extend(tuple(o.matrix_world@v.co) for v in o.data.vertices)
 assert all(math.isfinite(c) for p in points for c in p)
 return dict(triangles=n,degenerate=bad,min=[min(p[k] for p in points) for k in range(3)],max=[max(p[k] for p in points) for k in range(3)])
bpy.ops.wm.open_mainfile(filepath=str(parent));original={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(scene));current={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
assert set(current)-set(original)=={'R170_SOURCE_ISLAND_CURB'}
assert all(current.get(n)==h for n,h in original.items())
curb=bpy.data.objects['R170_SOURCE_ISLAND_CURB'];bm=bmesh.new();bm.from_mesh(curb.data);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume();assert volume>0;bm.free()
road=bpy.data.objects['R168_SOURCE_JUNCTION'];road.data.calc_loop_triangles();tree=BVHTree.FromPolygons([road.matrix_world@v.co for v in road.data.vertices],[list(t.vertices) for t in road.data.loop_triangles],all_triangles=True)
offsets=[];widths=[]
for i,v in enumerate(curb.data.vertices):
 p=curb.matrix_world@v.co;h,*_=tree.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),400);assert h is not None
 dz=p.z-h.z;offsets.append(dz);expected=.12 if i%4 in (1,2) else -.005;assert abs(dz-expected)<.0001
 if i%4==1:
  q=curb.data.vertices[i+1].co;widths.append(math.hypot(q.x-p.x,q.y-p.y))
assert max(abs(w-.18) for w in widths)<.0001
names=['R162_MEASURED_ENVELOPE','R164_MEASURED_ENVELOPE','R165_MEASURED_ENVELOPE','R166_MEASURED_ENVELOPE','R167_MEASURED_ENVELOPE','R161_ROAD_CONNECTIONS','R168_SOURCE_JUNCTION','R170_SOURCE_ISLAND_CURB']
bpy.ops.object.select_all(action='DESELECT');objects=[bpy.data.objects[n] for n in names]
for o in objects:o.select_set(True)
before=meshstats(objects);assert before['degenerate']==0
out=R/'exports/r152_clean/r170_district.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out));after=meshstats([o for o in bpy.context.scene.objects if o.type=='MESH'])
assert before['triangles']==after['triangles'] and after['degenerate']==0
error=max(abs(before[k][i]-after[k][i]) for k in ['min','max'] for i in range(3));assert error<.001
report=dict(parent=parent.name,scene=scene.name,inherited_meshes_unchanged=len(original),added_meshes=['R170_SOURCE_ISLAND_CURB'],closed_manifold=True,volume_m3=volume,ground_samples=len(offsets),bottom_offset_m=-.005,top_offset_m=.12,width_m=.18,section_is_assumed=True,before=before,after=after,max_bounds_drift_m=error,glb_bytes=out.stat().st_size,glb_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),technical_pass=True,visual_acceptance=False)
(R/'reports/R170_GEOMETRY_GLB_CHECK.json').write_text(json.dumps(report,indent=2));print('R170_VERIFIED',report,flush=True)
