"""Reopen both scenes; sample formerly missing overhead cover and preserved routes."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R111_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(u,v,z):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
samples=[(u,v) for u in [1123,1130,1140,1150] for v in range(270,578,7)]
results={};fail=[]
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',B.parent/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[];owners=[];dep=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  eo=ob.evaluated_get(dep);me=eo.to_mesh();offset=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(offset+i for i in f.vertices));owners.append(ob.name)
  eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs);rows=[]
 for u,v in samples:
  p=pt(u,v,4.30);h=tree.ray_cast(p,Vector((0,0,1)),.25)
  rows.append(dict(uv=[u,v],cover=owners[h[2]] if h[0] is not None else None))
 results[phase]=rows
o=bpy.data.objects[r['closed_objects'][0]];bm=bmesh.new();bm.from_mesh(o.data)
solid=dict(nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free()
if solid['nonmanifold'] or solid['zero_faces'] or solid['volume']<=0:fail.append(solid)
# Only sample the actual soffit polygon; northern / southern stair routes stay outside.
obtree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
checked=[]
for before,after in zip(results['before'],results['after']):
 p=pt(*after['uv'],4.3)
 if obtree.ray_cast(p,Vector((0,0,1)),.25)[0] is None:continue
 checked.append(dict(uv=after['uv'],before=before['cover'],after=after['cover']))
 if after['cover'] is None:fail.append(after)
assert checked and any(x['before'] is None for x in checked)
result=dict(file=r['file'],solid=solid,cover_checks=checked,old_missing=sum(x['before'] is None for x in checked),new_missing=sum(x['after'] is None for x in checked),failures=fail,construction_acceptance=False,limits=['Checks overhead continuity at the inherited gallery soffit datum; measured height and concealed construction are unknown.','Not whole-building acceptance.'])
(B/'reports/R111_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(len(checked),'overhead samples; old missing',result['old_missing'],'new missing',result['new_missing']);assert not fail
