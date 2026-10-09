from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R101_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=r['upper_z'];results={}
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or not o.visible_get():continue
  eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
  eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs);rows=[]
 def check(label,a,b,expected):
  d=b-a;hit=tree.ray_cast(a,d.normalized(),d.length);rows.append(dict(id=label,from_world=list(a),to_world=list(b),expected_hit=expected,hit=None if hit[0] is None else owners[hit[2]],passed=(hit[0] is not None)==expected))
 for x,y in [(615,632.33),(618,632.33),(615,647.58),(618,647.58),(621,647.58)]:
  for h in [.4,1.2,2.1]:check('passage_side',pt(x,y-3,UP+h),pt(x,y+3,UP+h),True)
 for y in [635,640,644]:
  for h in [.3,1.1,2.05]:check('clear_doorway',pt(605,y,UP+h),pt(632,y,UP+h),False)
 for x in [616,620]:
  for y in [635,644]:
   check('floor',pt(x,y,UP+.1),pt(x,y,UP-.3),True);check('ceiling',pt(x,y,UP+2.55),pt(x,y,UP+2.95),True)
 results[phase]=rows
q=dict(file=r['file'],results=results,before_failures=sum(not x['passed'] for x in results['before']),failures=[x for x in results['after'] if not x['passed']],construction_acceptance=False);(B/'reports/R101_verification.json').write_text(json.dumps(q,indent=2));print('R101',len(rows),'checks',q['before_failures'],'before',q['failures']);assert not q['failures']
