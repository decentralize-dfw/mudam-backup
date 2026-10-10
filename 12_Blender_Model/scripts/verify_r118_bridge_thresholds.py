from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R118_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];rows=[]
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));deps=bpy.context.evaluated_depsgraph_get()
 for side,x in [('E',461),('W',691.5)]:
  trees=[]
  for name in [f'R117_{side}_BRIDGE_FLOOR_JOIN',f'R23_THRESHOLD_{side}_BRIDGE']:
   o=bpy.data.objects[name];eo=o.evaluated_get(deps);me=eo.to_mesh();tree=BVHTree.FromPolygons([eo.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);trees.append((name,tree));eo.to_mesh_clear()
  for y in range(558,597):
   a=pt(x,y,4.8790748);hits=[name for name,t in trees if t.ray_cast(a,Vector((0,0,-1)),.05)[0] is not None];rows.append(dict(phase=phase,side=side,x=x,y=y,owners=hits,passed=len(hits)==1))
q=dict(file=r['file'],checks=rows,before_duplicate_samples=sum(len(x['owners'])>1 for x in rows if x['phase']=='before'),failures=[x for x in rows if x['phase']=='after' and not x['passed']],construction_acceptance=False);assert q['before_duplicate_samples']>0;(B/'reports/R118_verification.json').write_text(json.dumps(q,indent=2));print('R118',q['before_duplicate_samples'],'duplicate before',len(q['failures']),'after failures')
