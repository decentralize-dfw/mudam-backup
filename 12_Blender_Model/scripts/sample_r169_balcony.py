from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0];p=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];t=(p[0]-p[3]).normalized();inside=Vector((t.y,-t.x,0));out=-inside;right=Vector((-out.y,out.x,0));center=(p[0]+p[3])*.5+inside*(-.45)
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));points=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 for f in o.data.polygons:
  q=o.matrix_world@f.center;n=o.matrix_world.to_3x3()@f.normal;u=(q-center).dot(right);d=(q-center).dot(out)
  if abs(u)<11 and -1<d<4 and b['base']+2<q.z<b['base']+8.5:points.append((u,d,q.z-b['base'],f.area,n.z))
a=np.array(points);rows=[]
for u in np.arange(-10.5,10.5,.35):
 sel=a[(abs(a[:,0]-u)<.25)&(a[:,2]>5.0)&(a[:,2]<6.2)]
 if len(sel)<4:continue
 rows.append([float(u),float(np.quantile(sel[:,1],.8)),len(sel)])
(D/'balcony_profile_33.json').write_text(json.dumps(dict(profile=rows,limits='Profile may include foreground vegetation. Inspect coherent curves before use.',source_height_band=[5,6.2]),indent=2));print(rows)
