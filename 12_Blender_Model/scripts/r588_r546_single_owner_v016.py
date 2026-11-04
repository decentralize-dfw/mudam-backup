import bpy,bmesh,json,hashlib
import numpy as np
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');W=R/'reports'
BASE=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v015.blend';OUT=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v016.blend'
assert BASE.exists(),BASE
bpy.ops.wm.open_mainfile(filepath=str(BASE));NAME='R546_WEST_MOAT_EDGE_1';REST='R588_WEST_CLASS2_GROUND_RESTORATION'
def sig(o):
 m=o.data;v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v);l=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',l)
 return hashlib.sha256(v.tobytes()+l.tobytes()+str((o.matrix_world,o.hide_render)).encode()).hexdigest()
def tree(o):
 m=o.data;m.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices)for t in m.loop_triangles],all_triangles=True)
before={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};o=bpy.data.objects[NAME];old=o.data;old.calc_loop_triangles();resttree=tree(bpy.data.objects[REST]);materials=list(old.materials)
oldtop=[t for t in old.loop_triangles if t.normal.z>.05];keep=[t for t in oldtop if max(old.vertices[i].co.y for i in t.vertices)<=3.20001];removed=[t for t in oldtop if t not in keep];assert len(keep)==6,(len(keep),len(oldtop))
# Entire removed northern wing is already owned by the valid restoration ground.
ownership=[]
for t in removed:
 a=np.array([list(old.vertices[i].co)for i in t.vertices])
 for w in [[1/3]*3,[.8,.1,.1],[.1,.8,.1],[.1,.1,.8]]:
  p=np.array(w)@a;hit,n,fi,dist=resttree.ray_cast(Vector((p[0],p[1],0)),Vector((0,0,-1)),20)
  assert hit is not None,('Restoration coverage missing',p.tolist());ownership.append(dict(x=float(p[0]),y=float(p[1]),oldZ=float(p[2]),restorationZ=hit.z))
def area_xy(t):
 a=[old.vertices[i].co for i in t.vertices];return abs((a[1]-a[0]).cross(a[2]-a[0]).z)*.5
# Original UVs are world-planar. Retain their exact metric mappings.
uvcoef={};A=np.array([[old.vertices[l.vertex_index].co.x,old.vertices[l.vertex_index].co.y,1]for l in old.loops])
for l in old.uv_layers:
 uv=np.array([list(x.uv)for x in l.data]);co=np.linalg.lstsq(A,uv,rcond=None)[0];err=float(np.max(abs(A@co-uv)));assert err<1e-5,(l.name,err);uvcoef[l.name]=co
ids=sorted({i for t in keep for i in t.vertices});lookup={oldid:newid for newid,oldid in enumerate(ids)};verts=[tuple(old.vertices[i].co)for i in ids];faces=[tuple(lookup[i]for i in t.vertices)for t in keep];ns=[[old.corner_normals[li].vector.copy()for li in t.loops]for t in keep];n=len(verts);topcount=len(faces)
# Preserve original 0.18 m closed substrate depth exactly where it remains.
xygroups=defaultdict(list)
for v in old.vertices:xygroups[(round(v.co.x,5),round(v.co.y,5))].append(v.co.z)
thickness=[]
for x,y,z in verts:
 zs=xygroups[(round(x,5),round(y,5))];thickness.append(max(zs)-min(zs))
assert max(abs(v-.18)for v in thickness)<1e-5,thickness
allverts=verts+[(x,y,z-thickness[i])for i,(x,y,z)in enumerate(verts)];edges=defaultdict(list)
for face in faces:
 for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))].append((a,b))
boundary=[e[0]for e in edges.values()if len(e)==1];allfaces=faces+[tuple(i+n for i in reversed(f))for f in faces]+[(a+n,b+n,b,a)for a,b in boundary]
me=bpy.data.meshes.new(NAME+'_SINGLE_OWNER_v016');me.from_pydata(allverts,[],allfaces);me.update()
for ma in materials:me.materials.append(ma)
for lname,co in uvcoef.items():
 l=me.uv_layers.new(name=lname)
 for loop in me.loops:
  v=me.vertices[loop.vertex_index].co;l.data[loop.index].uv=np.array([v.x,v.y,1.])@co
