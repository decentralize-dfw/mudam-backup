from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
b=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'config/r302_fort_surfaces.json').read_text());out=[]
for pixels in [[410,670],[450,654],[500,633],[548,615],[430,700],[475,678],[520,658],[550,646]]:
 x,y=-305+pixels[0]*300/1400,25-pixels[1]*300/1400;zs=[]
 for dx in np.linspace(-.3,.3,5):
  for dy in np.linspace(-.3,.3,5):
   h,n,*_=b.ray_cast(Vector((x+dx,y+dy,100)),Vector((0,0,-1)),300)
   if h and -16<h.z<-9:zs.append(h.z)
 out.append(dict(pixel=pixels,xy=[x,y],z=float(np.median(zs)) if zs else None))
(R/'config/r304_court_bank_levels.json').write_text(json.dumps(out,indent=2));print(out)
