from pathlib import Path
import bpy,json,numpy as np
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend'))
floors=[];walls=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get() or o.name.startswith('R151_ACT_'):continue
 if any(k in o.name for k in ('FLOOR','LANDING')) and not o.name.startswith('R34'):
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   vs=np.array([o.matrix_world@o.data.vertices[i].co for i in t.vertices]);n=np.cross(vs[1]-vs[0],vs[2]-vs[0])
   if n[2]>1e-7 and vs[:,2].max()<.1 and abs(n[2])/max(np.linalg.norm(n),1e-12)>.95:
    floors.append(dict(name=o.name,xy=vs[:,:2].tolist(),z=float(vs[:,2].min())-.35))
 if o.name.startswith('R35_WALL_51946353_'):
  vs=np.array([o.matrix_world@v.co for v in o.data.vertices]);walls.append(dict(name=o.name,vertices=vs.tolist(),faces=[list(p.vertices) for p in o.data.polygons]))
(R/'.local_source_cache/r152/site_constraints.json').write_text(json.dumps(dict(floors=floors,walls=walls)))
print('R152_CONSTRAINTS',len(floors),len(walls),flush=True)
