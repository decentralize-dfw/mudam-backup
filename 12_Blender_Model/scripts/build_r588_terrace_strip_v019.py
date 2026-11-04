import bpy,bmesh,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R/'reports'
SRC='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v018.blend';DST='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v019.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/SRC));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE']
with bpy.data.libraries.load(str(R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v014.blend'),link=False)as(fr,to):to.objects=['R322_WEST_MUSEUM_TERRACE']
original=to.objects[0];o.data=original.data.copy();bpy.data.objects.remove(original);me=o.data
v15=json.loads((R/'reports/R588_WHOLE_TERRACE_V015_BUILD.json').read_text());k=v15['sourcePlaneOutwardSlope'];D=json.loads((W/'R588_FACADE_JOIN_DESIGN.json').read_text());cp=D['sourcePlane'];poly=[np.array(p)for p in D['outline']];a=np.array([-12.414369583129883,7.20503568649292]);b=np.array([-2.4570999145507812,-.0714000016450882]);L=float(np.linalg.norm(b-a));t=(b-a)/L;n=np.array([-t[1],t[0]]);za=-3.3628203868865967;zb=-3.295886516571045

def sig(ob):
 a=np.empty(len(ob.data.vertices)*3,np.float32);ob.data.vertices.foreach_get('co',a);b=np.empty(len(ob.data.loops),np.int32);ob.data.loops.foreach_get('vertex_index',b);return hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
def ds(p,a,b):
 ab=b-a;q=np.clip((p-a)@ab/(ab@ab),0,1)if ab@ab>1e-18 else 0;return float(np.linalg.norm(p-a-ab*q))
def coords(p):v=np.array(p[:2])-a;return float(v@t),float(-v@n)
def ground(p):
 s,d=coords(p);z=za+(zb-za)*s/L
 if s<0:
  q=a+t*s;z=cp[0]*q[0]+cp[1]*q[1]+cp[2]
 if min(ds(np.array(p[:2]),aa,bb)for aa,bb in zip(poly,poly[1:]+poly[:1]))<.0002:return cp[0]*p.x+cp[1]*p.y+cp[2]
 return z+k*d
before={q.name:sig(q)for q in bpy.context.scene.objects if q.type=='MESH'};oldnormal=[v.vector.copy()for v in me.corner_normals];bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();nl=bm.loops.layers.float_vector.new('R588_RETAINED_CORNER_NORMAL')
for f in bm.faces:
 for l,li in zip(f.loops,me.polygons[f.index].loop_indices):l[nl]=oldnormal[li]
outer=[np.array(me.vertices[i].co[:2])for i in range(2,52)]
oldN=len(bm.verts);cuts=[]
for station in list(np.arange(-2,13,1)):
 fs=[]
 for f in bm.faces:
  vals=[coords(v.co)for v in f.verts]
  if min(v.co.z for v in f.verts)<-5:continue
  if min(p[0]for p in vals)<station-1e-7<max(p[0]for p in vals) and min(p[1]for p in vals)<.65 and max(p[1]for p in vals)>-.005:fs.append(f)
 if not fs:continue
 edges=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);q=a+t*station
 result=bmesh.ops.bisect_plane(bm,geom=list(vs)+list(edges)+fs,dist=1e-7,plane_co=Vector((*q,0)),plane_no=Vector((*t,0)),clear_inner=False,clear_outer=False);cuts.append(dict(station=float(station),faces=len(fs),cuts=len(result['geom_cut'])))
bm.normal_update();changes=[]
def sm(v):v=float(np.clip(v,0,1));return v*v*(3-2*v)
for v in bm.verts:
 ss,dd=coords(v.co)
 if not(-3<ss<L+3 and -.004<dd<8 and v.co.z>-5):continue
 if not any(f.normal.z>1e-5 for f in v.link_faces):continue
 outerdist=min(ds(np.array(v.co[:2]),aa,bb)for aa,bb in zip(outer,outer[1:]));wouter=sm(outerdist/1.3);ws=sm((ss+3)/3)*sm((L+3-ss)/3)
 if ss<1.75:ws*=sm((4.5-dd)/1.5)*(1-sm(ss/1.75))+sm(ss/1.75)
 if 0<=ss<=L:ws=1.
 target=ground(v.co);w=wouter*ws
 if min(ds(np.array(v.co[:2]),aa,bb)for aa,bb in zip(poly,poly[1:]+poly[:1]))<.0002:w=1.
 newz=v.co.z+(target-v.co.z)*w
 if abs(v.co.z-newz)>.65:raise RuntimeError(('Unexpected local plane correction',list(v.co),newz))
 if abs(v.co.z-newz)>1e-8:changes.append(dict(old=list(v.co),newZ=newz));v.co.z=newz
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
bm.normal_update();bad=[f for f in bm.faces if f.calc_area()<1e-10]
assert not bad,[(f.calc_area(),[list(v.co)for v in f.verts])for f in bad]
assert all(e.is_manifold for e in bm.edges),sum(not e.is_manifold for e in bm.edges)
# Bisect interpolates every existing UV layer and the retained corner normals.
# Recompute this strip's smooth upper normals, excluding technical side faces.
acc={v:Vector((0,0,0))for v in bm.verts}
for f in bm.faces:
 if f.normal.z>.9:
  for v in f.verts:acc[v]+=f.normal*f.calc_area()
for v in acc:
 if acc[v].length:acc[v].normalize()
nc=Vector((-cp[0],-cp[1],1)).normalized();nf=Vector((-.0206561516970396,-.019071225076913834,.9996047616004943)).normalized()
for f in bm.faces:
 if f.normal.z<.9:continue
 for l in f.loops:
  ss,dd=coords(l.vert.co);xy=np.array(l.vert.co[:2]);edgeDist=ds(xy,a,b);cornerDist=min(ds(xy,aa,bb)for aa,bb in zip(poly,poly[1:]+poly[:1]));nn=l[nl].copy()
  if -3<ss<L+3 and -.004<dd<8:nn=acc[l.vert];f.smooth=True
  if edgeDist<.6:
   q=float(np.clip(ss/L,0,1));ne=(nc*(1-q)+nf*q).normalized();w=sm(1-edgeDist/.6);nn=(nn*(1-w)+ne*w).normalized();f.smooth=True
  if cornerDist<.6 and cornerDist<edgeDist:
   w=sm(1-cornerDist/.6);nn=(nn*(1-w)+nc*w).normalized();f.smooth=True
  l[nl]=nn
bm.to_mesh(me);bm.free();attr=me.attributes['R588_RETAINED_CORNER_NORMAL'];normals=[v.vector.copy()for v in attr.data];me.attributes.remove(attr);me.normals_split_custom_set(normals);me.update();bm=bmesh.new();bm.from_mesh(me);check=dict(vertices=len(bm.verts),faces=len(bm.faces),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert check['nonManifold']==check['zeroArea']==0
report=dict(scene=DST,sourceScene=SRC,object=o.name,cuts=cuts,insertedVertices=len(me.vertices)-oldN,correctedVertices=len(changes),maximumVerticalCorrection=max(abs(q['old'][2]-q['newZ'])for q in changes),terraceGeometryBaseline='v014; one application of source grade after subdivision',checks=check,method='Subdivide inherited long skinny join triangles at architectural grade stations; grade each new top vertex to the same source-constrained piecewise plane. UVs interpolated with mesh cuts; outer geometry unchanged.',changes=changes,accepted=False,published=False)
out=R/'scenes'/DST;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));assert all(sig(bpy.data.objects[n])==h for n,h in before.items()if n!='R322_WEST_MUSEUM_TERRACE');report['reopened']=True;report['unchangedOtherMeshes']=len(before)-1;(R/'reports/R588_TERRACE_STRIP_V019.json').write_text(json.dumps(report,indent=2));print('V019_READY',report,flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-12,8,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=10;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_facade_join_v019.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('R588_DIAGNOSTIC_FLAT');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.3,.2,1);bs.inputs['Roughness'].default_value=.8
for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1','R588_WEST_GLASS_CORNER_GROUND']:
 mm=bpy.data.objects[name].data;mm.materials.clear();mm.materials.append(mat)
 for f in mm.polygons:f.material_index=0
s.render.filepath=str(R/'renders/qa/R588_facade_join_v019_flat.png');bpy.ops.render.render(write_still=True)
