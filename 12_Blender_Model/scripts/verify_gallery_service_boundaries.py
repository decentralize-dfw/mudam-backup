"""Reopen both scenes and check source boundary continuity, including floor/head joins."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R113_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
results={};fail=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',B.parent/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[];owners=[];dep=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  eo=ob.evaluated_get(dep);me=eo.to_mesh();offset=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(offset+i for i in f.vertices));owners.append(ob.name)
  eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs);rows=[]
 for wall in r['boundaries']:
  xi=wall['inner_x'];sign=1 if wall['outer_x']>xi else -1;y0,y1=wall['y_range']
  for i in range(1,31):
   y=y0+(y1-y0)*i/31
   for z in [.01,.3,1.5,2.1,3.5,4.34]:
    p=pt(xi-sign*2,y,z);q=pt(xi+sign*.3,y,z);h=tree.ray_cast(p,(q-p).normalized(),(q-p).length)
    rows.append(dict(side=wall['side'],y=y,z=z,hit=owners[h[2]] if h[0] is not None else None))
 results[phase]=rows
fail=[x for x in results['after'] if x['hit'] is None]
old=sum(x['hit'] is None for x in results['before']);assert old>0
q=dict(file=r['file'],checks=results,old_missing=old,new_missing=len(fail),failures=fail,construction_acceptance=False,limits=['Source boundary continuity only; exact concealed wall thickness and ceiling elevation remain candidates.'])
(B/'reports/R113_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('Old gaps:',old,'remaining:',len(fail));assert not fail
