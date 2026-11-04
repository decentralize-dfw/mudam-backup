import bpy,bmesh,json,hashlib,numpy as np,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');W=R/'reports'
src=sys.argv[sys.argv.index('--')+1] if '--'in sys.argv else 'MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v011.blend'
dst=sys.argv[sys.argv.index('--')+2] if '--'in sys.argv else 'MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v012.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/src));d=json.loads((W/'R588_FACADE_JOIN_DESIGN.json').read_text());c=d['sourcePlane'];outline=d['outline']
def z(x,y):return c[0]*x+c[1]*y+c[2]
def sig(o):
 a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);b=np.empty(len(o.data.loops),dtype=np.int32);o.data.loops.foreach_get('vertex_index',b)
 return hashlib.sha256(a.tobytes()+b.tobytes()+str(o.matrix_world).encode()).hexdigest()
def distance(p):
 best=1e9
 for a,b in zip(outline,outline[1:]+outline[:1]):
  a=np.array(a);ab=np.array(b)-a
  if ab@ab<1e-16:continue
  t=np.clip((p-a)@ab/(ab@ab),0,1);best=min(best,float(np.linalg.norm(p-a-ab*t)))
 return best
def check(o):
 bm=bmesh.new();bm.from_mesh(o.data);r=dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();return r
def cut_terrain(target):
 old=target.data;old.calc_loop_triangles();uvs=list(old.uv_layers);verts=[];faces=[];attrs=[];mis=[]
 def clip(points,a,b,sign,inside):
  out=[]
  for j,P in enumerate(points):
   Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-9 if inside else dp<=1e-9;iq=dq>=-1e-9 if inside else dq<=1e-9
   if ip:out.append(P)
   if ip!=iq:
    t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
  return out
 for tr in old.loop_triangles:
  points=[]
  for li in tr.loops:
   p=old.vertices[old.loops[li].vertex_index].co;points.append(tuple(p)+tuple(v for layer in uvs for v in layer.data[li].uv)+tuple(old.corner_normals[li].vector))
  chunks=[points]
  if max(p[0]for p in points)>-17.01 and min(p[0]for p in points)<-10.2 and max(p[1]for p in points)>7.2 and min(p[1]for p in points)<12.08:
   for region in d['triangles']:
    sign=1 if sum(region[i][0]*region[(i+1)%3][1]-region[(i+1)%3][0]*region[i][1]for i in range(3))>0 else -1;result=[]
    for chunk in chunks:
     if max(p[0]for p in chunk)<min(p[0]for p in region) or min(p[0]for p in chunk)>max(p[0]for p in region) or max(p[1]for p in chunk)<min(p[1]for p in region) or min(p[1]for p in chunk)>max(p[1]for p in region):result.append(chunk);continue
     remaining=chunk
     for i,a in enumerate(region):
      if len(remaining)<3:break
      b=region[(i+1)%3];outside=clip(remaining,a,b,sign,False)
      if len(outside)>2:result.append(outside)
      remaining=clip(remaining,a,b,sign,True)
    chunks=result
  for chunk in chunks:
   for i in range(1,len(chunk)-1):
    tri=[chunk[0],chunk[i],chunk[i+1]]
    if (Vector(tri[1][:3])-Vector(tri[0][:3])).cross(Vector(tri[2][:3])-Vector(tri[0][:3])).length<1e-9:continue
    k=len(verts);verts.extend(p[:3]for p in tri);attrs.extend(p[3:]for p in tri);faces.append((k,k+1,k+2));mis.append(tr.material_index)
 new=bpy.data.meshes.new('R588_TERRAIN_CORNER_CLEARANCE');new.from_pydata(verts,[],faces);new.update()
 for mat in old.materials:new.materials.append(mat)
 for i,f in enumerate(new.polygons):f.material_index=mis[i];f.use_smooth=True
 for j,layer in enumerate(uvs):
  uv=new.uv_layers.new(name=layer.name)
  for l in new.loops:uv.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
 new.normals_split_custom_set([Vector(attrs[l.vertex_index][-3:]).normalized()for l in new.loops]);target.data=new
before={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'};adjust=[]
for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1']:
 o=bpy.data.objects[name];o.data.calc_loop_triangles();bv=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(t.vertices)for t in o.data.loop_triangles],all_triangles=True);changes=[]
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if p.z< -4.5 or not(-18<p.x<-9 and 6<p.y<12.6):continue
  dist=distance(np.array([p.x,p.y]))
  if dist>=1:continue
  hit=bv.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),20)[0]
  if hit is None or hit.z< -4.5:continue
  w=1-dist;w=w*w*(3-2*w);delta=(z(p.x,p.y)-hit.z)*w
  if abs(delta)>.5:raise RuntimeError(('Excessive inherited grade change',name,list(p),delta))
  if abs(delta)>1e-7:v.co.z+=delta;changes.append(abs(delta))
 o.data.update();adjust.append(dict(name=name,changedVertices=len(changes),maximumVerticalAdjustment=max(changes,default=0)))
xy=[];lookup={}
def ix(p):
 p=tuple(round(v,6)for v in p)
 if p not in lookup:lookup[p]=len(xy);xy.append(p)
 return lookup[p]
