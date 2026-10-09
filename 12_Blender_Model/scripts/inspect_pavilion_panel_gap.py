from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R85_BATI_UST_SAHANLIK_KABUK_v001.blend'));r=json.loads((B/'reports/R13_build_report.json').read_text());print(r.keys());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(x,y):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,1.2))
rows=[]
for y in [276,278,280,282]:
 hits=[]
 for pane in r['panels']:
  ps=[Vector(p) for p in pane['source_polygon']];t=BVHTree.FromPolygons(ps,[tuple(range(len(ps)))]);h=t.ray_cast(point(139,y),Vector((0,0,1)),45)
  if h[0] is not None:hits.append(dict(name=pane['name'],z=h[0].z))
 rows.append(dict(canonical=[139,y],source_panel_hits=hits))
(B/'reports/PAVILION_PANEL_GAP_DIAGNOSTIC.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
