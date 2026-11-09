import bpy,bmesh,re,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R571_SUR_ZEMIN_TEMAS_AO_BAKE_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 if not any(s in o.name for s in ['HISTORIC_WALL','RETAINING','RUIN_PARTITION','TOWER_BODY','FORT_MASONRY','MOAT','MASONRY_PLINTH','TOWER_CONICAL_ROOF']):continue
 bb=[o.matrix_world@Vector(v)for v in o.bound_box]
 if max(v.x for v in bb)<-90 or min(v.x for v in bb)>95 or max(v.y for v in bb)<-95 or min(v.y for v in bb)>95:continue
 bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=o.name,faces=len(bm.faces),boundary=sum(e.is_boundary for e in bm.edges),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),looseVertices=sum(not v.link_edges for v in bm.verts));bm.free();rows.append(row)
(R/'reports/R575_RING_STRUCTURAL_CLOSURE.json').write_text(json.dumps(rows,indent=2));print('STRUCTURES',len(rows));print([r for r in rows if r['nonManifold']or r['zeroArea']or r['looseVertices']])
