import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
SRC='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v019.blend';DST='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v020.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/SRC));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];me=o.data
fit=json.loads((W/'R588_R549_LEFT_GRADE_FIT.json').read_text());C=fit['plane'];CD=json.loads((W/'R588_FACADE_JOIN_DESIGN.json').read_text());CP=CD['sourcePlane'];poly=[np.array(p)for p in CD['outline']]
A=np.array([-23.66860008239746,9.909099578857422]);B=np.array([-14.716455459594727,8.885946273803711]);L=float(np.linalg.norm(B-A));T=(B-A)/L;N=np.array([-T[1],T[0]]);ZA=-3.249281406402588;ZB=-3.3362252712249756

def sig(ob):
 a=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',a);b=np.empty(len(ob.data.loops),np.int32);ob.data.loops.foreach_get('vertex_index',b);return hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
def ds(p,a,b):
 ab=b-a;q=np.clip((p-a)@ab/(ab@ab),0,1)if ab@ab>1e-18 else 0;return float(np.linalg.norm(p-a-ab*q))
def cd(p):q=np.array(p[:2])-A;return float(q@T),float(-q@N)
def sm(v):v=float(np.clip(v,0,1));return v*v*(3-2*v)
def plane(p):return C[0]*p[0]+C[1]*p[1]+C[2]
def cp(p):return CP[0]*p[0]+CP[1]*p[1]+CP[2]
def pd(p):return min(ds(np.array(p[:2]),a,b)for a,b in zip(poly,poly[1:]+poly[:1]))
def design(p):
 s,d=cd(p);edgepoint=A+T*s;edge=ZA+(ZB-ZA)*s/L
 return plane(p)+(edge-plane(edgepoint))*sm(1-d)
before={ob.name:sig(ob)for ob in bpy.context.scene.objects if ob.type=='MESH'};mats=[m.name for m in me.materials];uvnames=[u.name for u in me.uv_layers];oldnormal=[v.vector.copy()for v in me.corner_normals]
bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();nl=bm.loops.layers.float_vector.new('R588_RETAINED_NORMAL')
for f in bm.faces:
 for loop,li in zip(f.loops,me.polygons[f.index].loop_indices):loop[nl]=oldnormal[li]
# Real outer technical wall boundary is kept at its existing crest elevation.
outer=[]
for f in bm.faces:
 if min(v.co.z for v in f.verts)>-5 or abs(f.normal.z)>.02:continue
 for e in f.edges:
  if all(v.co.z>-5 for v in e.verts)and sum(cd(v.co)[1]for v in e.verts)/2>3:
   outer.append([np.array(v.co[:2])for v in e.verts])
assert outer,'Missing outer boundary'
def outer_distance(s):
 a=A+T*s;vals=[]
 for p,q in outer:
  v=q-p;M=np.column_stack([-N,-v])
  if abs(np.linalg.det(M))<1e-10:continue
  d,u=np.linalg.solve(M,p-a)
  if -.0001<=u<=1.0001 and d>3:vals.append(d)
 return min(vals)if vals else 6.0
cuts=[];oldN=len(bm.verts)
for axis,station in [('along',float(v))for v in range(-1,11)]+[('across',v)for v in [.25,.5,1,2,3]]:
 fs=[]
 for f in bm.faces:
  if min(v.co.z for v in f.verts)<-5:continue
  vals=[cd(v.co)for v in f.verts]
  if axis=='along':ok=min(v[0]for v in vals)<station-1e-7<max(v[0]for v in vals)and min(v[1]for v in vals)<3.2 and max(v[1]for v in vals)>-.005
  else:ok=min(v[1]for v in vals)<station-1e-7<max(v[1]for v in vals)and min(v[0]for v in vals)<L+1.5 and max(v[0]for v in vals)>-1.5
  if ok:fs.append(f)
 if not fs:continue
 edges=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);q=A+T*station if axis=='along'else A-N*station;normal=T if axis=='along'else N
 result=bmesh.ops.bisect_plane(bm,geom=list(vs)+list(edges)+fs,dist=1e-7,plane_co=Vector((*q,0)),plane_no=Vector((*normal,0)),clear_inner=False,clear_outer=False);cuts.append(dict(axis=axis,station=station,faces=len(fs),cutElements=len(result['geom_cut'])))
bm.normal_update();changes=[]
for v in bm.verts:
 s,d=cd(v.co)
 if not(-1.5<s<L+1.5 and -.005<d<8 and v.co.z>-5):continue
 if not any(f.normal.z>1e-5 for f in v.link_faces):continue
 ws=sm((s+1.5)/1.5)*sm((L+1.5-s)/1.5)
 if 0<=s<=L:ws=1.
 D=outer_distance(s);wo=1 if d<=3 else sm((D-d)/max(.25,D-3));w=ws*wo;target=design(v.co)
 if pd(v.co)<.0002:target=cp(v.co);w=1.
 newz=v.co.z+(target-v.co.z)*w
 if abs(newz-v.co.z)>.85:raise RuntimeError(('Unsupported grade change',list(v.co),newz,w))
 if abs(newz-v.co.z)>1e-8:changes.append(dict(old=list(v.co),newZ=newz,s=s,outward=d,weight=w));v.co.z=newz
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bm.normal_update()
assert all(e.is_manifold for e in bm.edges),sum(not e.is_manifold for e in bm.edges)
assert not[f for f in bm.faces if f.calc_area()<1e-10],[(f.calc_area(),[list(v.co)for v in f.verts])for f in bm.faces if f.calc_area()<1e-10]
acc={v:Vector((0,0,0))for v in bm.verts}
for f in bm.faces:
 if f.normal.z>.9:
  for v in f.verts:acc[v]+=f.normal*f.calc_area()
