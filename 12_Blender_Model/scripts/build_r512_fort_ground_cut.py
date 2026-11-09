import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R508_BATI_KULE_EKSEN_ZEMIN_ADAY_v001.blend'));domains=json.loads((R/'reports/R512_FORT_SOIL_CUT_DOMAINS.json').read_text());targets=['R417_FORT_OPEN_END_EARTH_COVER','R420_SOUTH_LOW_COURT_CONTACT','R508_WEST_COURT_CONTACT_0'];records=[]
for d in domains:
 for ring in d['outlines']:
  n=len(ring);vs=[(x,y,z) for z in [-20,20] for x,y in ring];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new('R512_CUT');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new('R512_CUT',me);bpy.context.scene.collection.objects.link(cut)
  for name in targets:
   ob=bpy.data.objects[name];before=len(ob.data.polygons);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R512_REMOVE_UNSUPPORTED_FRONT_SOIL','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);records.append(dict(tower=d['tower'],object=name,beforeFaces=before,afterFaces=len(ob.data.polygons)))
  bpy.data.objects.remove(cut,do_unlink=True)
checks=[]
for name in targets:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));row=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(o.data);bm.free();checks.append(row)
assert not any(q['nonManifold'] or q['zeroArea'] for q in checks),checks
out=R/'scenes/MUDAM_R512_KALE_DIS_TASAN_TOPRAK_KESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R512_BUILD.json').write_text(json.dumps(dict(records=records,checks=checks,reopened=True,accepted=False,published=False),indent=2))
