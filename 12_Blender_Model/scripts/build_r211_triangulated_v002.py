from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v001.blend'));report=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('R176_','R190_','R201_','R206_','R209_')):continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');before=sum(f.calc_area()<1e-10 for f in bm.faces)
 bmesh.ops.dissolve_degenerate(bm,dist=.00001,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
 after=sum(f.calc_area()<1e-10 for f in bm.faces);boundary=sum(e.is_boundary for e in bm.edges);bm.to_mesh(o.data);bm.free();report.append(dict(name=o.name,zeroBefore=before,zeroAfter=after,boundary=boundary))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v002.blend'),compress=True)
(R/'reports/R211_TRIANGULATED_v002.json').write_text(json.dumps(report,indent=2));print([r for r in report if r['zeroBefore'] or r['zeroAfter'] or r['boundary']])
