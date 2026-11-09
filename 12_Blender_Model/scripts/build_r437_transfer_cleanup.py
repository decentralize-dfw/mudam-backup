import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R434_KALE_ON_CEPHE_ACIKLIKLARI_ADAY_v001.blend'));rows=[]
for name in ['R154_FORT_MASONRY_BODY']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);before=sum(e.is_boundary for e in bm.edges);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-4);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];removed=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);
 if name=='R434_SUPERSEDED_WINDOW_MASONRY':bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));rows.append(dict(name=name,boundaryBefore=before,boundaryAfter=sum(e.is_boundary for e in bm.edges),removedZeroAreaTriangles=removed,zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.to_mesh(o.data);bm.free()
f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());poly=json.loads((R/'reports/R437_WINDOW_INFILL_POLYGON.json').read_text());entry=Vector((*f['entry'],0));tangent=Vector((*f['tangent'],0));direction=Vector((*f['direction'],0));n=len(poly);vs=[tuple(entry+tangent*x+direction*dep+Vector((0,0,z))) for dep in [0,2.1] for x,z in poly];faces=[]
for t in tessellate_polygon([[Vector((x,z,0)) for x,z in poly]]):
 ids=[i if isinstance(i,int) else min(range(n),key=lambda j:(Vector((*poly[j],0))-i).length) for i in t];faces.append(tuple(reversed(ids)));faces.append(tuple(i+n for i in ids))
for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
o=bpy.data.objects['R434_SUPERSEDED_WINDOW_MASONRY'];ma=o.data.materials[0];me=bpy.data.meshes.new('R437_ANALYTIC_WINDOW_INFILL');me.from_pydata(vs,[],faces);me.update();me.materials.append(ma);o.data=me;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));rows.append(dict(name=o.name,boundaryAfter=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.dot(tangent)/4,p.z/4)
out=R/'scenes/MUDAM_R437_KALE_ON_CEPHE_AKTARIM_TEMIZLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(R/'reports/R437_TRANSFER_CLEANUP.json').write_text(json.dumps(dict(scene=out.name,checks=rows,accepted=False,published=False),indent=2));print(rows)

