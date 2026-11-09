import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend'));o=bpy.data.objects['R152_HISTORIC_WALL_453755312'];bm=bmesh.new();bm.from_mesh(o.data)
r=[dict(vertices=[list(v.co) for v in e.verts],faces=[dict(index=f.index,area=f.calc_area(),normal=list(f.normal),vertices=[list(v.co) for v in f.verts]) for f in e.link_faces]) for e in bm.edges if not e.is_manifold];(R/'reports/R334_EDGE_INSPECTION.json').write_text(json.dumps(r,indent=2));print(r)
