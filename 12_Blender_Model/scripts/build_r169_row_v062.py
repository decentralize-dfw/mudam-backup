from pathlib import Path
import bpy,bmesh,json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v061.json').read_text());v=d['vertices'];nx=d['nx'];ny=d['ny'];f=[]
for j in range(ny-1):
 for i in range(nx-1):
  k=j*nx+i
  if abs(v[k][2]-v[k+nx+1][2])<abs(v[k+1][2]-v[k+nx][2]):f.extend([(k,k+1,k+nx+1),(k,k+nx+1,k+nx)])
  else:f.extend([(k,k+1,k+nx),(k+1,k+nx+1,k+nx)])
roof_faces=len(f);planes=json.loads((D/'facade_planes_v062.json').read_text());q=np.array(planes['q']);ns=np.array([s['normal'] for s in planes['sides']]);lines=[float(ns[k]@q[k]+planes['sides'][k]['offset']) for k in range(4)];corners=[np.linalg.solve(np.array([ns[(k-1)%4],ns[k]]),[lines[(k-1)%4],lines[k]]) for k in range(4)]
edges=[list(range(nx)),[j*nx+nx-1 for j in range(ny)],list(range(ny*nx-1,(ny-1)*nx-1,-1)),[j*nx for j in range(ny-1,-1,-1)]];ground={h['index']:h['z'] for h in json.loads((D/'ground_edge_v061.json').read_text())}
for side,edge in enumerate(edges):
 upper=[];lower=[]
 for j,i in enumerate(edge):
  p=np.array(v[i][:2]);p+=ns[side]*(lines[side]-ns[side]@p)
  if j==0:p=corners[side]
  if j==len(edge)-1:p=corners[(side+1)%4]
  upper.append(len(v));v.append((*p,v[i][2]-.05));lower.append(len(v));v.append((*p,ground[i]-.30))
 for j in range(len(edge)-1):
  a,b=edge[j:j+2];c,e=upper[j:j+2];f.extend([(a,c,e),(a,e,b)]);g,h=lower[j:j+2];f.extend([(c,g,h),(c,h,e)])
bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=p.index<roof_faces
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v062.blend'),compress=True)
