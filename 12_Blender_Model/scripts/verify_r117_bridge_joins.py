"""Current full-scene route check, independent of superseded R28 object names."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];r=json.loads((B/'reports'/args[0]).read_text());P=json.loads((B/'config/ground_gallery_access.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
rows=[]
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file))
 vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
  eo.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs)
 for side,x in [('E',461),('W',691.5)]:
  for y in [560,570,580,590]:
   a=pt((x,y))+Vector((0,0,4.8790748));h=tree.ray_cast(a,Vector((0,0,-1)),.045);name=None if h[0] is None else owners[h[2]];rows.append(dict(phase=phase,side=side,x=x,y=y,owner=name,passed=name is not None))
q=dict(file=r['file'],checks=rows,before_missing=sum(not a['passed'] for a in rows if a['phase']=='before'),failures=[a for a in rows if a['phase']=='after' and not a['passed']],construction_acceptance=False);(B/'reports'/args[1]).write_text(json.dumps(q,indent=2));print(q)
