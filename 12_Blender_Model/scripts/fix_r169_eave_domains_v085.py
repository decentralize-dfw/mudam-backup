from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KAPALI_KABUK_ADAY_v084.blend'));samp=np.array(json.loads((D/'row_whole_roof_samples_v061.json').read_text())['vertices']);center=samp[:,:2].mean(0);fits=json.loads((D/'row_whole_roof_samples_v065.json').read_text())['plane_cleaning']['models'];hips=json.loads((R/'reports/R169_ARCHITECTURAL_REBUILD_v075.json').read_text())['hip_plane_evidence'];planes=[np.array(fits[i]['coeff']) for i in [0,1]]+[np.array(h['coeff']) for h in hips]
def z(p):return min(float((np.array(p[:2])-center)@c[:2]+c[2]) for c in planes)
def breaks(a,b):
 aa=np.array(a[:2]);bb=np.array(b[:2]);out=[0.,1.]
 for i in range(len(planes)):
  for j in range(i):
   c=planes[i]-planes[j];den=(bb-aa)@c[:2]
   if abs(den)>1e-10:
    t=-((aa-center)@c[:2]+c[2])/den
    if 1e-6<t<1-1e-6:out.append(float(t))
 return sorted(set(out))
changed=[]
for o in list(bpy.context.scene.objects):
 if not (o.name.startswith('ARCH_EAVE_CLOSURE_SIDE_') or o.name.startswith('ARCH_REAR_EAVE_CLOSURE_') or o.name=='ARCH_FRONT_MANSARD_BAND'):continue
 vv=[];ff=[]
 for face in o.data.polygons:
  p=[o.data.vertices[i].co.copy() for i in face.vertices]
  if len(p)!=4:continue
  if o.name=='ARCH_FRONT_MANSARD_BAND' and max(p[0].z,p[1].z)<-65:
   k=len(vv);vv.extend(p);ff.append((k,k+1,k+2,k+3));continue
  ts=breaks(p[0],p[1])
  for lo,hi in zip(ts,ts[1:]):
   a=p[0].lerp(p[1],lo);b=p[0].lerp(p[1],hi);a.z=z(a);b.z=z(b);c=p[3].lerp(p[2],hi);d=p[3].lerp(p[2],lo);k=len(vv);vv.extend([a,b,c,d]);ff.append((k,k+1,k+2,k+3))
 mat=o.data.materials[0];me=bpy.data.meshes.new(o.name+'_continuous');me.from_pydata(vv,[],ff);me.update();o.data=me;me.materials.append(mat);changed.append(o.name)
for o in bpy.context.scene.objects:
 if o.name.startswith('ARCH_DORMER_CAP_'):
  for idx in [2,3]:p=o.data.vertices[idx].co;p.z=z(p)
 if o.name.startswith('ARCH_DORMER_CHEEK_'):
  p=o.data.vertices[3].co;p.z=z(p)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_SUREKLI_SACAK_v085.blend'));print('PIECEWISE_EAVE_FIXED',changed)
