from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R100_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];results={}
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));rows=[]
 for record in r['records']:
  ob=bpy.data.objects[record['object']];target=pt(record['new_xy'])
  for i in record['vertices']:
   q=ob.matrix_world@ob.data.vertices[i].co;q.z=0;error=(q-target).length;rows.append(dict(object=ob.name,index=i,error_m=error,passed=error<.0001))
 results[phase]=rows
q=dict(file=r['file'],results=results,before_max_m=max(x['error_m'] for x in results['before']),after_max_m=max(x['error_m'] for x in results['after']),failures=[x for x in results['after'] if not x['passed']],construction_acceptance=False,limits=r['limits']);(B/'reports/R100_verification.json').write_text(json.dumps(q,indent=2));print('R100',len(rows),'contacts',q['before_max_m'],'to',q['after_max_m']);assert not q['failures']
