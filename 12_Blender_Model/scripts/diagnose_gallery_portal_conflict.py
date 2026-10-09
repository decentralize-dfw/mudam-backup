from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R02_build_report.json').read_text());a,b=map(Vector,r['portal_endpoints']);n=Vector(r['normal']);p=a.lerp(b,.5);p.z=6
for file,names in [('MUDAM_R72_ATRIUM_DUVAR_SUREKLILIGI_v004.blend',['R28_E_HIGH_GALLERY_WALL','R23_E_2_WALL']),('MUDAM_R73_GALERI_DUVAR_GOVDELERI_v002.blend',['R73_E_CONTINUOUS_GALLERY_WALL'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/file))
 for name in names:
  o=bpy.data.objects[name];t=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons]);hits=[]
  for distance in [.4,.65,1,2]:
   h=t.ray_cast(p-n*distance,n,distance*2);hits.append((distance, list(h[0]) if h[0] else None,h[3]))
  print(file,name,hits)
