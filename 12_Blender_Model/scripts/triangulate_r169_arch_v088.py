from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'));removed=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];removed+=len(bad)
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES')
 bm.to_mesh(o.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
out=R/'exports/r152_clean/r169_architectural_v088_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out));deg=[];tri=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  if t.area<1e-10:deg.append(dict(object=o.name,area=t.area,vertices=[list(o.data.vertices[i].co) for i in t.vertices]))
p=R/'reports/R169_ARCH_GROUND_v088.json';d=json.loads(p.read_text());d.update(glb_bytes=out.stat().st_size,glb_triangles=tri,glb_degenerate_triangles=len(deg),degenerate_detail=deg,triangulation_zero_area_removed=removed);p.write_text(json.dumps(d,indent=2));print('TRIANGULATED',removed,'GLB',tri,'DEGENERATE',deg)
