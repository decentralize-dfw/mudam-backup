"""Inspect full-scene enclosure contacts and circulation against saved source contours."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R101_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=r['upper_z'];r['file']='12_Blender_Model/scenes/MUDAM_R113_GALERI_SERVIS_UZUN_DUVARLARI_v001.blend';bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));studio=json.loads((B/'config/upper_studio.json').read_text());room=json.loads((B/'reports/R96_build_report.json').read_text())['documentation_east_room'];lift=json.loads((B/'config/upper_lift_landing.json').read_text());vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[]
def check(label,a,b,expected):
 va=pt(*a);vb=pt(*b);d=vb-va;hit=t.ray_cast(va,d.normalized(),d.length);rows.append(dict(id=label,a=a,b=b,hit=None if hit[0] is None else owners[hit[2]],passed=(hit[0] is not None)==expected))
def inside(p,poly):
 x,y=p;ok=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:ok=not ok
 return ok
for label,poly,height in [('studio',studio['inner_polygon'],2.7),('documentation_east',room,2.7),('lift_landing',lift['landing_polygon'],3.3)]:
 for x in range(math.ceil(min(p[0] for p in poly))+3,math.floor(max(p[0] for p in poly))-2,5):
  for y in range(math.ceil(min(p[1] for p in poly))+3,math.floor(max(p[1] for p in poly))-2,5):
   if not inside((x,y),poly):continue
   check(label+'_floor',(x,y,UP+.08),(x,y,UP-.3),True);check(label+'_ceiling',(x,y,UP+height-.1),(x,y,UP+height+.25),True)
for label,a,b in [('studio_to_reading',(515,640),(550,640)),('reading_to_east_room',(603,640),(635,640)),('bridge_to_reading',(576,580),(576,620)),('lift_landing_to_bridge',(666,545),(666,575))]:
 for h in [.25,1.1,2.05]:check(label,(*a,UP+h),(*b,UP+h),False)
q=dict(file=r['file'],checks=rows,failures=[x for x in rows if not x['passed']],construction_acceptance=False,limits=['Source-contour sampling detects local discontinuities; it is not final geometric or architectural acceptance.','Lift closed doorway and shaft excluded from open circulation probes.']);(B/'reports/R113_upper_front_inspection.json').write_text(json.dumps(q,indent=2));print(len(rows),'checks;',len(q['failures']),'failures');print(json.dumps(q['failures'][:30],indent=2))
