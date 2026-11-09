import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R571_SUR_ZEMIN_TEMAS_AO_BAKE_ADAY_v001.blend'));o=bpy.data.objects['R154_FORT_MASONRY_BODY'];bm=bmesh.new();bm.from_mesh(o.data);edges={e for e in bm.edges if e.is_boundary};loops=[]
while edges:
 start=next(iter(edges));todo=[start];group=set()
 while todo:
  e=todo.pop()
  if e in group:continue
  group.add(e);edges.discard(e)
  for v in e.verts:todo.extend(f for f in v.link_edges if f.is_boundary and f not in group)
 vv={v for e in group for v in e.verts};pts=[list(o.matrix_world@v.co)for v in vv];loops.append(dict(vertices=[v.index for v in vv],edges=[[v.index for v in e.verts]for e in group],points=pts,bounds=[[min(p[j]for p in pts)for j in range(3)],[max(p[j]for p in pts)for j in range(3)]]))
(R/'reports/R576_FORT_BODY_BOUNDARIES.json').write_text(json.dumps(loops,indent=2));print([(len(l['edges']),l['bounds'])for l in loops]);bm.free()
