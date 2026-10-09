"""Multi-height, multi-direction envelope diagnostic. Findings require source classification."""
from pathlib import Path
import runpy,json,sys,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['12_Blender_Model/scenes/MUDAM_R82_BATI_MERDIVEN_GIRIS_KABUK_v001.blend'];sys.argv=['audit','--',args[0]];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));tree=g['tree'];point=g['point'];summaries=[];findings=[];count=0
for reg in g['regions']:
 rows=[r for r in g['rows'] if r['region']==reg['id']];tested=0;escapes=0
 for row in rows[::2]:
  xy=row['canonical'];heights=[reg['z']+.15,reg['z']+2.1]
  if row['cover_hit'] and row['cover_hit']['z']>reg['z']+2.4:heights.append(row['cover_hit']['z']-.08)
  for z in heights:
   for a in range(0,360,15):
    tested+=1;count+=1;d=Vector((math.cos(math.radians(a)),math.sin(math.radians(a)),0));hit=tree.ray_cast(point(xy,z),d,200)
    if hit[0] is None:findings.append(dict(region=reg['id'],canonical=xy,z=z,angle=a));escapes+=1
 summaries.append(dict(region=reg['id'],rays=tested,escapes=escapes))
q=dict(file=args[0],rays=count,summaries=summaries,findings=findings,architectural_acceptance=False,limits=['Diagnostic only, no geometry changes.','Near-cover rays can encounter modeled panel joints and structural tolerances; every finding needs localization and source review.','Real stairs and lightwells are preserved; this check does not establish surveyed accuracy.']);(B/'reports/KABUK_COK_KOTLU_TARAMA.json').write_text(json.dumps(q,indent=2));print(json.dumps(summaries,indent=2))
