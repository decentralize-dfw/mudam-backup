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
a=np.array(points);np.save(D/'balcony_face_samples_33.npy',a)
for z0,z1 in [(5.2,5.5),(5.7,6.2),(6.2,6.6),(2.2,2.6)]:
 rows=[]
 for u in np.arange(4.5,9.5,.5):
  sel=a[(abs(a[:,0]-u)<.25)&(a[:,2]>z0)&(a[:,2]<z1)]
  if len(sel):rows.append([round(float(u),2),len(sel),[round(float(q),2) for q in np.quantile(sel[:,1],[.1,.5,.9])]])
 print('BAND',z0,z1,rows)
