from pathlib import Path
import runpy,json,sys,math,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];q=json.loads((B/'reports/KABUK_COK_KOTLU_TARAMA.json').read_text());sys.argv=['audit','--',q['file']];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));orig={}
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob.name.startswith(('P06_MAIN_ROOF_FACE','P06_WEST_GLAZED','P06_LOWER_SLOPE','P06_MAIN_LANTERN')):orig[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons])
out=[]
for f in q['findings']:
 if f['region'] not in ['GH','WEST_CAFE']:continue
 a=math.radians(f['angle']);d=Vector((math.cos(a),math.sin(a),0));o=g['point'](f['canonical'],f['z']);hits=[]
 for n,t in orig.items():
  h=t.ray_cast(o,d,200)
  if h[0] is not None:
   near=g['tree'].find_nearest(h[0]);hits.append(dict(source=n,distance=h[3],intersection=list(h[0]),nearest=g['names'][g['owners'][near[2]]],nearest_distance=near[3]))
 hits.sort(key=lambda h:h['distance']);out.append(dict(finding=f,original_hits=hits[:2]))
(B/'reports/ENCLOSURE_ORIGINAL_SURFACE_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(json.dumps(out[:10],indent=2))
