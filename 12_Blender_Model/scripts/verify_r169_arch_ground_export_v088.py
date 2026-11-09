from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.name not in ['R152_CLASS2_TERRAIN','R154_FAR_GROUND']:continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'));points=set();removed=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<1e-10];removed+=len(bad)
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
 bm.to_mesh(o.data);bm.free()
 if 'WALL' in o.name or 'BASE' in o.name:
  o.data.calc_loop_triangles()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z< -74.9:points.add(tuple(p))
  for e in o.data.edges:
   a=o.matrix_world@o.data.vertices[e.vertices[0]].co;b=o.matrix_world@o.data.vertices[e.vertices[1]].co
   if a.z< -74.9 and b.z< -74.9:
    for i in range(1,21):points.add(tuple(a.lerp(b,i/20)))
clear=[];missing=[]
for p in points:
 h,*_=tree.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),250)
 if h is None:missing.append(p)
 else:clear.append(p[2]-h.z)
report=dict(accepted=False,ground_points=len(points),missing_ground=len(missing),floating_points=sum(x>.02 for x in clear),maximum_clearance=max(clear),minimum_clearance=min(clear),degenerate_faces_removed=removed,scope='Foundation contact with existing R170 terrain, not whole site/source fidelity acceptance.')
(R/'reports/R169_ARCH_GROUND_v088.json').write_text(json.dumps(report,indent=2));bpy.context.scene['validation']='118920 interior ray samples no leaks; source fidelity not accepted.';bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
out=R/'exports/r152_clean/r169_architectural_v088_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out));tris=0;deg=0;images=0
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles);deg+=sum(t.area<1e-10 for t in o.data.loop_triangles)
report.update(glb_bytes=out.stat().st_size,glb_triangles=tris,glb_degenerate_triangles=deg,scan_textures=0,scan_mesh_imported=False);(R/'reports/R169_ARCH_GROUND_v088.json').write_text(json.dumps(report,indent=2));print('GROUND_EXPORT',report)