for n in acc.values():
 if n.length:n.normalize()
grad=((ZB-ZA)/L)*T+float(np.array(C[:2])@N)*N;nf=Vector((-grad[0],-grad[1],1)).normalized();nc=Vector((-CP[0],-CP[1],1)).normalized()
def common(s):q=float(np.clip(s/L,0,1));return(nf*(1-q)+nc*q).normalized()
for f in bm.faces:
 if f.normal.z<.9:continue
 for loop in f.loops:
  s,d=cd(loop.vert.co);xy=np.array(loop.vert.co[:2]);edgeDist=ds(xy,A,B);cornerDist=pd(loop.vert.co);nn=loop[nl].copy()
  if -1.5<s<L+1.5 and -.005<d<8:nn=acc[loop.vert];f.smooth=True
  if edgeDist<.6:
   w=sm(1-edgeDist/.6);nn=(nn*(1-w)+common(s)*w).normalized();f.smooth=True
  if cornerDist<.6 and cornerDist<edgeDist:
   w=sm(1-cornerDist/.6);nn=(nn*(1-w)+nc*w).normalized();f.smooth=True
  loop[nl]=nn
bm.to_mesh(me);bm.free();attr=me.attributes['R588_RETAINED_NORMAL'];normals=[v.vector.copy()for v in attr.data];me.attributes.remove(attr);me.normals_split_custom_set(normals);me.update();assert[m.name for m in me.materials]==mats;assert[u.name for u in me.uv_layers]==uvnames
# Identical normal field on the neighboring apron, without moving its geometry.
ap=bpy.data.objects['R549_WEST_GLASS_EXTERNAL_GROUND_1'];am=ap.data;an=[v.vector.copy()for v in am.corner_normals]
for f in am.polygons:
 if f.normal.z<.9:continue
 for li in f.loop_indices:
  p=am.vertices[am.loops[li].vertex_index].co;s,d=cd(p);ed=ds(np.array(p[:2]),A,B)
  if ed<.6:
   w=sm(1-ed/.6);an[li]=(an[li]*(1-w)+common(s)*w).normalized();f.use_smooth=True
am.normals_split_custom_set(an)
def check(ob):
 b=bmesh.new();b.from_mesh(ob.data);r=dict(vertices=len(b.verts),faces=len(b.faces),nonManifold=sum(not e.is_manifold for e in b.edges),zeroArea=sum(f.calc_area()<1e-10 for f in b.faces));b.free();return r
checks={name:check(bpy.data.objects[name])for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_1']};assert all(v['nonManifold']==v['zeroArea']==0 for v in checks.values())
me.calc_loop_triangles();bv=BVHTree.FromPolygons([v.co for v in me.vertices],[tr.vertices for tr in me.loop_triangles],all_triangles=True);tests=[]
for s in np.linspace(.02,L-.02,37):
 for d in [.0002,.01,.1,.25,.5,1,2,3]:
  xy=A+T*s-N*d;p,n,i,dist=bv.ray_cast(Vector((*xy,0)),Vector((0,0,-1)),20);target=design(xy);tests.append(dict(station=float(s),outward=d,xy=list(xy),z=None if p is None else p.z,target=target,error=None if p is None else p.z-target))
missing=[r for r in tests if r['error']is None];edge=[r for r in tests if r['outward']<=.01];assert not missing,missing;assert max(abs(r['error'])for r in edge)<.002,sorted(edge,key=lambda q:abs(q['error']))[-5:]
report=dict(scene=DST,sourceScene=SRC,sourceFit=fit,method='Whole left terrace join graded from independent ACT ground-control plane; original R549 boundary height preserved with a smooth1m transition; actual outer retaining crest conserved. No scan mesh or texture reused.',cuts=cuts,insertedVertices=len(me.vertices)-oldN,changedVertices=len(changes),maximumAdjustment=max(abs(r['old'][2]-r['newZ'])for r in changes),checks=checks,UVLayersPreserved=uvnames,materialsPreserved=mats,profiles=tests,edgeMax=max(abs(r['error'])for r in edge),interiorMax=max(abs(r['error'])for r in tests),limits=['A-end ACT is facade-occluded; its ground continuity is inferred from adjacent independently sampled floor. Existing outer retaining crest is not recertified.'],accepted=False,published=False)
out=R/'scenes'/DST;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));assert all(sig(bpy.data.objects[n])==h for n,h in before.items()if n!='R322_WEST_MUSEUM_TERRACE');report['unchangedOtherMeshGeometry']=len(before)-1;report['reopened']=True;report['sceneSHA256']=hashlib.sha256(out.read_bytes()).hexdigest();(R/'reports/R588_LEFT_JUNCTION_V020.json').write_text(json.dumps(report,indent=2));print('V020_READY',DST,report['edgeMax'],report['interiorMax'],checks,flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-19.5,9,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=14;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_left_join_v020_top.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-20,3,2);s.camera.rotation_euler=(Vector((-19,9.5,-3.3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=14;s.render.filepath=str(R/'renders/qa/R588_left_join_v020_oblique.png');bpy.ops.render.render(write_still=True)
