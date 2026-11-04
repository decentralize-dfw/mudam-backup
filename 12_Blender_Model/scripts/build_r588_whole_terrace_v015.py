import bpy,bmesh,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
SRC='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v014.blend';DST='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v015.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/SRC))
def sig(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);b=np.empty(len(o.data.loops),np.int32);o.data.loops.foreach_get('vertex_index',b);return hashlib.sha256(a.tobytes()+b.tobytes()+str(o.matrix_world).encode()).hexdigest()
def uvhash(me):
 out={}
 for u in me.uv_layers:
  a=np.empty(len(u.data)*2,np.float32);u.data.foreach_get('uv',a);out[u.name]=hashlib.sha256(a.tobytes()).hexdigest()
 return out
def check(o):
 bm=bmesh.new();bm.from_mesh(o.data);r=dict(vertices=len(bm.verts),faces=len(bm.faces),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free();return r
before={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'}
o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];me=o.data;uvbefore=uvhash(me);matbefore=[m.name for m in me.materials];oldcorners=[v.vector.copy()for v in me.corner_normals]
a=np.array([-12.414369583129883,7.20503568649292]);b=np.array([-2.4570999145507812,-.0714000016450882]);L=float(np.linalg.norm(b-a));t=(b-a)/L;n=np.array([-t[1],t[0]]);za=-3.3628203868865967;zb=-3.295886516571045
controls=[]
for fn in ['R588_R549_OUTER_BAND_AUDIT.json','R588_R549_OUTERMOST_BAND_AUDIT.json']:
 dd=json.loads((W/fn).read_text())
 for p in dd['source']['profiles']:
  for r in p['rows']:
   if r['outward']<=3 and r['z'] is not None:
    xy=np.array(r['xy']);s=float((xy-a)@t);d=float(-(xy-a)@n);edge=za+(zb-za)*s/L;controls.append(dict(xy=list(xy),s=s,d=d,edge=edge,z=r['z']))
vv=np.array([[q['d'],q['z']-q['edge']]for q in controls]);k=float(np.dot(vv[:,0],vv[:,1])/np.dot(vv[:,0],vv[:,0]))
res=np.array([q['edge']+k*q['d']-q['z']for q in controls]);design=json.loads((W/'R588_FACADE_JOIN_DESIGN.json').read_text());poly=design['outline'];cp=design['sourcePlane']
# Existing source-traced retaining boundary is conserved; its true crest is a
# different architectural boundary from the erroneous internal terrace seam.
outer=[np.array(me.vertices[i].co[:2])for i in range(2,52)]
def distseg(p,aa,bb):
 ab=bb-aa;tt=np.clip((p-aa)@ab/(ab@ab),0,1)if ab@ab>1e-18 else 0.;return float(np.linalg.norm(p-aa-ab*tt))
def pdist(p):return min(distseg(p,np.array(aa),np.array(bb))for aa,bb in zip(poly,poly[1:]+poly[:1]))
def smooth(v):v=float(np.clip(v,0,1));return v*v*(3-2*v)
# Change existing connected upper skin only; existing closed technical body,
# actual outer curb, museum openings, bottom and all materials/UV stay intact.
upper={i for f in me.polygons if f.normal.z>.05 for i in f.vertices};changed=[]
for v in me.vertices:
 p=v.co.copy();xy=np.array(p[:2]);s=float((xy-a)@t);d=float(-(xy-a)@n)
 if v.index not in upper or p.z< -5 or not(-3<s<L+3 and -.004<d<8):continue
 outerdist=min(distseg(xy,aa,bb)for aa,bb in zip(outer,outer[1:]));wouter=smooth(outerdist/1.3)
 ws=smooth((s+3)/3)*smooth((L+3-s)/3)
 if s<1.75:ws*=smooth((4.5-d)/1.5)*(1-smooth(s/1.75))+smooth(s/1.75)
 if 0<=s<=L:ws=1.
 oncorner=pdist(xy)<.0002
 edge=za+(zb-za)*s/L
 if s<0:
  e=a+t*s;edge=cp[0]*e[0]+cp[1]*e[1]+cp[2]
 target=edge+k*d;w=wouter*ws
 if oncorner:target=cp[0]*p.x+cp[1]*p.y+cp[2];w=1.0
 newz=p.z+(target-p.z)*w
 if abs(newz-p.z)>.65:raise RuntimeError(('Excessive correction',v.index,list(p),newz,w))
 if abs(newz-p.z)>1e-8:v.co.z=newz;changed.append(dict(index=v.index,old=list(p),new=list(v.co),s=s,outward=d,weight=w))
me.update();changedids={c['index']for c in changed};newcorners=[]
for f in me.polygons:
 for li in f.loop_indices:
  vi=me.loops[li].vertex_index
  if vi in changedids and f.normal.z>.05:newcorners.append(me.vertices[vi].normal.copy())
  else:newcorners.append(oldcorners[li])
if len(newcorners)==len(me.loops):me.normals_split_custom_set(newcorners)
assert uvhash(me)==uvbefore
assert [m.name for m in me.materials]==matbefore
ck=check(o);assert ck['nonManifold']==ck['zeroArea']==0,ck
# The shared R549 top is directly measured at21 interior samples, on both sides.
me.calc_loop_triangles();bv=BVHTree.FromPolygons([v.co for v in me.vertices],[tr.vertices for tr in me.loop_triangles],all_triangles=True);seams=[]
for ss in np.linspace(.005,L-.005,41):
 xy=a+t*ss-n*.0002;p,nn,ii,dd=bv.ray_cast(Vector((*xy,0)),Vector((0,0,-1)),20);expected=za+(zb-za)*ss/L
 seams.append(dict(s=float(ss),xy=list(xy),z=None if p is None else p.z,expected=float(expected),error=None if p is None else float(p.z-expected)))
assert all(r['error']is not None and abs(r['error'])<.002 for r in seams),[q for q in seams if q['error']is None or abs(q['error'])>=.002]
report=dict(scene=DST,sourceScene=SRC,changedObject=o.name,changedVertices=len(changed),maximumAdjustment=max(abs(q['new'][2]-q['old'][2])for q in changed),changes=changed,sourceControls=controls,sourcePlaneOutwardSlope=k,sourceFitRMS=float(np.sqrt(np.mean(res*res))),sourceFitMax=float(np.max(abs(res))),sharedEdgeLength=L,maximumSharedEdgeError=max(abs(q['error'])for q in seams),seams=seams,checks=ck,retainedUVHashes=uvbefore,retainedMaterialNames=matbefore,method='Independent constrained drainage plane across full facade join; smoothly blends to preserved actual retaining crest. No scan mesh or scan texture copied.',limits=['Existing outer retaining crest conserved; this does not recertify exact outer wall elevation. Source floor varies locally up to10cm around constrained plane.'],accepted=False,published=False)
out=R/'scenes'/DST;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];assert uvhash(o.data)==uvbefore;assert check(o)['nonManifold']==check(o)['zeroArea']==0
others=[name for name,h in before.items()if name!=o.name and sig(bpy.data.objects[name])!=h];assert not others,others;report['reopened']=True;report['unchangedOtherMeshes']=len(before)-1;(R/'reports/R588_WHOLE_TERRACE_V015_BUILD.json').write_text(json.dumps(report,indent=2));print('V015_READY',str(out),len(changed),ck,report['maximumSharedEdgeError'],flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-12,8,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=10;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_facade_join_v015.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-12,3,40);s.camera.data.ortho_scale=22;s.render.resolution_x=1100;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R588_full_terrace_v015.png');bpy.ops.render.render(write_still=True)
