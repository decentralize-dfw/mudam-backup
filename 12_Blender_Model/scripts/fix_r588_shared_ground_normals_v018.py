import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R/'reports'
SRC='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v017.blend';DST='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v018.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/SRC))
def h(me):
 a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);b=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',b);z=hashlib.sha256(a.tobytes()+b.tobytes())
 for u in me.uv_layers:
  v=np.empty(len(u.data)*2,np.float32);u.data.foreach_get('uv',v);z.update(u.name.encode()+v.tobytes())
 return z.hexdigest()
before={o.name:h(o.data)for o in bpy.context.scene.objects if o.type=='MESH'};d=json.loads((W/'R588_FACADE_JOIN_DESIGN.json').read_text());cp=d['sourcePlane'];poly=[np.array(p)for p in d['outline']];nc=Vector((-cp[0],-cp[1],1)).normalized();nf=Vector((-.0206561516970396,-.019071225076913834,.9996047616004943)).normalized();a=np.array([-12.414369583129883,7.20503568649292]);b=np.array([-2.4570999145507812,-.0714000016450882]);L=float(np.linalg.norm(b-a));t=(b-a)/L

def ds(p,a,b):
 ab=b-a;tt=np.clip((p-a)@ab/(ab@ab),0,1)if ab@ab>1e-18 else 0;return float(np.linalg.norm(p-a-ab*tt))
def sm(v):v=float(np.clip(v,0,1));return v*v*(3-2*v)
rows=[]
for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1']:
 me=bpy.data.objects[name].data;old=[v.vector.copy()for v in me.corner_normals];new=list(old);nr=0
 for f in me.polygons:
  if f.normal.z<.9:continue
  f.use_smooth=True
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;xy=np.array(p[:2]);edgeDist=ds(xy,a,b);cornerDist=min(ds(xy,aa,bb)for aa,bb in zip(poly,poly[1:]+poly[:1]));s=float(np.clip((xy-a)@t/L,0,1));ne=(nc*(1-s)+nf*s).normalized()
   if edgeDist<.6 and (name.startswith('R322')or edgeDist<.0002):
    w=sm(1-edgeDist/.6);new[li]=(old[li]*(1-w)+ne*w).normalized();nr+=1
   if cornerDist<.6 and cornerDist<edgeDist:
    w=sm(1-cornerDist/.6);new[li]=(old[li]*(1-w)+nc*w).normalized();nr+=1
 me.normals_split_custom_set(new);rows.append(dict(name=name,updatedLoops=nr));assert h(me)==before[name]
out=R/'scenes'/DST;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));after={o.name:h(o.data)for o in bpy.context.scene.objects if o.type=='MESH'};assert before==after
report=dict(scene=DST,sourceScene=SRC,method='One common top-surface normal field along connected R322/R549/new-corner boundary;600mm interpolation to interior normals. Positions/UVs/materials unchanged.',geometryUVUnchanged=len(before),reopened=True,objects=rows,accepted=False,published=False);(R/'reports/R588_SHARED_GROUND_NORMALS_V018.json').write_text(json.dumps(report,indent=2));print('V018_READY',report,flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-12,8,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=10;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_facade_join_v018.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('R588_DIAGNOSTIC_FLAT');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.3,.2,1);bs.inputs['Roughness'].default_value=.8
for name in ['R322_WEST_MUSEUM_TERRACE','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1','R588_WEST_GLASS_CORNER_GROUND']:
 me=bpy.data.objects[name].data;me.materials.clear();me.materials.append(mat)
 for f in me.polygons:f.material_index=0
s.render.filepath=str(R/'renders/qa/R588_facade_join_v018_flat.png');bpy.ops.render.render(write_still=True)