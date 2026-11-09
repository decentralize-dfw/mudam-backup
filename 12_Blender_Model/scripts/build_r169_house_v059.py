from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v053.json').read_text());v=d['vertices'];nx=d['nx'];ny=d['ny'];f=[]
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@p.co for p in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
for j in range(ny-1):
 for i in range(nx-1):
  k=j*nx+i
  if abs(v[k][2]-v[k+nx+1][2])<abs(v[k+1][2]-v[k+nx][2]):f.extend([(k,k+1,k+nx+1),(k,k+nx+1,k+nx)])
  else:f.extend([(k,k+1,k+nx),(k+1,k+nx+1,k+nx)])
edges=[list(range(nx)),[j*nx+nx-1 for j in range(ny)],list(range(ny*nx-1,(ny-1)*nx-1,-1)),[j*nx for j in range(ny-1,-1,-1)]];planes=json.loads((D/'facade_planes_v057.json').read_text());ground={h['index']:h['z'] for h in json.loads((D/'ground_edge_v059.json').read_text())};stats=[]
for side,edge in enumerate(edges):
 normal=Vector((*planes['sides'][side]['normal'],0));rows=[edge];hits=0;fallback=0
 for j in range(1,41):
  row=[]
  for i in edge:
   top=Vector(v[i]);base=ground[i]-.08;z=top.z+(base-top.z)*j/40;p=Vector((top.x,top.y,z));h,n,idx,dist=tree.ray_cast(p+normal*1.2,-normal,2.4)
   if h and abs(n.z)<.7 and abs(n.dot(normal))>.45 and abs(h.z-z)<.01:
    p=h;hits+=1
   else:fallback+=1
   row.append(len(v));v.append(tuple(p))
  rows.append(row)
 for row,nextrow in zip(rows,rows[1:]):
  for i in range(len(edge)-1):a,b=row[i:i+2];c,e=nextrow[i:i+2];f.extend([(a,c,e),(a,e,b)])
 stats.append(dict(side=side,source_hits=hits,fallback_points=fallback))
bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v059.blend'),compress=True);(R/'reports/R169_FACADE_SECTIONS_v059.json').write_text(json.dumps(dict(sides=stats,accepted=False,limits='Ray surface resampling; source-hidden points retain vertical boundary. Facade detail not fully reconstructed.'),indent=2));print(stats)
