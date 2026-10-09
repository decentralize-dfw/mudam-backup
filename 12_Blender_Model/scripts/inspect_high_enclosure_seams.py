from pathlib import Path
import runpy,json,sys,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];q=json.loads((B/'reports/KABUK_COK_KOTLU_TARAMA.json').read_text());sys.argv=['audit','--',q['file']];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));out=[];selected=[q['findings'][i] for i in [0,2,26,44,45,52,70,-1]]
for f in selected:
 rays=[]
 for da in [-.5,-.1,-.01,0,.01,.1,.5]:
  a=f['angle']+da;d=Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0));hit=g['tree'].ray_cast(g['point'](f['canonical'],f['z']),d,200);rays.append(dict(da=da,name=None if hit[0] is None else g['names'][g['owners'][hit[2]]],distance=hit[3],world=None if hit[0] is None else list(hit[0])))
 out.append(dict(finding=f,rays=rays))
(B/'reports/ENCLOSURE_HIGH_SEAM_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