norms=[]
for fi,f in enumerate(me.polygons):
 f.use_smooth=fi<topcount
 for li in f.loop_indices:norms.append(ns[fi][li-f.loop_start]if fi<topcount else f.normal.copy())
me.normals_split_custom_set(norms);o.data=me;o['R588_surface_ownership']='Duplicate R546 north wing removed where R588 restoration already provides ground; only original south footprint retained. No new source-resampled surface.'
bm=bmesh.new();bm.from_mesh(me);nonman=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);vol=bm.calc_volume(signed=False);bm.free();assert nonman==zero==0,(nonman,zero)
newtree=tree(o);rays=[]
for x in np.linspace(-32.08,-30.81,30):
 p,n,fi,d=newtree.ray_cast(Vector((x,3.2-1e-6,0)),Vector((0,0,-1)),20);q,nn,fj,dd=resttree.ray_cast(Vector((x,3.2+1e-6,0)),Vector((0,0,-1)),20);assert p is not None and q is not None; rays.append(dict(x=float(x),gap=abs(p.z-q.z)))
sourcecheck=[]
for x,y,z in [(-32.6027,3.3973,-6.7172255516),(-32.43226,3.33181,-6.7534809113),(-32.2,3.2426,-6.7707958221)]:
 p,n,fi,d=resttree.ray_cast(Vector((x,y+1e-5,0)),Vector((0,0,-1)),20);assert p is not None;sourcecheck.append(dict(x=x,y=y,sourceZ=z,keptGroundZ=p.z,residual=p.z-z))
changed=[n for n,h in before.items()if sig(bpy.data.objects[n])!=h];assert changed==[NAME],changed
report={'base':str(BASE),'scene':str(OUT),'method':'Complete duplicate-north-wing removal with one surface owner, preserving source-fitted shared edge and original remaining southern substrate.','changedMeshes':changed,'unchangedOtherMeshes':len(before)-1,'oldFootprintArea':sum(area_xy(t)for t in oldtop),'retainedSouthArea':sum(area_xy(t)for t in keep),'removedDuplicateArea':sum(area_xy(t)for t in removed),'removedRegionOwnershipSamples':ownership,'sourceCheckVisibleWestReturn':sourcecheck,'sourceCheckRMS':float(np.sqrt(np.mean([p['residual']**2 for p in sourcecheck]))),'sourceCheckMax':max(abs(p['residual'])for p in sourcecheck),'nonManifold':nonman,'zeroArea':zero,'volume':vol,'sharedEdgeMaxGap':max(q['gap']for q in rays),'sharedEdgeSamples':rays,'material':materials[0].name,'uvLayers':list(uvcoef),'originalTopCoordinatesPreserved':True,'restorationGeometryUnchanged':True,'trueDiagonalR152BankUnchanged':True,'limits':['Occluded northern source rays hit historical retaining wall, not ground; no hidden-floor height claimed from them.','Restoration surface retained from the prior class2-ground reconstruction; west exposed ACT residual max ~6 cm.','No complete museum-ring acceptance implied; AO and GLB/browser validation remain separate.'],'accepted':False,'published':False}
assert report['sharedEdgeMaxGap']<1e-5
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True);bpy.ops.wm.open_mainfile(filepath=str(OUT));report['reopened']=True;assert [n for n,h in before.items()if sig(bpy.data.objects[n])!=h]==[NAME]
(W/'R588_R546_SINGLE_OWNER_V016_BUILD.json').write_text(json.dumps(report,indent=2));print('R588_V016_GEOMETRY_READY',json.dumps(report),flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R588_west_v016.png');bpy.ops.render.render(write_still=True);print('R588_V016_RENDER_READY',flush=True)
