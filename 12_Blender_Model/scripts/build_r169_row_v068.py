from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v061.json').read_text());v=d['vertices'];nx=d['nx'];ny=d['ny'];f=[]
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
roof_count=len(f);edges=[list(range(nx)),[j*nx+nx-1 for j in range(ny)],list(range(ny*nx-1,(ny-1)*nx-1,-1)),[j*nx for j in range(ny-1,-1,-1)]];planes=json.loads((D/'facade_planes_v062.json').read_text());ground={h['index']:h['z'] for h in json.loads((D/'ground_edge_v061.json').read_text())};stats=[]
for side,edge in enumerate(edges):
 normal=Vector((*planes['sides'][side]['normal'],0));line=float(np.dot(planes['q'][side],planes['sides'][side]['normal'])+planes['sides'][side]['offset']);positions=[];offsets=np.full((40,len(edge)),np.nan)
 for j in range(1,41):
  points=[]
  for ii,i in enumerate(edge):
   top=Vector(v[i]);z=top.z+(ground[i]-.3-top.z)*j/40;p=Vector((top.x,top.y,z));p+=normal*(line-normal.dot(p));points.append(p);h,n,idx,dist=tree.ray_cast(p+normal*1.0,-normal,2.0)
   if h and abs(n.z)<.6 and abs(n.dot(normal))>.65:offsets[j-1,ii]=1-dist
  positions.append(points)
 valid=np.isfinite(offsets);a=np.nan_to_num(offsets)
 # Harmonic interpolation only for unobserved points, retaining measured offsets.
 for iteration in range(80):
  pad=np.pad(a,1,mode='edge');avg=(pad[:-2,1:-1]+pad[2:,1:-1]+pad[1:-1,:-2]+pad[1:-1,2:])/4;a=np.where(valid,a,avg)
 # Reject isolated depth spikes; keep coherent source-backed recesses and bays.
 pad=np.pad(a,1,mode='edge');filtered=np.median(np.stack([pad[j:j+40,i:i+len(edge)] for j in range(3) for i in range(3)]),axis=0)
 rows=[edge]
 for j,points in enumerate(positions):
  row=[]
  for ii,p in enumerate(points):row.append(len(v));v.append(tuple(p+normal*float(filtered[j,ii])))
  rows.append(row)
 for row,nxt in zip(rows,rows[1:]):
  for i in range(len(edge)-1):a,b=row[i:i+2];c,e=nxt[i:i+2];f.extend([(a,c,e),(a,e,b)])
 stats.append(dict(side=side,measured=int(valid.sum()),interpolated=int((~valid).sum())))
# Join every side-grid corner through its full height; avoid open side seams.
starts=[];offset=nx*ny
for edge in edges:starts.append(offset);offset+=40*len(edge)
for side in range(4):
 nxt=(side+1)%4;pa=edges[side][-1];pb=edges[nxt][0]
 for j in range(40):
  a=starts[side]+j*len(edges[side])+len(edges[side])-1;b=starts[nxt]+j*len(edges[nxt]);face=list(dict.fromkeys([pa,pb,b,a]))
  if len(face)>=3:f.append(face)
  pa,pb=a,b
bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v068.blend'),compress=True);(R/'reports/R169_FACADE_SECTIONS_v068.json').write_text(json.dumps(dict(sides=stats,accepted=False,limits='Interpolated hidden facade samples; 3x3 isolated offset spike rejection; four-side corner joining still requires check.'),indent=2));print(stats)

