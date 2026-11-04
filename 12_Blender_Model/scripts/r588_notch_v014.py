import bpy,bmesh,json,hashlib,time
import numpy as np
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');W=R/'reports'
BASE=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v013.blend'
OUT=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v014.blend'
TARGETS=['R546_WEST_MOAT_EDGE_1','R588_WEST_CLASS2_GROUND_RESTORATION']
CONTROL=[[-32.,-6.799160957336426],[-31.6,-6.769585609436035],[-31.3,-6.749593734741211],[-31.,-6.741000175476074],[-30.8,-6.736425399780273]]
a=np.array(CONTROL);coef=np.linalg.lstsq(np.c_[a[:,0],np.ones(len(a))],a[:,1],rcond=None)[0]
def target(x):return float(coef[0]*x+coef[1])
assert BASE.exists(),BASE
bpy.ops.wm.open_mainfile(filepath=str(BASE))
def sig(o):
 m=o.data;a=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',a);b=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',b)
 return hashlib.sha256(a.tobytes()+b.tobytes()+str((o.matrix_world,o.hide_render)).encode()).hexdigest()
def uvhash(m):
 out={}
 for l in m.uv_layers:
  a=np.empty(len(l.data)*2,dtype=np.float32);l.data.foreach_get('uv',a);out[l.name]=hashlib.sha256(a.tobytes()).hexdigest()
 return out
before={o.name:sig(o)for o in bpy.data.objects if o.type=='MESH'};report={'base':str(BASE),'scene':str(OUT),'method':'Five ACT ground height controls define one independent fitted straight shared edge; original neighboring vertices and topology preserved. No scan mesh copied.','source_controls_xy_z':[[x,3.2,z]for x,z in CONTROL],'source':'museum_ring_reference.blend vertical ray controls, normal.z .8587-.9519','plane_line_z_mx_b':coef.tolist(),'sourceFitRMS':float(np.sqrt(np.mean((a[:,1]-(a[:,0]*coef[0]+coef[1]))**2))),'sourceFitMax':float(np.max(abs(a[:,1]-(a[:,0]*coef[0]+coef[1])))),'objects':{},'aoTargets':TARGETS,'accepted':False,'published':False}
for name in TARGETS:
 o=bpy.data.objects[name];m=o.data;uvbefore=uvhash(m);oldnorm=[n.vector.copy()for n in m.corner_normals];oldcoords=[v.co.copy()for v in m.vertices]
 # Both solid meshes have coincident XY top/bottom pairs. Equal Z delta preserves thickness.
 byxy=defaultdict(list)
 for v in m.vertices:byxy[(round(v.co.x,5),round(v.co.y,5))].append(v.index)
 moved=[]
 for (x,y),indices in byxy.items():
  if abs(y-3.2)>1e-4 or not(-32.09<=x<=-30.79):continue
  top=max(m.vertices[i].co.z for i in indices);delta=target(x)-top
  for i in indices:
   m.vertices[i].co.z+=delta;moved.append(i)
 m.update();moved=set(moved)
 touched=[p for p in m.polygons if any(i in moved for i in p.vertices)]
 # Only affected normals change; preserve all unchanged corner normals and UVs.
 incident=defaultdict(list)
 for p in m.polygons:
  for vi in p.vertices:incident[vi].append((p.normal.copy(),p.area))
 norms=list(oldnorm)
 for p in touched:
  for li in p.loop_indices:
   vi=m.loops[li].vertex_index
   if p.use_smooth:
    nn=sum((n*area for n,area in incident[vi]if n.dot(p.normal)>.55),Vector((0,0,0)))
    norms[li]=nn.normalized()if nn.length>1e-8 else p.normal.copy()
   else:norms[li]=p.normal.copy()
 m.normals_split_custom_set(norms)
 bm=bmesh.new();bm.from_mesh(m);nonman=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();assert nonman==zero==0,(name,nonman,zero)
 assert uvbefore==uvhash(m),name
 assert all((v.co-oldcoords[v.index]).length==0 for v in m.vertices if v.index not in moved)
 edge=[]
 for (x,y),indices in byxy.items():
  if abs(y-3.2)<1e-4 and -32.09<=x<=-30.79:
   edge.append(dict(x=x,y=y,before=max(oldcoords[i].z for i in indices),after=max(m.vertices[i].co.z for i in indices),target=target(x)))
 support=[m.vertices[i].co for p in touched for i in p.vertices]
 report['objects'][name]=dict(movedVertices=len(moved),changedFaces=len(touched),nonManifold=nonman,zeroArea=zero,maxVertexDelta=max((m.vertices[i].co-oldcoords[i]).length for i in moved),changedFaceBounds=[[min(v[k]for v in support),max(v[k]for v in support)]for k in range(3)],sharedEdge=edge,uvsUnchanged=True,topologyUnchanged=True,materialsUnchanged=True)
 o['R588_shared_edge_correction']='Five ACT controls, z=m*x+b at y=3.2; neighbor-row planar interpolation, no new scanned surface.'
