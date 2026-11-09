import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R254_OVAL_BUTUNLESIK_ADAY_v001.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.name not in ['R154_FAR_GROUND','R182_EXTENSION_GROUND','R152_CLASS2_TERRAIN']:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);floor=bpy.data.objects['R254_OVAL_MATCHED_FLOOR'];samples=[];misses=[]
for e in floor.data.edges:
 a,b=[floor.matrix_world@floor.data.vertices[i].co for i in e.vertices]
 if abs(a.z-8.5)>.001 or abs(b.z-8.5)>.001:continue
 # Use only edges shared with a vertical side, not triangulated internal floor diagonals.
 linked=[p for p in floor.data.polygons if all(i in p.vertices for i in e.vertices)]
 if not any(abs(p.normal.z)<.3 for p in linked):continue
 for j in range(max(2,math.ceil((b-a).length/.5))+1):
  q=a.lerp(b,j/max(2,math.ceil((b-a).length/.5)));h,*_=g.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),200)
  if h:samples.append(dict(x=q.x,y=q.y,ground=h.z,baseGap=8.5-h.z))
  else:misses.append([q.x,q.y])
out=dict(samples=len(samples),missing=len(misses),maxBaseGap=max((p['baseGap'] for p in samples),default=None),groundRange=[min((p['ground'] for p in samples),default=None),max((p['ground'] for p in samples),default=None)],misses=misses,source='Current independently modeled terrain, not surveyed external ground',accepted=False)
(R/'reports/R254_OVAL_GROUND_CONTACT.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
