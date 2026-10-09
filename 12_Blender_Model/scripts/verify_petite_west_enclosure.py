from pathlib import Path
import sys,json,runpy
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R87_build_report.json').read_text());sys.argv=['audit','--',r['file'],'8'];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));tree=g['tree'];point=g['point'];fail=[];checks=[]
def uv(p,z):return point([(p[0]+p[1])/2,(p[0]-p[1])/2],z)
route=r['route_uv']
for z in [r['upper_z']+.2,r['upper_z']+1.2,r['upper_z']+2.1]:
 for a,b in zip(route,route[1:]):
  pa,pb=uv(a,z),uv(b,z);hit=tree.ray_cast(pa,(pb-pa).normalized(),(pb-pa).length-.01);row=dict(a=a,b=b,z=z,hit=None if hit[0] is None else g['names'][g['owners'][hit[2]]]);checks.append(row)
  if row['hit']:fail.append(row)
for name in ['R87_global_audit.json','R87_inherited_verification.json']:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'];fail.extend(q['failures'])
q=json.loads((B/'reports/R87_enclosure_dense_summary.json').read_text());assert q['file']==r['file'];rows=[s for s in q['summaries'] if s['region'].startswith('PETITE')]
for row in rows:
 if any(row[k] for k in ['floor_missing','cover_missing','floor_below_expected','side_escape_samples']):fail.append(row)
result=dict(file=r['file'],route_checks=checks,dense_regions=rows,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R87_verification.json').write_text(json.dumps(result,indent=2));print('R87 route/dense',len(fail),'failures');assert not fail