# Match lighting normals only along the artificial shared join, averaging the
# two authored top grades. The actual distant diagonal bank is untouched.
def bv_for(o):
 m=o.data;m.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices)for t in m.loop_triangles],all_triangles=True)
join_bvs={n:bv_for(bpy.data.objects[n])for n in TARGETS}
samples=[]
for x in [-32.08,-31.8,-31.6,-31.3,-31.,-30.81]:
 ns=[]
 for name,dy in [(TARGETS[0],-0.0001),(TARGETS[1],0.0001)]:
  p,n,fi,d=join_bvs[name].ray_cast(Vector((x,3.2+dy,0)),Vector((0,0,-1)),20)
  if p is not None:ns.append(n)
 if len(ns)==2:samples.append((x,tuple((ns[0]+ns[1]).normalized()),float(ns[0].angle(ns[1]))))
assert len(samples)==6,samples
normalcoef=np.linalg.lstsq(np.c_[[x for x,n,a in samples],np.ones(len(samples))],np.array([n for x,n,a in samples]),rcond=None)[0]
report['sharedEdgeNormalMethod']='Same linearly varying normal at both meshes, fitted to average neighboring authored grade normals; only shared-join corner normals and touching R546 top smooth flags adjusted.'
report['sharedEdgeOriginalGradeAnglesDegrees']=[float(a*180/np.pi)for x,n,a in samples]
report['materialContinuity']={}
for name in TARGETS:
 m=bpy.data.objects[name].data;nn=[n.vector.copy()for n in m.corner_normals];count=0
 # A solid has matching top/bottom XY. Only higher Z member at each XY receives shared normal.
 tops=defaultdict(lambda:-1e20)
 for v in m.vertices:tops[(round(v.co.x,5),round(v.co.y,5))]=max(tops[(round(v.co.x,5),round(v.co.y,5))],v.co.z)
 for poly in m.polygons:
  if poly.normal.z<=0:continue
  for li in poly.loop_indices:
   v=m.vertices[m.loops[li].vertex_index];x,y,z=v.co
   if abs(y-3.2)<1e-4 and -32.09<=x<=-30.79 and abs(z-tops[(round(x,5),round(y,5))])<1e-5:
    nn[li]=Vector(np.array([x,1.])@normalcoef).normalized();poly.use_smooth=True;count+=1
 m.normals_split_custom_set(nn)
 report['objects'][name]['sharedNormalCorners']=count
 report['materialContinuity'][name]={'materials':[ma.name for ma in m.materials],'explicitUVMaps':sorted({nd.uv_map for ma in m.materials if ma and ma.use_nodes for nd in ma.node_tree.nodes if nd.type=='UVMAP'}),'uvLayers':[l.name for l in m.uv_layers],'activeUV':m.uv_layers.active.name if m.uv_layers.active else None}
assert report['materialContinuity'][TARGETS[0]]['materials']==report['materialContinuity'][TARGETS[1]]['materials']
changed=[n for n,h in before.items()if h!=sig(bpy.data.objects[n])];assert set(changed)==set(TARGETS),changed
report['changedMeshes']=changed;report['unchangedOtherMeshes']=len(before)-len(changed)
def bv(o):
 m=o.data;m.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[list(t.vertices)for t in m.loop_triangles],all_triangles=True)
bvs={n:bv(bpy.data.objects[n])for n in TARGETS};rays=[]
for x in np.linspace(-32.08,-30.81,30):
 row={'x':float(x),'y':3.2,'z':{}}
 for name,b in bvs.items():
  p,n,fi,d=b.ray_cast(Vector((x,3.2+1e-6,0)),Vector((0,0,-1)),20);assert p is not None,(name,x);row['z'][name]=p.z
 row['delta']=max(row['z'].values())-min(row['z'].values());rays.append(row)
report['sharedEdgeRaySamples']=rays;report['sharedEdgeMaxSeparation']=max(q['delta']for q in rays);assert report['sharedEdgeMaxSeparation']<1e-5,report['sharedEdgeMaxSeparation']
report['limits']=['ACT control-line fit is source-supported within scan resolution, not a surveyed elevation certificate.','Existing neighbors remain fixed: R588 first north row y=3.45 (local 0.25 m transition); R546 own adjacent boundaries y=2.7047..3.88945 remain unchanged.','Real steep diagonal R152 bank is unchanged. Its dark shading is not repaired by flattening or smoothing.','Affected surfaces need fresh AO bake before final publication.']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True);bpy.ops.wm.open_mainfile(filepath=str(OUT));report['reopened']=True
assert set(n for n,h in before.items()if h!=sig(bpy.data.objects[n]))==set(TARGETS)
(W/'R588_NOTCH_V014_BUILD.json').write_text(json.dumps(report,indent=2));print('R588_NOTCH_V014_READY',json.dumps(report),flush=True)
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R588_west_v014.png');bpy.ops.render.render(write_still=True)
print('R588_NOTCH_V014_RENDER_READY',flush=True)
