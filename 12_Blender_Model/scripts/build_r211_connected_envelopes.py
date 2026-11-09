from pathlib import Path
import bpy,bmesh,json
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R210_KUZEY_ZEMIN_SUREKLILIGI_v001.blend'));audit=json.loads((R/'reports/R211_ENVELOPE_AUDIT.json').read_text());report=[]
for record in audit:
 if not record['boundary']:continue
 o=bpy.data.objects[record['name']];old=o.data;bm=bmesh.new();bm.from_mesh(old);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);bm.verts.ensure_lookup_table();bm.verts.index_update()
 coords=[v.co.copy() for v in bm.verts];boundary={v.index for e in bm.edges if e.is_boundary for v in e.verts};tree=KDTree(len(boundary))
 for i in boundary:tree.insert(coords[i],i)
 tree.balance();edgepoints={};insertions=0
 for e in bm.edges:
  if not e.is_boundary:continue
  ia,ib=[v.index for v in e.verts];a,b=coords[ia],coords[ib];d=b-a;length=d.length
  if length<.002:continue
  found=[]
  for p,i,dist in tree.find_range((a+b)*.5,length*.5+.002):
   if i in [ia,ib]:continue
   t=(p-a).dot(d)/d.length_squared
   if .00001<t<.99999 and (p-(a+d*t)).length<.0005:found.append((t,i))
  if found:edgepoints[(ia,ib)]=[i for t,i in sorted(found)];insertions+=len(found)
 faces=[];materials=[]
 for f in bm.faces:
  ids=[v.index for v in f.verts];ring=[]
  for ia,ib in zip(ids,ids[1:]+ids[:1]):
   ring.append(ia);ring.extend(edgepoints.get((ia,ib),list(reversed(edgepoints.get((ib,ia),[])))))
  faces.append(ring);materials.append(f.material_index)
 bm.free();me=bpy.data.meshes.new(o.name+'_CONNECTED');me.from_pydata(coords,[],faces);me.update()
 for m in old.materials:me.materials.append(m)
 for p,mi in zip(me.polygons,materials):p.material_index=mi
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);after=sum(e.is_boundary for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.to_mesh(me);bm.free();o.data=me
 report.append(dict(name=o.name,before=record['boundary'],after=after,inserted_edge_vertices=insertions,zero_faces=zero,method='Conform existing coplanar T-junction edges; no holes capped and no openings removed'));print(report[-1],flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v001.blend'),compress=True)
(R/'reports/R211_CONNECTED_ENVELOPES.json').write_text(json.dumps(dict(accepted=False,buildings=report,fullScopeAccepted=False),indent=2))
