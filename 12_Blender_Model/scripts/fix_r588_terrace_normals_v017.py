import bpy,json,numpy as np,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];W=R/'reports'
SRC='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v016.blend';DST='MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v017.blend'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/SRC));o=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];me=o.data
v15=json.loads((R/'reports/R588_WHOLE_TERRACE_V015_BUILD.json').read_text());changed={r['index']for r in v15['changes']}
def datahash(me):
 a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);b=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',b);h=hashlib.sha256(a.tobytes()+b.tobytes())
 for u in me.uv_layers:
  a=np.empty(len(u.data)*2,np.float32);u.data.foreach_get('uv',a);h.update(u.name.encode()+a.tobytes())
 return h.hexdigest()
def nhash(me):
 return hashlib.sha256(np.array([v.vector[:]for v in me.corner_normals],np.float32).tobytes()).hexdigest()
allbefore={q.name:datahash(q.data)for q in bpy.context.scene.objects if q.type=='MESH'};normalbefore=nhash(me);old=[n.vector.copy()for n in me.corner_normals]
# The walking surface normal must not average the closed body's vertical walls.
# Keep actual steep banks/caps and every unrelated corner normal unchanged.
topfaces=[f for f in me.polygons if f.normal.z>.90];affected=set(changed)
for f in topfaces:
 if any(i in changed for i in f.vertices):affected.update(f.vertices)
acc={i:Vector((0,0,0))for i in affected}
for f in topfaces:
 for i in f.vertices:
  if i in affected:acc[i]+=f.normal*f.area
for v in acc.values():
 if v.length:v.normalize()
new=list(old);rows=[]
for f in topfaces:
 for li in f.loop_indices:
  vi=me.loops[li].vertex_index
  if vi in affected and acc[vi].length:
   new[li]=acc[vi];angle=old[li].angle(new[li],0)*180/np.pi
   if angle>1e-5:rows.append(dict(loop=li,vertex=vi,angleDegrees=float(angle),old=list(old[li]),new=list(new[li])))
me.normals_split_custom_set(new);me.update();assert datahash(me)==allbefore[o.name]
report=dict(scene=DST,sourceScene=SRC,object=o.name,geometryUVHash=allbefore[o.name],normalBefore=normalbefore,normalAfter=nhash(me),changedTopLoops=len(rows),maximumNormalAngleDegrees=max(r['angleDegrees']for r in rows),changes=rows,method='Area-weighted up-facing walking-surface normals exclude closed technical vertical side walls; no vertex/UV/material changes.',accepted=False,published=False)
out=R/'scenes'/DST;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));after={q.name:datahash(q.data)for q in bpy.context.scene.objects if q.type=='MESH'};assert after==allbefore;report['reopened']=True;report['allMeshGeometryUVUnchanged']=len(after);report['normalAfterReopen']=nhash(bpy.data.objects['R322_WEST_MUSEUM_TERRACE'].data);(R/'reports/R588_TERRACE_NORMALS_V017.json').write_text(json.dumps(report,indent=2));print('V017_READY',DST,report['changedTopLoops'],report['maximumNormalAngleDegrees'],flush=True)
s=bpy.context.scene
for ob in s.objects:
 if ob.name.startswith('R158_TREE_'):ob.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-12,8,40));s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=10;s.camera.rotation_euler=(0,0,0);s.render.filepath=str(R/'renders/qa/R588_facade_join_v017.png');bpy.ops.render.render(write_still=True)
