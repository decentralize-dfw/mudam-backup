import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];o.data.calc_loop_triangles();tris=[[[*(o.matrix_world@o.data.vertices[i].co)]for i in t.vertices]for t in o.data.loop_triangles if t.normal.z>.2];(R/'reports/R586_EXISTING_TERRACE_TOP.json').write_text(json.dumps(tris))
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for u in range(265,420,12):
 for v in range(375,530,12):
  if not (v>u+70 and v<u+150):continue
  x=-59+u*.038;y=27-v*.038;h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=50)
  if h:rows.append([x,y,p.z])
(R/'reports/R586_APRON_CONTROLS.json').write_text(json.dumps(rows));print('controls',len(rows))
