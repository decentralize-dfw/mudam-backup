from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True);p=R/'exports/r152_clean/r171_lower_district_REVIEW.glb';bpy.ops.import_scene.gltf(filepath=str(p));tris=bad=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles);bad+=sum(t.area<1e-10 for t in o.data.loop_triangles)
d=json.loads((R/'reports/R171_HARDSCAPE_v002.json').read_text());print('RESULT',len(d['buildings']),sum('vertices' in v for v in d['hardscape']),sum(v['boundaryEdges'] for v in d['buildings']),p.stat().st_size,tris,bad)
(R/'reports/R171_GLB_v002.json').write_text(json.dumps(dict(reopened=True,bytes=p.stat().st_size,triangles=tris,degenerateTriangles=bad,accepted=False),indent=2))
