from pathlib import Path
import sys,runpy,json,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];sys.argv=['audit','--',args[0]];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));tree=g['tree'];r=json.loads((B/'reports/R14_build_report.json').read_text());rows=[]
for step in r['steps']:
 for f in [-.42,-.2,0,.2,.42]:
  p=Vector(step['center'])+Vector(step['side'])*step['width']*f
  cover=tree.ray_cast(p+Vector((0,0,1.2)),Vector((0,0,1)),40)
  misses=[]
  for z in [.15,1.2,2.1]:
   for angle in range(0,360,15):
    hit=tree.ray_cast(p+Vector((0,0,z)),Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0)),200)
    if hit[0] is None:misses.append(dict(z=z,angle=angle))
  if cover[0] is None or misses:rows.append(dict(step=step['name'],fraction=f,position=list(p),cover_missing=cover[0] is None,escapes=misses))
q=dict(file=args[0],samples=len(r['steps'])*5,side_rays=len(r['steps'])*5*72,findings=rows,limits=['Source R14 tread sample positions; geometry closure diagnostic only.','Real stair geometry, counts and dimensions remain conditional.']);(B/'reports/BATI_MERDIVEN_KABUK_TARAMA.json').write_text(json.dumps(q,indent=2));print('stair findings',len(rows))