fs=[tuple(ix(p)for p in tri)for tri in d['triangles']];n=len(xy)
from collections import Counter
edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3))
vs=[(x,y,z(x,y))for x,y in xy]+[(x,y,-6.2)for x,y in xy]
faces=fs+[tuple(n+i for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1]
me=bpy.data.meshes.new('R588_WEST_GLASS_CORNER_GROUND');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
me.materials.append(bpy.data.materials['R588_WEST_EARTH_NO_STALE_AO'])
for un in ['R545_GROUND_ATLAS','R545_MICRO_2M']:
 uv=me.uv_layers.new(name=un)
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((p.x+80)/160,(p.y+85)/180)if un=='R545_GROUND_ATLAS'else(p.x/2,p.y/2)
o['level_id']='SITE';o['source']=d['method'];o['technical_base']='-6.2m closed substrate, not surveyed foundation'
# Remove only overlaps within this closed new substrate; neighboring grade is unchanged outside the one-metre join band.
for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1','R152_CLASS2_TERRAIN']:
 target=bpy.data.objects[name]
 if name=='R152_CLASS2_TERRAIN':cut_terrain(target);continue
 if name=='R152_CLASS2_TERRAIN':
  old=target.data;old.calc_loop_triangles();oldvs=[v.co.copy()for v in old.vertices];oldtris=[tuple(t.vertices)for t in old.loop_triangles];oldns=[[old.corner_normals[i].vector.copy()for i in t.loops]for t in old.loop_triangles];ntree=BVHTree.FromPolygons(oldvs,oldtris,all_triangles=True);nmap={tuple(round(v,6)for v in old.vertices[l.vertex_index].co):old.corner_normals[l.index].vector.copy()for l in old.loops}
 cutter=o
 if name=='R152_CLASS2_TERRAIN':
  cm=me.copy();cutter=bpy.data.objects.new('R588_TEMP_CORNER_GROUND_CUT',cm);bpy.context.scene.collection.objects.link(cutter)
  for v in cm.vertices:v.co.z=20 if v.index<n else -20
  cm.update()
 mod=target.modifiers.new('R588_CORNER_SUBSTRATE_CLEARANCE','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
 if cutter!=o:bpy.data.objects.remove(cutter,do_unlink=True)
 if name=='R152_CLASS2_TERRAIN':
  nn=[]
  for l in target.data.loops:
   p=target.data.vertices[l.vertex_index].co;k=tuple(round(v,6)for v in p);normal=nmap.get(k)
   if normal is None:
    q,_,idx,_=ntree.find_nearest(p);tri=oldtris[idx];normal=barycentric_transform(q,*[oldvs[i]for i in tri],*oldns[idx]).normalized()
   nn.append(normal)
  target.data.normals_split_custom_set(nn)
 else:
  target.data.calc_loop_triangles();gbv=BVHTree.FromPolygons([v.co for v in target.data.vertices],[list(t.vertices)for t in target.data.loop_triangles],all_triangles=True);deltas=[]
  for v in target.data.vertices:
   p=v.co.copy()
   if p.z< -4.5 or not(-18<p.x<-9 and 6<p.y<12.6):continue
   dist=distance(np.array([p.x,p.y]))
   if dist>=1:continue
   hit=gbv.ray_cast(Vector((p.x,p.y,0)),Vector((0,0,-1)),20)[0]
   if hit is None or hit.z< -4.5:continue
   w=1-dist;w=w*w*(3-2*w);delta=(z(p.x,p.y)-hit.z)*w
   if abs(delta)>1.0:raise RuntimeError(('New boundary grade mismatch',name,list(p),delta))
   v.co.z+=delta;deltas.append(abs(delta))
  adjust.append(dict(name=name,postCutBoundaryVertices=len(deltas),maximumVerticalAdjustment=max(deltas,default=0)))
  bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5);bmesh.ops.delete(bm,geom=[e for e in bm.edges if e.is_wire],context='EDGES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free()
checks=[check(bpy.data.objects[n])for n in ['R588_WEST_GLASS_CORNER_GROUND','R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1']];assert all(r['nonManifold']==r['zeroArea']==0 for r in checks),checks
out=R/'scenes'/dst;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));after={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'};changed=[k for k in before if before[k]!=after.get(k)];allowed=[a['name']for a in adjust]+['R152_CLASS2_TERRAIN'];assert set(changed)<=set(allowed),changed
checks=[check(bpy.data.objects[r['name']])for r in checks];assert all(r['nonManifold']==r['zeroArea']==0 for r in checks),checks
report=dict(scene=str(out),sourceScene=src,reopened=True,checks=checks,changed=changed,unchanged=len(before)-len(changed),adjustments=adjust,area=d['area'],sourceHeldout=d['sourceHeldout'],heldoutRMS=d['heldoutRMS'],heldoutMax=d['heldoutMax'],accepted=False,published=False)
(R/'reports/R588_FACADE_CORNER_BUILD.json').write_text(json.dumps(report,indent=2));print('JOIN_OK',report,flush=True)
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-12,8,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=10;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_facade_join_rebuilt.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-62,-19,39);s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=56;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.filepath=str(R/'renders/qa/R588_west_v012.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-40,8,65);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=38;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R588_west_top_v012.png');bpy.ops.render.render(write_still=True)
