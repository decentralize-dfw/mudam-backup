from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R210_KUZEY_ZEMIN_SUREKLILIGI_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('R176_','R186_','R201_','R206_','R190_','R209_','R200_','R205_')):continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001)
 out.append(dict(name=o.name,faces=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R211_ENVELOPE_AUDIT.json').write_text(json.dumps(out,indent=2));print([r for r in out if r['boundary'] or r['zero_faces']])
