from pathlib import Path
import bpy,bmesh,json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v061.json').read_text());v=d['vertices'];nx=d['nx'];ny=d['ny'];f=[]
for j in range(ny-1):
 for i in range(nx-1):
  k=j*nx+i
  if abs(v[k][2]-v[k+nx+1][2])<abs(v[k+1][2]-v[k+nx][2]):f.extend([(k,k+1,k+nx+1),(k,k+nx+1,k+nx)])
  else:f.extend([(k,k+1,k+nx),(k+1,k+nx+1,k+nx)])
edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(ny*nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
# Continuous authored envelope: no old roof skirt, no independent cut-height ledge.
ground={h['index']:h['z'] for h in json.loads((D/'ground_edge_v061.json').read_text())}
for a,b in zip(edge,edge[1:]+edge[:1]):
 off=len(v);v.extend([(v[a][0],v[a][1],ground[a]-.10),(v[b][0],v[b][1],ground[b]-.10)]);f.append((a,off,off+1,b))
bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for p in me.polygons:p.use_smooth=len(p.vertices)==3
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v061.blend'),compress=True)

