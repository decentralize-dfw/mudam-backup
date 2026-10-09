from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R99_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());results={};output='R99_verification.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];r['file']=args[0];output=args[1]
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or not o.visible_get():continue
  eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
  eo.to_mesh_clear()
 t=BVHTree.FromPolygons(vs,fs);rows=[]
 for p in r['probes']:
  a=Vector(p['point']);n=Vector(p['normal']);hit=t.ray_cast(a+n,-n,2);rows.append(dict(id='source_wall',passed=hit[0] is not None,hit=None if hit[0] is None else owners[hit[2]]))
 for route in ['W_N','W_S']:
  for z in [.3,1.1,2]:
   a,b=[pt(*p,z) for p in P['routes'][route]];hit=t.ray_cast(a,(b-a).normalized(),(b-a).length);rows.append(dict(id=route,passed=hit[0] is None,hit=None if hit[0] is None else owners[hit[2]]))
 results[phase]=rows
q=dict(file=r['file'],results=results,before_missing_wall=sum(not x['passed'] for x in results['before'] if x['id']=='source_wall'),failures=[x for x in results['after'] if not x['passed']],construction_acceptance=False,limits=r['limits']);(B/'reports'/output).write_text(json.dumps(q,indent=2));print('R99',q['before_missing_wall'],'missing before; after',q['failures']);assert not q['failures']
