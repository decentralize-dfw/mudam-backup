from pathlib import Path
import bpy,json,numpy as np,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KADEMELI_CEPHE_v081.blend'));f=json.loads((D/'facade_planes_v062.json').read_text());q=np.array(f['q']);samples=np.array(json.loads((D/'row_whole_roof_samples_v061.json').read_text())['vertices']);center=samples[:,:2].mean(0);fits=json.loads((D/'row_whole_roof_samples_v065.json').read_text())['plane_cleaning']['models'];hips=json.loads((R/'reports/R169_ARCHITECTURAL_REBUILD_v075.json').read_text())['hip_plane_evidence'];planes=[np.array(fits[i]['coeff']) for i in [0,1]]+[np.array(h['coeff']) for h in hips];slate=bpy.data.materials['Authored slate - neutral unlit source color not copied'];plaster=bpy.data.materials['Mineral plaster provisional palette'];frame=bpy.data.materials['Painted light window frames'];created=[]
def roofz(p):return min(float((p-center)@c[:2]+c[2]) for c in planes)
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['purpose']='Bounded architectural junction closure; preserves actual glazed openings';created.append(name);return o
def quad(name,p,mat=slate):return mesh(name,p,[(0,1,2,3)],mat)
walls=[]
for k in range(4):
 a=f['sides'][(k-1)%4];b=f['sides'][k];na=np.array(a['normal']);nb=np.array(b['normal']);walls.append(np.linalg.solve(np.array([na,nb]),[na@q[(k-1)%4]+a['offset'],nb@q[k]+b['offset']]))
rearcenter=Vector((-81.746925354,-294.516082764,-69));rearRight=Vector((-.97769629955,-.2100233883,0));rn=np.array(f['sides'][0]['normal'])
def sx(p):return 1024+(Vector((*p,0))-rearcenter).dot(rearRight)*2048/36
def dep(p):return -1.28 if sx(p)<650 else (-.74 if sx(p)>1200 else 0)
# Side junctions close precisely between traced roof endpoints and existing wall endpoints.
for side in [1,3]:
 j=(side+1)%4;a=q[side];b=q[j];wa=walls[side];wb=walls[j]
 quad('ARCH_EAVE_CLOSURE_SIDE_'+str(side),[(*a,roofz(a)),(*b,roofz(b)),(*wb,roofz(wb)),(*wa,roofz(wa))])
# Rear eave junction split at actual wall depth transitions and annex roof intersections.
r=json.loads((D/'architectural_rear_hip_plane_v079.json').read_text());tri=np.array(r['corners']);edge=q[1]-q[0];length2=edge@edge;breaks=[0.,1.]
for x in [650,1200]:
 wp=np.array((rearcenter+rearRight*((x-1024)*36/2048))[:2]);breaks.append(float((wp-q[0])@edge/length2))
# Triangular roof crosses the rear eave at two positions.
crossings=[]
for a,b in zip(tri,np.roll(tri,-1,axis=0)):
 M=np.column_stack([edge,-(b-a)])
 try:u,v=np.linalg.solve(M,a-q[0])
 except:continue
 if 0<=u<=1 and 0<=v<=1:crossings.append(float(u));breaks.append(float(u))
breaks=sorted(set(max(0,min(1,u)) for u in breaks));annex=(min(crossings),max(crossings)) if len(crossings)>=2 else (2,3)
for k,(u,v) in enumerate(zip(breaks,breaks[1:])):
 if annex[0]<(u+v)/2<annex[1]:continue
 a=q[0]+edge*u;b=q[0]+edge*v;wa=walls[0]+(walls[1]-walls[0])*u;wb=walls[0]+(walls[1]-walls[0])*v;delta=dep((wa+wb)/2);wa+=rn*delta;wb+=rn*delta
 # Existing rear wall top was interpolated between its original endpoints.
 ha=roofz(walls[0])*(1-u)+roofz(walls[1])*u;hb=roofz(walls[0])*(1-v)+roofz(walls[1])*v
 quad('ARCH_REAR_EAVE_CLOSURE_'+str(k),[(*a,roofz(a)),(*b,roofz(b)),(*wb,hb),(*wa,ha)])
# Rear corner returns close shifts to the unchanged end walls.
for i in [0,1]:
 p=walls[i];shift=rn*dep(p);quad('ARCH_REAR_CORNER_RETURN_'+str(i),[(*p,-75),(*(p+shift),-75),(*(p+shift),roofz(p)),(*p,roofz(p))],plaster)
# Flashing along the source-traced projection/main-roof junction, only inside main footprint.
c=np.array(r['coeff']);org=np.array(r['origin'])
for idx,(ia,ib) in enumerate([(0,2),(2,1)]):
 a=tri[ia];b=tri[ib];da=rn@(a-q[0]);db=rn@(b-q[0])
 if da>0:a=a+(b-a)*(da/(da-db))
 if db>0:b=b+(a-b)*(db/(db-rn@(a-q[0])+1e-12))
 za=float((a-org)@c[:2]+c[2]);zb=float((b-org)@c[:2]+c[2]);quad('ARCH_REAR_ROOF_FLASHING_'+str(idx),[(*a,za),(*b,zb),(*b,roofz(b)),(*a,roofz(a))])
# Seal 27mm front band-to-wall mismatch with an explicit continuous sill strip.
a=walls[2];b=walls[3];quad('ARCH_FRONT_BAND_FOOT',[(*a,-65.5),(*b,-65.5),(*b,-65.46),(*a,-65.46)],slate)
# Front dormer reveals connect their real openings to recessed glazing.
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('ARCH_DORMER_GLASS_'):continue
 pts=[v.co.copy() for v in o.data.vertices];fn=Vector((.208791494,-.977960169,0))
 for j in range(4):quad(o.name+'_REVEAL_'+str(j),[pts[j],pts[(j+1)%4],pts[(j+1)%4]+fn*.125,pts[j]+fn*.125],frame)
# Rooflight perimeter upstands join offset glazing to the full roof sheet thickness.
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('ARCH_ROOFLIGHT_GLASS_'):continue
 pts=[v.co.copy() for v in o.data.vertices];normal=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
 if normal.z<0:normal=-normal
 for j in range(4):quad(o.name+'_UPSTAND_'+str(j),[pts[j],pts[(j+1)%4],pts[(j+1)%4]-normal*.20,pts[j]-normal*.20],frame)
# Rear reveal/glazing 10mm joints; front glass solids already overlap reveals.
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('ARCH_REAR_GLAZING_'):continue
 pts=[v.co.copy() for v in o.data.vertices];normal=Vector((*rn,0))
 for j in range(4):quad(o.name+'_REVEAL_JOINT_'+str(j),[pts[j],pts[(j+1)%4],pts[(j+1)%4]+normal*.02,pts[j]+normal*.02],frame)
s=bpy.context.scene;s['acceptance']='Unaccepted: explicit roof-wall/glazing junction closures added; whole-shell coverage and ground tests still required. Do not claim airtight/watertight based on this save.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_BIRLESIM_v083.blend'));target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,30));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_shell_rear_v083.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_SHELL_JUNCTIONS_v083.json').write_text(json.dumps(dict(accepted=False,created=created,scope='Explicit bounded roof-wall, roof junction, corner, dormer and glazing connections. No blanket hole fill.',pending='Independent coverage and ground testing; interior basal closure and remaining rear upper apertures.'),indent=2));print('JUNCTIONS_SAVED',len(created))
