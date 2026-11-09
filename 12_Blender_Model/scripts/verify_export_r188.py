from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R188_UZAK_CEVRE_v001.blend'))
sources=json.loads((R/'config/r179_background_domains.json').read_text())+json.loads((R/'config/r188_background_domains.json').read_text());sources={str(r['id']):r for r in sources};records=[]
for o in bpy.context.scene.objects:
 o.select_set(False)
 if o.type!='MESH' or not o.name.startswith(('R179_BACKGROUND_','R188_BACKGROUND_')):continue
 rid=o.name.split('BACKGROUND_')[1];row=sources[rid];xy=row['outer']+[p for h in row['holes'] for p in h]
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);boundary=sum(e.is_boundary for e in bm.edges);bm.to_mesh(o.data);bm.free();o.data.calc_loop_triangles()
 err=max(min(math.hypot(v.co.x-x,v.co.y-y) for x,y in xy) for v in o.data.vertices);bad=sum(t.area<1e-10 for t in o.data.loop_triangles)
 assert not boundary and not bad and err<.001,(rid,boundary,bad,err)
 o.select_set(True);records.append(dict(id=rid,boundary_edges=boundary,degenerate=bad,maximum_footprint_error=err,height_source=row['height'],representation='Simple outside-scan massing, explicitly requested'))
assert len(records)==7,len(records)
path=R/'exports/r152_clean/r188_background_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));total=bad=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();total+=len(o.data.loop_triangles);bad+=sum(t.area<1e-10 for t in o.data.loop_triangles)
assert not bad
(R/'reports/R188_EXPORT_REOPEN.json').write_text(json.dumps(dict(reopened=True,buildings=records,triangles=total,degenerate=bad,accepted_scope='Closed source-footprint geometry for user-authorized simple outside-scan masses; not detailed architectural fidelity',full11regions_complete=False),indent=2))
