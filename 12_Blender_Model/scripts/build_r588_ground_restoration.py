import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
W=R/'reports'
d=json.loads((W/'R588_GROUND_RESTORE_FROM_AUTHORED_R154.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/d['baseScene']))
def sig(o):
 a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a)
 b=np.empty(len(o.data.loops),dtype=np.int32);o.data.loops.foreach_get('vertex_index',b)
 return hashlib.sha256(a.tobytes()+b.tobytes()+str((o.matrix_world,o.hide_render)).encode()).hexdigest()
before={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects['R152_CLASS2_TERRAIN']
me=bpy.data.meshes.new('R588_WEST_CLASS2_GROUND_RESTORATION');me.from_pydata(d['closedVertices'],[],d['closedFaces']);me.update()
ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob)
for m in terrain.data.materials:me.materials.append(m)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
uvs=[]
for layer in terrain.data.uv_layers:
 inds=np.linspace(0,len(terrain.data.loops)-1,min(4000,len(terrain.data.loops)),dtype=int)
 xyz=np.array([list(terrain.matrix_world@terrain.data.vertices[terrain.data.loops[i].vertex_index].co) for i in inds])
 A=np.column_stack([xyz[:,:2],np.ones(len(xyz))]);uv=np.array([list(layer.data[i].uv) for i in inds]);coef=np.linalg.lstsq(A,uv,rcond=None)[0]
 err=float(np.max(np.abs(A@coef-uv)))
 # Existing terrain atlas layers are world-planar. Preserve their transform exactly.
 if err>1e-4:raise RuntimeError(('Non-planar UV requires explicit interpolation',layer.name,err))
 out=me.uv_layers.new(name=layer.name)
 for li,loop in enumerate(me.loops):
  p=me.vertices[loop.vertex_index].co;out.data[li].uv=np.array([p.x,p.y,1])@coef
 uvs.append(dict(name=layer.name,maximumFitResidual=err,transform=coef.tolist()))
for f in me.polygons:f.use_smooth=f.normal.z>.5
ob['source']=d['source'];ob['level_id']='SITE';ob['scope']='Restore accidental holes between existing independently authored terrain and the western museum retaining wall.'
ob['uncertainty']=d['sourceLimits'];ob['technical_slab_thickness']=d['technicalSlabThickness']
def check():
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[ob.name].data)
 c=dict(vertices=len(bm.verts),faces=len(bm.faces),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=False));bm.free();return c
c=check();assert c['nonManifold']==c['zeroArea']==0,c
out=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v009.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);name=ob.name;bpy.ops.wm.open_mainfile(filepath=str(out));ob=bpy.data.objects[name]
after={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'};changed=[k for k in before if before[k]!=after.get(k)];assert not changed,changed
c=check();assert c['nonManifold']==c['zeroArea']==0,c
report=dict(scene=str(out),baseScene=d['baseScene'],reopened=True,checks=c,added=name,inheritedMeshesUnchanged=len(before),changed=changed,restoredArea=d['restoreArea'],UV=uvs,source=d['source'],sourceLimits=d['sourceLimits'],maxBoundaryAdjustment=d['boundarySnapMaxAdjustment'],neighborDisagreement=d['maxCurrentNeighborDisagreement'],accepted=False,published=False)
(R/'reports/R588_GROUND_BUILD.json').write_text(json.dumps(report,indent=2));print('R588_GROUND_OK',report,flush=True)
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R588_west_v009.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-40,8,65);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=38;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R588_west_top_v009.png');bpy.ops.render.render(write_still=True)
