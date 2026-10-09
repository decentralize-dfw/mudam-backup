from pathlib import Path
import runpy,json,sys,math
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parents[1];q=json.loads((B/'reports/KABUK_COK_KOTLU_TARAMA.json').read_text());sys.argv=['audit','--',q['file']];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));regions={r['id']:r['poly'] for r in g['regions']};regions['GH']=json.loads((B/'config/roof_revision.json').read_text())['outer_canonical'];p0=g['point']([0,0]);ax=g['point']([1,0])-p0;ay=g['point']([0,1])-p0;inv=Matrix(((ax.x,ay.x),(ax.y,ay.y))).inverted();out=[]
def cross(a,b):return a.x*b.y-a.y*b.x
for f in q['findings']:
 poly=regions[f['region']];a=math.radians(f['angle']);d=Vector((math.cos(a),math.sin(a),0));dc=inv@Vector((d.x,d.y));o=Vector(f['canonical']);hits=[]
 for i,(pa,pb) in enumerate(zip(poly,poly[1:]+poly[:1])):
  pa,pb=Vector(pa),Vector(pb);v=pb-pa;den=cross(dc,v)
  if abs(den)<1e-9:continue
  t=cross(pa-o,v)/den;u=cross(pa-o,dc)/den
  if t>0 and 0<=u<=1:hits.append((t,i,list(o+dc*t)))
 if hits:
  t,i,p=min(hits);near=g['tree'].find_nearest(g['point'](p,f['z']));out.append(dict(finding=f,boundary=i,edge=[poly[i],poly[(i+1)%len(poly)]],exit_canonical=p,nearest=g['names'][g['owners'][near[2]]],nearest_distance=near[3]))
(B/'reports/ENCLOSURE_BOUNDARY_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print('located',len(out))
