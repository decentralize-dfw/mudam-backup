from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_BIRLESIK_v087.blend'));f=json.loads((D/'facade_planes_v062.json').read_text());q=np.array(f['q']);n=np.array(f['sides'][0]['normal']);walls=[]
for k in [0,1]:
 a=f['sides'][(k-1)%4];b=f['sides'][k];na=np.array(a['normal']);nb=np.array(b['normal']);walls.append(np.linalg.solve(np.array([na,nb]),[na@q[(k-1)%4]+a['offset'],nb@q[k]+b['offset']]))
center=np.array(json.loads((D/'row_whole_roof_samples_v061.json').read_text())['vertices'])[:,:2].mean(0);fits=json.loads((D/'row_whole_roof_samples_v065.json').read_text())['plane_cleaning']['models'];hips=json.loads((R/'reports/R169_ARCHITECTURAL_REBUILD_v075.json').read_text())['hip_plane_evidence'];planes=[np.array(fits[i]['coeff']) for i in [0,1]]+[np.array(h['coeff']) for h in hips]
def z(p):return min(float((p-center)@c[:2]+c[2]) for c in planes)
rc=np.array([-81.746925354,-294.516082764]);right=np.array([-.97769629955,-.2100233883]);edge=q[1]-q[0];we=walls[1]-walls[0];breaks=[0.,1.];steps=[]
for x in [700,1200]:
 p=rc+right*((x-1024)*36/2048);u=float((p-walls[0])@we/(we@we));breaks.append(u);steps.append(u)
tri=np.array(json.loads((D/'architectural_rear_hip_plane_v079.json').read_text())['corners']);cross=[]
for a,b in zip(tri,np.roll(tri,-1,axis=0)):
 try:u,v=np.linalg.solve(np.column_stack([edge,-(b-a)]),a-q[0])
 except:continue
 if 0<=u<=1 and 0<=v<=1:cross.append(float(u));breaks.append(float(u))
for i in range(4):
 for j in range(i):
  c=planes[i]-planes[j];den=edge@c[:2]
  if abs(den)>1e-10:
   u=-((q[0]-center)@c[:2]+c[2])/den
   if 0<u<1:breaks.append(float(u))
annex=(min(cross),max(cross));mat=bpy.data.materials['Authored slate - neutral unlit source color not copied']
for o in list(bpy.context.scene.objects):
 if o.name.startswith('ARCH_REAR_EAVE_CLOSURE_'):bpy.data.objects.remove(o,do_unlink=True)
def depth(p):
 x=1024+(p-rc)@right*2048/36;return -1.28 if x<700 else (-.74 if x>1200 else 0)
def basez(u):return z(walls[0])*(1-u)+z(walls[1])*u
def make(name,p):
 me=bpy.data.meshes.new(name);me.from_pydata(p,[],[list(range(len(p)))]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat)
bs=sorted(set(breaks))
for i,(u,v) in enumerate(zip(bs,bs[1:])):
 if annex[0]<(u+v)/2<annex[1]:continue
 a=q[0]+edge*u;b=q[0]+edge*v;d=depth(walls[0]+we*(u+v)/2);wa=walls[0]+we*u+n*d;wb=walls[0]+we*v+n*d;make('ARCH_REAR_EAVE_CLOSURE_'+str(i),[(*a,z(a)),(*b,z(b)),(*wb,basez(v)),(*wa,basez(u))])
for i,u in enumerate(steps):
 p=q[0]+edge*u;w=walls[0]+we*u;dl=depth(w-we*.0001);dr=depth(w+we*.0001);make('ARCH_EAVE_STEP_END_'+str(i),[(*p,z(p)),(*(w+n*dl),basez(u)),(*(w+n*dr),basez(u))])
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v087.blend'));print('STEP_JUNCTION_FIXED')
