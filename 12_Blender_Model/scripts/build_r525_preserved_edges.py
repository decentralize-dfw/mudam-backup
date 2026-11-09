import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R523_BATI_SUR_TERAS_HENDEK_ADAY_v001.blend'))
print('OPENED',flush=True)
d=json.loads((R/'reports/R525_PRESERVED_EDGE_MESH.json').read_text());me=bpy.data.meshes.new('R525_PRESERVED_TERRACE_EDGES');me.from_pydata(d['vertices'],[],d['faces']);me.update();o=bpy.data.objects.new('R525_WEST_TERRACE_EXISTING_SLOPING_EDGES',me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R523_WEST_TERRACE_MINERAL'])
print('MESH_READY',flush=True)
from collections import Counter
vs=d['vertices'];fs=d['faces'];byedge={}
for fi,f in enumerate(fs):
 for i in range(3):byedge.setdefault(tuple(sorted((f[i],f[(i+1)%3]))),[]).append(fi)
adj={i:set()for i in range(len(fs))}
for ids in byedge.values():
 for i in ids:adj[i].update(set(ids)-{i})
visited=set();newvs=[];newfs=[]
for seed in range(len(fs)):
 if seed in visited:continue
 stack=[seed];component=[]
 while stack:
  i=stack.pop()
  if i in visited:continue
  visited.add(i);component.append(i);stack.extend(adj[i]-visited)
 remap={}
 for i in component:
  for v in fs[i]:
   if v not in remap:remap[v]=len(newvs);newvs.append(vs[v])
  newfs.append([remap[v]for v in fs[i]])
vs,fs=newvs,newfs;n=len(vs);
edges=Counter(tuple(sorted((t[i],t[(i+1)%3])))for t in fs for i in range(3));assert max(edges.values())<=2
allvs=vs+[(x,y,-10.5)for x,y,z in vs];allfs=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1]
me.clear_geometry();me.from_pydata(allvs,[],allfs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(check.values()),check;bm.to_mesh(me);bm.free()
for name in ('UVMap','R497_MINERAL_METRIC'):
 uv=me.uv_layers.new(name=name)
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/3,v.y/3)
o['source']='Preserved previously source-supported sloping edges of R322 outside replacement terrace and lower moat floor; clipped to avoid duplicated faces. R524 probes confirm two source heights within 0.03m.'
out=R/'scenes/MUDAM_R525_BATI_TERAS_EGIMLI_KENAR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));dg=bpy.context.evaluated_depsgraph_get();probes=[]
for x,y,z in [(-22.375,1.5,-5.248085),(-14.25,.0375,-3.967213)]:
 h,p,n,i,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,35)),Vector((0,0,-1)),distance=80);probes.append(dict(x=x,y=y,object=o.name if h else None,error=p.z-z if h else None));assert h and abs(p.z-z)<.05,probes[-1]
(R/'reports/R525_BUILD.json').write_text(json.dumps(dict(check=check,reopened=True,probes=probes,accepted=False,published=False),indent=2));print('R525_OK',check,probes)
