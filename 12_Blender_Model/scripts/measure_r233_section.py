from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]

d=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text());p=np.array(d['parts'][1]['polygon']);profiles=[]
for b in np.linspace(.05,.95,19):
 zs=[]
 for a in np.linspace(.25,.75,11):
  xy=p[0]+a*(p[1]-p[0])+b*(p[3]-p[0]);hit=g.ray_cast(Vector((*xy,80)),Vector((0,0,-1)),160)[0]
  if hit:zs.append(hit.z)
 profiles.append(dict(cross=float(b),median=float(np.median(zs)),min=float(min(zs)),max=float(max(zs))))
(R/'config/r233_second_light_section.json').write_text(json.dumps(profiles,indent=2));print(profiles,flush=True)
