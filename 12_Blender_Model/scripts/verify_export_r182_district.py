from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R182_GENIS_ARAZI_MAHALLE_v002.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.name not in ['R154_FAR_GROUND','R154_FAR_ROADS']:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);seams=[]
for o in bpy.context.scene.objects:
 if not o.name.startswith('R182_EXTENSION_'):continue
 for v in o.data.vertices:
  x,y=v.co.x,v.co.y
  boundary=((abs(x+500)<.001 or abs(x-650)<.001) and -450.001<=y<=650.001) or ((abs(y+450)<.001 or abs(y-650)<.001) and -500.001<=x<=650.001)
  if boundary:
   h,*_=bvh.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),400)
   if h:seams.append(abs(v.co.z-h.z));v.co.z=h.z
 for l in o.data.loops:v=o.data.vertices[l.vertex_index].co;o.data.uv_layers.active.data[l.index].uv=(v.x/6,v.y/6)
selected=[];records=[]
for o in bpy.context.scene.objects:
 include=o.type=='MESH' and (o.name.startswith(('R171_','R173_','R174_','R182_DISTRICT_','R182_EXTENSION_')))
 o.select_set(include)
 if not include:continue
 selected.append(o);o.data.calc_loop_triangles();bad=sum(t.area<1e-10 for t in o.data.loop_triangles)
 isbuilding=(o.name.startswith(('R171_','R174_')) and o.name[5:].isdigit()) or o.name.startswith('R182_DISTRICT_')
 boundary=0
 if isbuilding:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001);boundary=sum(e.is_boundary for e in bm.edges);bm.free()
 records.append(dict(name=o.name,triangles=len(o.data.loop_triangles),degenerate=bad,building=isbuilding,boundary_edges=boundary))
assert not any(r['boundary_edges'] for r in records if r['building'])
assert all(math.isfinite(v) for o in selected for p in o.data.vertices for v in p.co)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R182_GENIS_ARAZI_MAHALLE_v003.blend'),compress=True)
path=R/'exports/r152_clean/r182_district_terrain_REVIEW.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
report=dict(accepted=False,source_scene='MUDAM_R182_GENIS_ARAZI_MAHALLE_v003.blend',objects=records,buildings=sum(r['building'] for r in records),boundary_adjustments=len(seams),maximum_boundary_correction=max(seams,default=0),bytes=path.stat().st_size,pending=['GLB reopen and compression','Source footprint verification','No acceptance of unrelated fort/northern architecture candidates'])
(R/'reports/R182_EXPORT_v003.json').write_text(json.dumps(report,indent=2));print('R182_EXPORT',report['buildings'],report['bytes'],sum(r['degenerate'] for r in records))
